"""Tests for pydocstyle and darglint validation integration."""

import pytest

from parser import get_ast_errors
from parser import parse_file

def test_pydocstyle_errors():
    code = '''def calculate():\n    """Docstring."""\n    pass'''
    
    # parse_file will internally run the linters and catch what it can.
    # We mainly test that the results structure contains what we expect.
    res = parse_file(code)
    
    assert "total_docstring_errors" in res
    
def test_darglint_errors():
    code = '''
def calculate(a, b):
    """
    Do math.
    
    Args:
        a: param
    """
    pass
    '''
    
    res = parse_file(code)
    # The integration should pass without crashing
    assert "total_functions" in res


def test_get_ast_errors_rest_style_param_marker():
    code = '''
def do_work(a, b):
    """Perform work.

    :returns: output
    """
    return a + b
    '''
    functions = [
        {
            "name": "do_work",
            "start_line": 2,
            "has_docstring": True,
            "docstring": "Perform work.\n\n:returns: output",
            "docstring_errors": [],
        }
    ]

    get_ast_errors(code, functions, style="reST")
    errors = functions[0]["docstring_errors"]
    assert any(e["code"] == "DAR101" and ":param" in e["message"] for e in errors)


def test_get_ast_errors_numpy_style_returns_marker():
    code = '''
def compute(a):
    """Compute output.

    Parameters
    ----------
    a : int
        input
    """
    return a * 2
    '''
    functions = [
        {
            "name": "compute",
            "start_line": 2,
            "has_docstring": True,
            "docstring": "Compute output.\n\nParameters\n----------\na : int\n    input",
            "docstring_errors": [],
        }
    ]

    get_ast_errors(code, functions, style="NumPy")
    errors = functions[0]["docstring_errors"]
    assert any(e["code"] == "DAR201" and "Returns" in e["message"] for e in errors)


def test_get_ast_errors_detects_missing_raises_section():
    code = '''
def risky(flag):
    """Run risky operation.

    Args:
        flag: toggle
    """
    if flag:
        raise ValueError("bad flag")
    return True
    '''
    functions = [
        {
            "name": "risky",
            "start_line": 2,
            "has_docstring": True,
            "docstring": "Run risky operation.\n\nArgs:\n    flag: toggle",
            "docstring_errors": [],
        }
    ]

    get_ast_errors(code, functions, style="Google")
    errors = functions[0]["docstring_errors"]
    codes = {e["code"] for e in errors}
    assert "DAR401" in codes