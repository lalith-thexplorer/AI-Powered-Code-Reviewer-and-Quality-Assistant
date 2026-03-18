"""Tests for string manipulation in docstring generation."""

import pytest

from convert_docstring_style import _extract_code
from convert_docstring_style import convert_style
from convert_docstring_style import detect_style
from convert_docstring_style import generate_docstrings
from unittest.mock import patch, MagicMock

@patch("convert_docstring_style.get_client")
def test_generator_mock(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    # Mock the API response
    mock_choice = MagicMock()
    mock_choice.message.content = "```python\ndef test():\n    '''NumPy style'''\n    pass\n```"
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
    
    code = "def test():\n    pass\n"
    
    # Call the actual generation code
    result, _ = convert_style(code, "NumPy")
    assert "'''NumPy style'''" in result


def test_detect_style_google():
    code = '''
def add(a, b):
    """Add values.

    Args:
        a: first
        b: second

    Returns:
        int: result
    """
    return a + b
    '''
    assert detect_style(code) == "Google"


def test_detect_style_none_incomplete_when_missing_docstrings():
    code = '''
def with_doc(x):
    """Has docs."""
    return x

def no_doc(y):
    return y
    '''
    assert detect_style(code) == "None/Incomplete"


def test_extract_code_strips_think_and_uses_code_block():
    raw = """<think>hidden</think>\n```python\ndef f():\n    return 1\n```"""
    result = _extract_code(raw, "def fallback():\n    pass")
    assert "def f()" in result


def test_extract_code_falls_back_on_syntax_error():
    fallback = "def fallback():\n    return 42"
    raw = "```python\ndef broken(:\n    pass\n```"
    result = _extract_code(raw, fallback)
    assert result == fallback


@patch("convert_docstring_style.get_client")
def test_generate_docstrings_uses_fallback_on_invalid_llm_output(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_choice = MagicMock()
    mock_choice.message.content = "```python\ndef broken(:\n    pass\n```"
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

    original = "def test(x):\n    return x"
    result, _ = generate_docstrings(original, "Google")
    assert result == original