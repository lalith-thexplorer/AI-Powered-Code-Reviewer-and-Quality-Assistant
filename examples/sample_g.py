"""File containing math helper utilities for basic arithmetic."""


def add(a, b):
    '''
    Add two numbers.
    '''
    return a + b


def subtract(a, b):
    '''
    Subtract b from a.
    '''
    return a - b


def multiply(a, b):
    '''
    Multiply two numbers together.
    '''
    return a * b


def divide(a, b):
    '''
    Divide a by b and return the quotient.

    Args:
        a (float): Numerator.
        b (float): Denominator, must not be zero.

    Returns:
        float: The result of division.

    Raises:
        ValueError: If b is zero.
    '''
    if b == 0:
        raise ValueError("Denominator cannot be zero.")
    return a / b


def power(base, exp):
    '''
    Raise base to the power of exp.

    Args:
        base (float): The base value.
        exp (float): The exponent.

    Returns:
        float: The computed power.
    '''
    return base ** exp
