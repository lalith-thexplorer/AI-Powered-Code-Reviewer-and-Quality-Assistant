import math


def calculate_area(radius):
    """
    Calculates the area of a circle.

    Uses the formula A = pi * r^2 to compute the area.

    Args:
        radius (float): The radius of the circle.

    Returns:
        float: The computed area.
    """
    return math.pi * radius ** 2


def calculate_circumference(radius):
    """
    Calculates the circumference of a circle.

    Formula used: C = 2 * pi * r.

    Args:
        radius (float): The radius of the circle.

    Returns:
        float: The computed circumference.
    """
    return 2 * math.pi * radius


def is_valid_radius(value):
    """
    Checks whether the given value is a valid radius.

    A valid radius must be a positive number greater than zero.

    Args:
        value (float): The value to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return isinstance(value, (int, float)) and value > 0
