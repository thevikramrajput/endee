"""
CodeDNA Parser Module
=====================
Multi-language AST parser that extracts code structures (functions, classes, modules)
from source files using tree-sitter for language-agnostic parsing, with fallback
regex-based parsing for broader compatibility.
"""

import os
import re
import ast
import hashlib
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

logger = logging.getLogger(__name__)


@dataclass
class CodeUnit:
    """Represents a single extractable code unit (function, class, or module)."""

    id: str  # Unique identifier (hash of content + path)
    name: str  # Function/class/module name
    code: str  # Raw source code
    language: str  # Programming language
    file_path: str  # Relative file path
    unit_type: str  # "function", "class", "module"
    start_line: int  # Starting line number
    end_line: int  # Ending line number
    loc: int  # Lines of code
    docstring: Optional[str] = None
    complexity: int = 1  # Cyclomatic complexity estimate
    parent_class: Optional[str] = None  # Parent class name if method
    imports: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)

    def to_metadata(self) -> Dict[str, Any]:
        """Convert to metadata dict for Endee storage."""
        return {
            "name": self.name,
            "language": self.language,
            "file_path": self.file_path,
            "unit_type": self.unit_type,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "loc": self.loc,
            "complexity": self.complexity,
            "has_docstring": self.docstring is not None,
            "parent_class": self.parent_class or "",
            "param_count": len(self.parameters),
        }

    def to_filter(self) -> Dict[str, Any]:
        """Convert to filter dict for Endee storage."""
        return {
            "language": self.language,
            "unit_type": self.unit_type,
            "complexity": self.complexity,
            "loc": self.loc,
        }


def _generate_id(file_path: str, name: str, start_line: int) -> str:
    """Generate a deterministic unique ID for a code unit."""
    raw = f"{file_path}:{name}:{start_line}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _estimate_complexity(code: str, language: str) -> int:
    """
    Estimate cyclomatic complexity from source code.
    Counts decision points (if, for, while, and, or, except, case).
    """
    complexity = 1  # Base complexity
    decision_keywords = [
        r"\bif\b",
        r"\belif\b",
        r"\belse\b",
        r"\bfor\b",
        r"\bwhile\b",
        r"\band\b",
        r"\bor\b",
        r"\bexcept\b",
        r"\bcase\b",
        r"\bcatch\b",
        r"\bswitch\b",
        r"\b\?\b",  # Ternary operator
    ]
    for pattern in decision_keywords:
        complexity += len(re.findall(pattern, code))
    return complexity


# ─────────────────────────────────────────────────────────────────────
# Python Parser (using built-in ast module — most reliable)
# ─────────────────────────────────────────────────────────────────────


