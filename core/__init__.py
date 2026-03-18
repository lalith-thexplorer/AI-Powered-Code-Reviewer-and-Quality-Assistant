"""Core business-logic package for AI Powered CRQA."""

from . import parser
from .convert_docstring_style import (
    _extract_code,
    convert_style,
    detect_style,
    generate_docstrings,
    get_client as get_docstring_client,
)
from .fix_code_with_ai import (
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    fix_docstrings,
    get_client as get_fix_client,
)
from .generate_workspace_tests import (
    DEFAULT_MODEL as DEFAULT_TEST_MODEL,
    generate_pytest_for_file,
    get_client as get_test_client,
)

__all__ = [
    "parser",
    "AVAILABLE_MODELS",
    "DEFAULT_MODEL",
    "DEFAULT_TEST_MODEL",
    "fix_docstrings",
    "detect_style",
    "convert_style",
    "generate_docstrings",
    "_extract_code",
    "generate_pytest_for_file",
    "get_docstring_client",
    "get_fix_client",
    "get_test_client",
]
