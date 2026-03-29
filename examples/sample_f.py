"""Utility functions for string processing operations."""


def reverses_string(text):
    """Reverses the given string and returns result.
    This function takes a string input and produces
    the reversed version of it.

    Args:
        text (str): The string to reverse.

    Returns:
        str: The reversed string.
    """
    return text[::-1]


def counts_vowels(text):
    """Counts the number of vowels present in the string.
    Iterates through each character and checks
    whether it belongs to the set of vowels.

    Args:
        text (str): The input string.

    Returns:
        int: Total count of vowels found.
    """
    return sum(1 for ch in text.lower() if ch in "aeiou")


def normalizes_whitespace(text):
    """Normalizes extra whitespace from the given string.
    Strips leading, trailing, and consecutive internal
    spaces to produce a clean single-spaced string.

    Args:
        text (str): Raw input string.

    Returns:
        str: Cleaned string with normalized spaces.
    """
    return " ".join(text.split())


def checks_palindrome(text):
    """Checks whether the provided string is a palindrome.
    Comparison is case-insensitive and ignores spaces.

    Args:
        text (str): The string to check.

    Returns:
        bool: True if palindrome, False otherwise.
    """
    cleaned = text.replace(" ", "").lower()
    return cleaned == cleaned[::-1]
