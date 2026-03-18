"""Tests for dashboard filtering logic."""
import pytest

def filter_functions(functions, search=None, status="All"):
    filtered = []
    for f in functions:
        match_search = search.lower() in f['name'].lower() if search else True
        passed = f.get('has_docstring', False) and len(f.get('docstring_errors', [])) == 0
        
        if status == "Passed" and not passed:
            continue
        if status == "Failed" and passed:
            continue
            
        if match_search:
            filtered.append(f)
    return filtered

def test_filter_functions_search():
    functions = [
        {"name": "test_function", "has_docstring": True, "docstring_errors": []},
        {"name": "other_function", "has_docstring": False, "docstring_errors": []}
    ]
    filtered = filter_functions(functions, search="test")
    assert len(filtered) == 1
    assert filtered[0]["name"] == "test_function"

def test_filter_functions_status():
    functions = [
        {"name": "documented_pass", "has_docstring": True, "docstring_errors": []},
        {"name": "documented_fail", "has_docstring": True, "docstring_errors": [{"code": "D200"}]},
        {"name": "undocumented", "has_docstring": False}
    ]
    passed_funcs = filter_functions(functions, status="Passed")
    failed_funcs = filter_functions(functions, status="Failed")
    
    assert len(passed_funcs) == 1
    assert passed_funcs[0]["name"] == "documented_pass"
    
    assert len(failed_funcs) == 2
    assert failed_funcs[0]["name"] == "documented_fail"
    assert failed_funcs[1]["name"] == "undocumented"

def test_filter_functions_combined():
    functions = [
        {"name": "test_doc", "has_docstring": True, "docstring_errors": []},
        {"name": "test_undoc", "has_docstring": False, "docstring_errors": []},
        {"name": "other_doc", "has_docstring": True, "docstring_errors": []}
    ]
    filtered = filter_functions(functions, search="test", status="Passed")
    assert len(filtered) == 1
    assert filtered[0]["name"] == "test_doc"


def test_filter_functions_case_insensitive_search():
    functions = [
        {"name": "Parse_File", "has_docstring": True, "docstring_errors": []},
        {"name": "another", "has_docstring": True, "docstring_errors": []},
    ]
    filtered = filter_functions(functions, search="parse")
    assert len(filtered) == 1
    assert filtered[0]["name"] == "Parse_File"


def test_filter_functions_handles_missing_docstring_errors_key():
    functions = [
        {"name": "documented", "has_docstring": True},
        {"name": "broken", "has_docstring": True, "docstring_errors": [{"code": "DAR101"}]},
    ]
    passed = filter_functions(functions, status="Passed")
    failed = filter_functions(functions, status="Failed")
    assert [f["name"] for f in passed] == ["documented"]
    assert [f["name"] for f in failed] == ["broken"]


@pytest.mark.parametrize("status", ["All", "Unknown", None])
def test_filter_functions_non_strict_status_returns_all_matching_search(status):
    functions = [
        {"name": "alpha", "has_docstring": True, "docstring_errors": []},
        {"name": "beta", "has_docstring": False, "docstring_errors": []},
    ]
    filtered = filter_functions(functions, search="a", status=status)
    assert len(filtered) == 2


def test_filter_functions_empty_input():
    assert filter_functions([], search="anything", status="Passed") == []