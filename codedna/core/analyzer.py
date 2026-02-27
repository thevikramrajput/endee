"""
CodeDNA Analyzer Module
=======================
Performs codebase health diagnostics by comparing code against
known anti-patterns using vector similarity in Endee.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from core.parser import CodeUnit
from core.searcher import CodeSearcher, SearchResult

logger = logging.getLogger(__name__)


@dataclass
class HealthViolation:
    """Represents a single code health violation."""
    code_unit_name: str
    code_unit_file: str
    violation_type: str
    pattern_name: str
    similarity: float
    severity: str  # "low", "medium", "high", "critical"
    description: str
    suggestion: str = ""


@dataclass
class HealthReport:
    """Complete health report for a codebase."""
    overall_score: float  # 0-100
    total_units_analyzed: int
    violations: List[HealthViolation] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    grade: str = "A"  # A, B, C, D, F

    def calculate_grade(self):
        """Calculate letter grade from overall score."""
        if self.overall_score >= 90:
            self.grade = "A"
        elif self.overall_score >= 80:
            self.grade = "B"
        elif self.overall_score >= 70:
            self.grade = "C"
        elif self.overall_score >= 60:
            self.grade = "D"
        else:
            self.grade = "F"
        return self.grade

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display."""
        return {
            "overall_score": round(self.overall_score, 1),
            "grade": self.grade,
            "total_units_analyzed": self.total_units_analyzed,
            "total_violations": len(self.violations),
            "critical_violations": sum(
                1 for v in self.violations if v.severity == "critical"
            ),
            "high_violations": sum(
                1 for v in self.violations if v.severity == "high"
            ),
            "medium_violations": sum(
                1 for v in self.violations if v.severity == "medium"
            ),
            "low_violations": sum(
                1 for v in self.violations if v.severity == "low"
            ),
            "metrics": self.metrics,
        }


