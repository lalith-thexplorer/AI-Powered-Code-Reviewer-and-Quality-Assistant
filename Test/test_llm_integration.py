"""Tests for AI integration logic to fix PEP errors."""

import pytest
from fix_code_with_ai import fix_docstrings
from unittest.mock import patch, MagicMock

@patch("fix_code_with_ai.get_client")
def test_fix_docstrings(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    # Mock the API response
    mock_choice = MagicMock()
    mock_choice.message.content = "```python\ndef test():\n    '''fixed'''\n    pass\n```"
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
    
    code = "def test():\n    pass\n"
    errors = [{"name": "test", "docstring_errors": [{"code": "D103", "message": "Missing docstring"}]}]
    
    result, _ = fix_docstrings(code, errors)
    assert "'''fixed'''" in result


def test_fix_docstrings_returns_original_when_no_errors():
    code = "def test():\n    return 1\n"
    result, _ = fix_docstrings(code, functions_with_errors=[])
    assert result == code


@patch("fix_code_with_ai.get_client")
def test_fix_docstrings_strips_think_and_picks_longest_block(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    llm_output = (
        "<think>internal reasoning</think>\n"
        "```python\ndef long(a):\n    '''ok'''\n    return a\n```\n"
        "```python\ndef short_tests():\n    pass\n```"
    )

    mock_choice = MagicMock()
    mock_choice.message.content = llm_output
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

    code = "def long(a):\n    return a\n"
    errors = [{"name": "long", "docstring_errors": [{"code": "D103", "message": "Missing docstring"}]}]
    result, _ = fix_docstrings(code, errors)
    assert "def long(a):" in result
    assert "'''ok'''" in result


@patch("fix_code_with_ai.get_client")
def test_fix_docstrings_falls_back_to_original_on_invalid_python(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    mock_choice = MagicMock()
    mock_choice.message.content = "```python\ndef broken(:\n    pass\n```"
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

    code = "def keep():\n    return True\n"
    errors = [{"name": "keep", "docstring_errors": [{"code": "D103", "message": "Missing docstring"}]}]
    result, _ = fix_docstrings(code, errors)
    assert result == code