class PythonParser:
    """Parse Python files using the built-in ast module."""

    def parse_file(self, file_path: str, source: str) -> List[CodeUnit]:
        """Extract functions and classes from a Python file."""
        units = []
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return units

        lines = source.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(
                node, ast.AsyncFunctionDef
            ):
                unit = self._extract_function(node, file_path, lines)
                if unit:
                    units.append(unit)

            elif isinstance(node, ast.ClassDef):
                unit = self._extract_class(node, file_path, lines)
                if unit:
                    units.append(unit)

        # Also extract module-level summary
        module_unit = self._extract_module(file_path, source, lines)
        if module_unit:
            units.append(module_unit)

        return units

    def _extract_function(
        self, node: ast.FunctionDef, file_path: str, lines: List[str]
    ) -> Optional[CodeUnit]:
        """Extract a function definition."""
        start = node.lineno - 1
        end = node.end_lineno if node.end_lineno else start + 1
        code = "\n".join(lines[start:end])
        loc = end - start

        if loc < config.MIN_FUNCTION_LOC or loc > config.MAX_FUNCTION_LOC:
            return None

        # Get docstring
        docstring = ast.get_docstring(node)

        # Get parameters
        params = []
        for arg in node.args.args:
            params.append(arg.arg)

        # Get decorators
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(f"{ast.dump(dec)}")

        # Get return type annotation
        return_type = None
        if node.returns:
            try:
                return_type = ast.dump(node.returns)
            except Exception:
                pass

        # Determine parent class
        parent_class = None
        # We'll set this during tree walk if needed

        return CodeUnit(
            id=_generate_id(file_path, node.name, node.lineno),
            name=node.name,
            code=code,
            language="python",
            file_path=file_path,
            unit_type="function",
            start_line=node.lineno,
            end_line=end,
            loc=loc,
            docstring=docstring,
            complexity=_estimate_complexity(code, "python"),
            parent_class=parent_class,
            parameters=params,
            return_type=return_type,
            decorators=decorators,
        )

    def _extract_class(
        self, node: ast.ClassDef, file_path: str, lines: List[str]
    ) -> Optional[CodeUnit]:
        """Extract a class definition."""
        start = node.lineno - 1
        end = node.end_lineno if node.end_lineno else start + 1
        code = "\n".join(lines[start:end])
        loc = end - start

        if loc < config.MIN_FUNCTION_LOC:
            return None

        docstring = ast.get_docstring(node)

        # Extract method names for the class summary
        methods = [
            n.name
            for n in ast.walk(node)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        return CodeUnit(
            id=_generate_id(file_path, node.name, node.lineno),
            name=node.name,
            code=code,
            language="python",
            file_path=file_path,
            unit_type="class",
            start_line=node.lineno,
            end_line=end,
            loc=loc,
            docstring=docstring,
            complexity=_estimate_complexity(code, "python"),
            parameters=methods,  # Store method names as "parameters"
        )

    def _extract_module(
        self, file_path: str, source: str, lines: List[str]
    ) -> Optional[CodeUnit]:
        """Extract module-level summary."""
        loc = len(lines)
        if loc < 5:
            return None

        # Get module docstring
        try:
            tree = ast.parse(source)
            docstring = ast.get_docstring(tree)
        except Exception:
            docstring = None

        # Get imports
        imports = []
        for line in lines[:50]:  # Check first 50 lines for imports
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line)

        module_name = Path(file_path).stem

        return CodeUnit(
            id=_generate_id(file_path, module_name, 1),
            name=module_name,
            code=source[:2000],  # First 2000 chars as module summary
            language="python",
            file_path=file_path,
            unit_type="module",
            start_line=1,
            end_line=loc,
            loc=loc,
            docstring=docstring,
            complexity=_estimate_complexity(source, "python"),
            imports=imports,
        )


# ─────────────────────────────────────────────────────────────────────
# JavaScript/TypeScript Parser (regex-based)
# ─────────────────────────────────────────────────────────────────────


