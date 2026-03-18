"""Tests for coverage math logic used in Dashboard."""

import math

import pytest


def compute_coverage(total_funcs, total_doc_funcs):
    """Replica of dashboard coverage math for static unit testing."""
    if total_funcs == 0:
        return 100.0
    return (total_doc_funcs / total_funcs) * 100


@pytest.mark.parametrize(
    "total_funcs,total_doc_funcs,expected",
    [
        (10, 10, 100.0),
        (10, 8, 80.0),
        (10, 0, 0.0),
        (0, 0, 100.0),
        (3, 2, 66.6666666667),
    ],
)
def test_coverage_math_values(total_funcs, total_doc_funcs, expected):
    result = compute_coverage(total_funcs, total_doc_funcs)
    assert math.isclose(result, expected, rel_tol=1e-9)


def test_coverage_monotonicity():
    lower = compute_coverage(20, 5)
    higher = compute_coverage(20, 10)
    assert higher > lower


def test_coverage_bounds_for_valid_inputs():
    # Valid inputs should produce bounded percentages.
    for total in [1, 3, 10, 100]:
        for documented in range(total + 1):
            pct = compute_coverage(total, documented)
            assert 0.0 <= pct <= 100.0