class CodeHealthAnalyzer:
    """
    Analyzes codebase health by comparing code patterns against
    known anti-patterns stored in Endee's anti_patterns index.
    """

    def __init__(self, searcher: CodeSearcher):
        """
        Initialize the analyzer.

        Args:
            searcher: CodeSearcher instance for querying anti-patterns.
        """
        self.searcher = searcher

    def analyze_unit(self, unit: CodeUnit) -> List[HealthViolation]:
        """
        Analyze a single code unit for health violations.

        Checks against:
        1. Anti-pattern similarity (via Endee)
        2. Complexity heuristics
        3. Documentation coverage
        4. Code length heuristics
        """
        violations = []

        # 1. Check against anti-pattern database in Endee
        try:
            antipattern_matches = self.searcher.find_antipattern_matches(
                code_snippet=unit.code, top_k=3
            )
            for match in antipattern_matches:
                if match.similarity >= config.ANTIPATTERN_SIMILARITY_THRESHOLD:
                    violations.append(
                        HealthViolation(
                            code_unit_name=unit.name,
                            code_unit_file=unit.file_path,
                            violation_type="anti_pattern",
                            pattern_name=match.metadata.get("name", "Unknown"),
                            similarity=match.similarity,
                            severity=match.metadata.get("severity", "medium"),
                            description=match.metadata.get(
                                "description", "Matches known anti-pattern"
                            ),
                            suggestion=f"Refactor to avoid the '{match.metadata.get('name', '')}' pattern",
                        )
                    )
        except Exception as e:
            logger.debug(f"Anti-pattern check skipped for {unit.name}: {e}")

        # 2. Complexity check
        if unit.complexity > 15:
            severity = "critical" if unit.complexity > 25 else "high"
            violations.append(
                HealthViolation(
                    code_unit_name=unit.name,
                    code_unit_file=unit.file_path,
                    violation_type="high_complexity",
                    pattern_name="Excessive Complexity",
                    similarity=min(unit.complexity / 30.0, 1.0),
                    severity=severity,
                    description=f"Cyclomatic complexity of {unit.complexity} exceeds recommended threshold",
                    suggestion="Break down into smaller functions with single responsibilities",
                )
            )
        elif unit.complexity > 10:
            violations.append(
                HealthViolation(
                    code_unit_name=unit.name,
                    code_unit_file=unit.file_path,
                    violation_type="moderate_complexity",
                    pattern_name="Moderate Complexity",
                    similarity=unit.complexity / 20.0,
                    severity="medium",
                    description=f"Complexity of {unit.complexity} could be improved",
                    suggestion="Consider simplifying conditional logic",
                )
            )

        # 3. Documentation check
        if (
            unit.unit_type in ("function", "class")
            and not unit.docstring
            and unit.loc > 10
        ):
            violations.append(
                HealthViolation(
                    code_unit_name=unit.name,
                    code_unit_file=unit.file_path,
                    violation_type="missing_documentation",
                    pattern_name="Missing Documentation",
                    similarity=0.0,
                    severity="low",
                    description=f"{unit.unit_type.capitalize()} with {unit.loc} lines lacks documentation",
                    suggestion="Add a docstring explaining purpose, parameters, and return value",
                )
            )

        # 4. Long function check
        if unit.unit_type == "function" and unit.loc > 100:
            severity = "high" if unit.loc > 200 else "medium"
            violations.append(
                HealthViolation(
                    code_unit_name=unit.name,
                    code_unit_file=unit.file_path,
                    violation_type="long_function",
                    pattern_name="Long Function",
                    similarity=min(unit.loc / 300.0, 1.0),
                    severity=severity,
                    description=f"Function has {unit.loc} lines, exceeding recommended length",
                    suggestion="Extract helper functions to improve readability",
                )
            )

        # 5. Too many parameters
        if unit.unit_type == "function" and len(unit.parameters) > 5:
            severity = "high" if len(unit.parameters) > 8 else "medium"
            violations.append(
                HealthViolation(
                    code_unit_name=unit.name,
                    code_unit_file=unit.file_path,
                    violation_type="too_many_params",
                    pattern_name="Too Many Parameters",
                    similarity=min(len(unit.parameters) / 10.0, 1.0),
                    severity=severity,
                    description=f"Function has {len(unit.parameters)} parameters",
                    suggestion="Consider using a configuration object or dataclass",
                )
            )

        return violations

    def analyze_codebase(self, units: List[CodeUnit]) -> HealthReport:
        """
        Perform comprehensive health analysis on a codebase.

        Args:
            units: All parsed code units from the repository.

        Returns:
            HealthReport with overall score, violations, and metrics.
        """
        all_violations = []
        total_complexity = 0
        total_loc = 0
        documented_count = 0
        function_count = 0
        class_count = 0
        module_count = 0

        for unit in units:
            # Collect violations
            violations = self.analyze_unit(unit)
            all_violations.extend(violations)

            # Aggregate metrics
            total_complexity += unit.complexity
            total_loc += unit.loc
            if unit.docstring:
                documented_count += 1
            if unit.unit_type == "function":
                function_count += 1
            elif unit.unit_type == "class":
                class_count += 1
            elif unit.unit_type == "module":
                module_count += 1

        # Calculate overall score
        n = len(units) or 1

        # Severity weights
        severity_penalty = {
            "critical": 10,
            "high": 6,
            "medium": 3,
            "low": 1,
        }

        total_penalty = sum(
            severity_penalty.get(v.severity, 1) for v in all_violations
        )
        max_penalty = n * 10  # max possible penalty

        # Score components
        pattern_score = max(0, 100 - (total_penalty / max_penalty) * 100)
        avg_complexity = total_complexity / n
        complexity_score = max(0, 100 - (avg_complexity - 5) * 5)
        doc_ratio = documented_count / n if n > 0 else 0
        doc_score = doc_ratio * 100

        # Weighted overall score
        overall_score = (
            config.HEALTH_SCORE_WEIGHTS["pattern_violations"] * pattern_score
            + config.HEALTH_SCORE_WEIGHTS["complexity"] * complexity_score
            + config.HEALTH_SCORE_WEIGHTS["documentation"] * doc_score
            + config.HEALTH_SCORE_WEIGHTS["code_duplication"] * 80  # Placeholder
        )

        overall_score = max(0, min(100, overall_score))

        report = HealthReport(
            overall_score=overall_score,
            total_units_analyzed=len(units),
            violations=all_violations,
            metrics={
                "total_loc": total_loc,
                "avg_complexity": round(avg_complexity, 2),
                "documentation_ratio": round(doc_ratio * 100, 1),
                "function_count": function_count,
                "class_count": class_count,
                "module_count": module_count,
                "avg_loc_per_unit": round(total_loc / n, 1),
            },
        )
        report.calculate_grade()

        logger.info(
            f"Health Analysis Complete: Score={overall_score:.1f}, "
            f"Grade={report.grade}, Violations={len(all_violations)}"
        )

        return report