class JavaScriptParser:
    """Parse JavaScript/TypeScript files using regex patterns."""

    # Patterns for function extraction
    FUNCTION_PATTERNS = [
        # Regular functions
        r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*\{",
        # Arrow functions assigned to variables
        r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>\s*\{",
        # Class methods
        r"(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*\{",
    ]

    CLASS_PATTERN = r"(?:export\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{"

    def parse_file(self, file_path: str, source: str) -> List[CodeUnit]:
        """Extract functions and classes from a JS/TS file."""
        units = []
        lines = source.split("\n")
        language = "javascript"

        # Extract functions
        for pattern in self.FUNCTION_PATTERNS:
            for match in re.finditer(pattern, source):
                name = match.group(1)
                params_str = match.group(2) if match.lastindex >= 2 else ""
                start_pos = match.start()
                start_line = source[:start_pos].count("\n") + 1

                # Find matching closing brace
                end_line = self._find_closing_brace(lines, start_line - 1)
                code = "\n".join(lines[start_line - 1 : end_line])
                loc = end_line - start_line + 1

                if loc < config.MIN_FUNCTION_LOC or loc > config.MAX_FUNCTION_LOC:
                    continue

                params = [
                    p.strip().split(":")[0].strip()
                    for p in params_str.split(",")
                    if p.strip()
                ]

                units.append(
                    CodeUnit(
                        id=_generate_id(file_path, name, start_line),
                        name=name,
                        code=code,
                        language=language,
                        file_path=file_path,
                        unit_type="function",
                        start_line=start_line,
                        end_line=end_line,
                        loc=loc,
                        complexity=_estimate_complexity(code, language),
                        parameters=params,
                    )
                )

        # Extract classes
        for match in re.finditer(self.CLASS_PATTERN, source):
            name = match.group(1)
            start_pos = match.start()
            start_line = source[:start_pos].count("\n") + 1
            end_line = self._find_closing_brace(lines, start_line - 1)
            code = "\n".join(lines[start_line - 1 : end_line])
            loc = end_line - start_line + 1

            if loc >= config.MIN_FUNCTION_LOC:
                units.append(
                    CodeUnit(
                        id=_generate_id(file_path, name, start_line),
                        name=name,
                        code=code,
                        language=language,
                        file_path=file_path,
                        unit_type="class",
                        start_line=start_line,
                        end_line=end_line,
                        loc=loc,
                        complexity=_estimate_complexity(code, language),
                    )
                )

        # Module-level
        module_unit = self._extract_module(file_path, source, lines, language)
        if module_unit:
            units.append(module_unit)

        return units

    def _find_closing_brace(self, lines: List[str], start_idx: int) -> int:
        """Find the line number of the matching closing brace."""
        depth = 0
        for i in range(start_idx, min(start_idx + config.MAX_FUNCTION_LOC, len(lines))):
            depth += lines[i].count("{") - lines[i].count("}")
            if depth <= 0 and i > start_idx:
                return i + 1
        return min(start_idx + 20, len(lines))

    def _extract_module(
        self, file_path: str, source: str, lines: List[str], language: str
    ) -> Optional[CodeUnit]:
        """Extract module-level summary."""
        loc = len(lines)
        if loc < 5:
            return None

        imports = [
            l.strip()
            for l in lines[:50]
            if l.strip().startswith("import ") or l.strip().startswith("require(")
        ]

        module_name = Path(file_path).stem
        return CodeUnit(
            id=_generate_id(file_path, module_name, 1),
            name=module_name,
            code=source[:2000],
            language=language,
            file_path=file_path,
            unit_type="module",
            start_line=1,
            end_line=loc,
            loc=loc,
            complexity=_estimate_complexity(source, language),
            imports=imports,
        )


# ─────────────────────────────────────────────────────────────────────
# Java Parser (regex-based)
# ─────────────────────────────────────────────────────────────────────


class JavaParser:
    """Parse Java files using regex patterns."""

    METHOD_PATTERN = r"(?:public|private|protected|static|\s)*\s+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[\w,\s]+)?\s*\{"
    CLASS_PATTERN = (
        r"(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)"
    )

    def parse_file(self, file_path: str, source: str) -> List[CodeUnit]:
        """Extract methods and classes from a Java file."""
        units = []
        lines = source.split("\n")
        language = "java"

        # Extract methods
        for match in re.finditer(self.METHOD_PATTERN, source):
            name = match.group(1)
            params_str = match.group(2)
            start_pos = match.start()
            start_line = source[:start_pos].count("\n") + 1
            end_line = self._find_closing_brace(lines, start_line - 1)
            code = "\n".join(lines[start_line - 1 : end_line])
            loc = end_line - start_line + 1

            if loc < config.MIN_FUNCTION_LOC or loc > config.MAX_FUNCTION_LOC:
                continue

            params = [
                p.strip().split()[-1] for p in params_str.split(",") if p.strip()
            ]

            units.append(
                CodeUnit(
                    id=_generate_id(file_path, name, start_line),
                    name=name,
                    code=code,
                    language=language,
                    file_path=file_path,
                    unit_type="function",
                    start_line=start_line,
                    end_line=end_line,
                    loc=loc,
                    complexity=_estimate_complexity(code, language),
                    parameters=params,
                )
            )

        # Extract classes
        for match in re.finditer(self.CLASS_PATTERN, source):
            name = match.group(1)
            start_pos = match.start()
            start_line = source[:start_pos].count("\n") + 1
            end_line = self._find_closing_brace(lines, start_line - 1)
            code = "\n".join(lines[start_line - 1 : end_line])
            loc = end_line - start_line + 1

            if loc >= config.MIN_FUNCTION_LOC:
                units.append(
                    CodeUnit(
                        id=_generate_id(file_path, name, start_line),
                        name=name,
                        code=code,
                        language=language,
                        file_path=file_path,
                        unit_type="class",
                        start_line=start_line,
                        end_line=end_line,
                        loc=loc,
                        complexity=_estimate_complexity(code, language),
                    )
                )

        return units

    def _find_closing_brace(self, lines: List[str], start_idx: int) -> int:
        """Find the line number of the matching closing brace."""
        depth = 0
        for i in range(start_idx, min(start_idx + config.MAX_FUNCTION_LOC, len(lines))):
            depth += lines[i].count("{") - lines[i].count("}")
            if depth <= 0 and i > start_idx:
                return i + 1
        return min(start_idx + 20, len(lines))


# ─────────────────────────────────────────────────────────────────────
# Unified Parser Interface
# ─────────────────────────────────────────────────────────────────────


class CodeParser:
    """
    Unified multi-language code parser.
    Routes files to the appropriate language-specific parser.
    """

    def __init__(self):
        self.parsers = {
            "python": PythonParser(),
            "javascript": JavaScriptParser(),
            "java": JavaParser(),
        }

    def parse_file(self, file_path: str) -> List[CodeUnit]:
        """Parse a source file and extract code units."""
        ext = Path(file_path).suffix.lower()
        language = config.SUPPORTED_LANGUAGES.get(ext)

        if not language:
            logger.debug(f"Unsupported file extension: {ext}")
            return []

        parser = self.parsers.get(language)
        if not parser:
            logger.warning(f"No parser available for language: {language}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return []

        if not source.strip():
            return []

        try:
            units = parser.parse_file(file_path, source)
            logger.info(f"Parsed {len(units)} code units from {file_path}")
            return units
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return []

    def parse_directory(
        self, directory: str, recursive: bool = True
    ) -> List[CodeUnit]:
        """Parse all supported files in a directory."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        all_units = []
        dir_path = Path(directory)

        if not dir_path.exists():
            logger.error(f"Directory not found: {directory}")
            return []

        # Directories to skip
        skip_dirs = {
            ".git", "__pycache__", "node_modules", ".venv", "venv",
            "env", ".env", "dist", "build", ".tox", ".mypy_cache",
            ".pytest_cache", "egg-info", ".eggs",
        }

        pattern = "**/*" if recursive else "*"
        valid_files = [
            str(p) for p in dir_path.glob(pattern)
            if p.is_file() 
            and not any(part in skip_dirs for part in p.parts)
            and p.suffix.lower() in config.SUPPORTED_LANGUAGES
        ]
        
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            future_to_file = {executor.submit(self.parse_file, f): f for f in valid_files}
            for future in as_completed(future_to_file):
                try:
                    units = future.result()
                    all_units.extend(units)
                except Exception as e:
                    logger.error(f"File parsing exception in threads: {e}")

        logger.info(
            f"Total: Parsed {len(all_units)} code units from {directory} using {len(valid_files)} files"
        )
        return all_units

    def parse_code_string(
        self, code: str, language: str, file_path: str = "<string>"
    ) -> List[CodeUnit]:
        """Parse a code string directly."""
        parser = self.parsers.get(language)
        if not parser:
            return []
        try:
            return parser.parse_file(file_path, code)
        except Exception as e:
            logger.error(f"Failed to parse code string: {e}")
            return []
