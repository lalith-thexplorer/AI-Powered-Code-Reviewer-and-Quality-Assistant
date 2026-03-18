"""Tests for function parsing module."""

import pytest

import parser as parser_module
from parser import parse_file

def test_parse_valid_python():
    code = '''
def add(a, b):
    """Add two numbers."""
    return a + b
    '''
    result = parse_file(code)
    
    assert "total_functions" in result
    assert result["total_functions"] == 1
    assert len(result["functions"]) == 1
    
    func = result["functions"][0]
    assert func["name"] == "add"
    assert func["has_docstring"] is True

def test_parse_missing_docstring():
    code = '''
def subtract(a, b):
    return a - b
    '''
    result = parse_file(code)
    assert result["functions"][0]["has_docstring"] is False
    assert result["total_functions"] == 1


def test_parse_syntax_error_returns_error_dict():
    code = "def broken(:\n    pass"
    result = parse_file(code)
    assert "error" in result


def test_parse_coverage_with_multiple_functions(monkeypatch):
    code = '''
def a():
    """Doc."""
    return 1

def b(x):
    return x
    '''
    monkeypatch.setattr(parser_module, "get_pydocstyle_errors", lambda *args, **kwargs: [])
    monkeypatch.setattr(parser_module, "get_darglint_errors", lambda *args, **kwargs: [])

    result = parse_file(code)
    assert result["total_functions"] == 2
    assert result["coverage"] == 50.0


def test_cosmetic_codes_are_filtered(monkeypatch):
    code = '''
def sample(a):
    """Docstring."""
    return a
    '''

    def fake_pydoc(*args, **kwargs):
        return [
            {"code": "D201", "func_name": "sample", "message": "cosmetic"},
            {"code": "D103", "func_name": "sample", "message": "Missing docstring"},
        ]

    monkeypatch.setattr(parser_module, "get_pydocstyle_errors", fake_pydoc)
    monkeypatch.setattr(parser_module, "get_darglint_errors", lambda *args, **kwargs: [])

    result = parse_file(code)
    errors = result["functions"][0]["docstring_errors"]
    codes = {e["code"] for e in errors}
    assert "D201" not in codes
    assert "D103" in codes


def test_ast_safety_net_adds_missing_returns_error(monkeypatch):
    code = '''
def add(a, b):
    """Add values.

    Args:
        a: first
        b: second
    """
    return a + b
    '''

    monkeypatch.setattr(parser_module, "get_pydocstyle_errors", lambda *args, **kwargs: [])
    monkeypatch.setattr(parser_module, "get_darglint_errors", lambda *args, **kwargs: [])

    result = parse_file(code)
    errors = result["functions"][0]["docstring_errors"]
    codes = {e["code"] for e in errors}
    assert "DAR201" in codes