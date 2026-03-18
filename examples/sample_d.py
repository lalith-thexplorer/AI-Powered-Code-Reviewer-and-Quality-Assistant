"""Process and validate geometric measurements.

This module provides tools for calculating properties
of shapes, focusing on polygons and circles.
"""

import math


class Circle:
    """Represent a circle with a defined radius.

    Attributes:
        radius: A float representing the distance from the center.
    """

    def __init__(self, radius):
        """Initialize the circle with a radius.

        Args:
            radius: A float representing the circle's radius.
        """
        self.radius = radius

    def calculate_area(self):
        """Return the area of the circle.

        Returns:
            float: The calculated area.
        """
        return math.pi * (self.radius ** 2)


def get_distance(point_a, point_b):
    """Calculate the Euclidean distance between two 2D points.

    Args:
        point_a: Tuple of (x, y) coordinates.
        point_b: Tuple of (x, y) coordinates.

    Returns:
        float: Distance between the points.

    Raises:
        TypeError: If inputs are invalid.
    """
    return math.sqrt(
        (point_b[0] - point_a[0]) ** 2
        + (point_b[1] - point_a[1]) ** 2
    )


def is_valid_radius(value):
    """Check if the provided value is a valid radius.

    Args:
        value: Numeric value to validate.

    Returns:
        bool: True if positive number, False otherwise.
    """
    return isinstance(value, (int, float)) and value > 0