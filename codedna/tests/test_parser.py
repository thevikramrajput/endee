"""
CodeDNA — Parser Tests
======================
Tests for multi-language code parsing.
"""

import os
import sys
import pytest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.parser import CodeParser, PythonParser, JavaScriptParser, JavaParser, CodeUnit


class TestPythonParser:
    """Tests for Python AST-based parser."""

    def test_parse_function(self):
        code = '''
def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)
'''
        parser = PythonParser()
        units = parser.parse_file("test.py", code)

        functions = [u for u in units if u.unit_type == "function"]
        assert len(functions) >= 1

        fib = functions[0]
        assert fib.name == "calculate_fibonacci"
        assert fib.language == "python"
        assert fib.docstring is not None
        assert "n" in fib.parameters

    def test_parse_class(self):
        code = '''
class UserService:
    """Service for managing users."""

    def __init__(self, db):
        self.db = db

    def get_user(self, user_id):
        """Get user by ID."""
        return self.db.find(user_id)

    def create_user(self, name, email):
        """Create a new user."""
        user = {"name": name, "email": email}
        return self.db.insert(user)
'''
        parser = PythonParser()
        units = parser.parse_file("test.py", code)

        classes = [u for u in units if u.unit_type == "class"]
        assert len(classes) >= 1
        assert classes[0].name == "UserService"

    def test_parse_module(self):
        code = '''"""Test module for user operations."""
import os
from typing import List

def helper():
    """A helper function."""
    pass
'''
        parser = PythonParser()
        units = parser.parse_file("test.py", code)

        modules = [u for u in units if u.unit_type == "module"]
        assert len(modules) == 1
        assert modules[0].docstring is not None

    def test_skip_short_functions(self):
        code = '''
def x():
    pass
'''
        parser = PythonParser()
        units = parser.parse_file("test.py", code)
        functions = [u for u in units if u.unit_type == "function"]
        # Should skip because LOC < MIN_FUNCTION_LOC
        assert len(functions) == 0

    def test_complexity_estimation(self):
        code = '''
def complex_function(data):
    """A complex function with many branches."""
    if data:
        for item in data:
            if item.get("active"):
                while item.get("processing"):
                    if item.get("type") == "a" or item.get("type") == "b":
                        try:
                            process(item)
                        except ValueError:
                            handle_error(item)
    return data
'''
        parser = PythonParser()
        units = parser.parse_file("test.py", code)
        functions = [u for u in units if u.unit_type == "function"]
        assert len(functions) >= 1
        # Should have high complexity
        assert functions[0].complexity > 5


class TestJavaScriptParser:
    """Tests for JavaScript regex-based parser."""

    def test_parse_function(self):
        code = '''
function fetchUserData(userId) {
    const response = fetch(`/api/users/${userId}`);
    const data = response.json();
    return data;
}
'''
        parser = JavaScriptParser()
        units = parser.parse_file("test.js", code)

        functions = [u for u in units if u.unit_type == "function"]
        assert len(functions) >= 1
        assert functions[0].name == "fetchUserData"

    def test_parse_arrow_function(self):
        code = '''
const processData = (items) => {
    return items.filter(item => item.active);
};
'''
        parser = JavaScriptParser()
        units = parser.parse_file("test.js", code)
        functions = [u for u in units if u.unit_type == "function"]
        assert len(functions) >= 1

    def test_parse_class(self):
        code = '''
class UserController {
    constructor(service) {
        this.service = service;
    }

    async getUser(req, res) {
        const user = await this.service.findUser(req.params.id);
        res.json(user);
    }
}
'''
        parser = JavaScriptParser()
        units = parser.parse_file("test.js", code)
        classes = [u for u in units if u.unit_type == "class"]
        assert len(classes) >= 1
        assert classes[0].name == "UserController"


class TestJavaParser:
    """Tests for Java regex-based parser."""

    def test_parse_method(self):
        code = '''
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    public double divide(double a, double b) {
        if (b == 0) {
            throw new ArithmeticException("Division by zero");
        }
        return a / b;
    }
}
'''
        parser = JavaParser()
        units = parser.parse_file("Test.java", code)
        functions = [u for u in units if u.unit_type == "function"]
        assert len(functions) >= 1


class TestCodeParser:
    """Tests for the unified CodeParser."""

    def test_parse_directory(self):
        """Test parsing a directory with multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file
            py_file = os.path.join(tmpdir, "test_module.py")
            with open(py_file, "w") as f:
                f.write(
                    'def greet(name):\n'
                    '    """Greet someone."""\n'
                    '    message = f"Hello, {name}!"\n'
                    '    return message\n'
                )

            parser = CodeParser()
            units = parser.parse_directory(tmpdir)
            assert len(units) > 0

    def test_code_unit_metadata(self):
        """Test CodeUnit metadata generation."""
        unit = CodeUnit(
            id="test123",
            name="test_function",
            code="def test_function(x, y):\n    return x + y\n",
            language="python",
            file_path="test.py",
            unit_type="function",
            start_line=1,
            end_line=3,
            loc=3,
            complexity=1,
            parameters=["x", "y"],
        )

        meta = unit.to_metadata()
        assert meta["name"] == "test_function"
        assert meta["language"] == "python"
        assert meta["param_count"] == 2

        filters = unit.to_filter()
        assert filters["language"] == "python"
        assert filters["unit_type"] == "function"


class TestCodeTokenizer:
    """Tests for the code tokenizer used in sparse vectors."""

    def test_camel_case_splitting(self):
        from core.sparse import CodeTokenizer

        tokens = CodeTokenizer.tokenize("getUserById processOrderData")
        assert "get" in tokens
        assert "user" in tokens

    def test_comment_removal(self):
        from core.sparse import CodeTokenizer

        code = "x = 5  # this is a comment\ny = 10"
        tokens = CodeTokenizer.tokenize(code)
        assert "comment" not in tokens


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
