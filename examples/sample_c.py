"""
math_tools.py
A simple module demonstrating clean function definitions and docstrings.
"""

def calculate_bmi(weight_kg, height_m):
    """
    Calculates the Body Mass Index (BMI).

    Args:
        weight_kg (float): The weight of the person in kilograms.
        height_m (float): The height of the person in meters.

    Returns:
        float: The calculated BMI value.
    """
    return weight_kg / (height_m ** 2)

def greet_user(name, excitement_level=1):
    """
    Generates a personalized greeting string.

    Args:
        name (str): The name of the person to greet.
        excitement_level (int): Number of exclamation marks to add. Defaults to 1.

    Returns:
        str: A friendly greeting message.
    """
    punc = "!" * excitement_level
    return f"Hello, {name}{punc}"

def add(a,b):
    return a + b

if __name__ == "__main__":
    # Example usage:
    print(greet_user("Alex", 3))
    
    my_bmi = calculate_bmi(80, 1.8)
    print(f"Calculated BMI: {my_bmi:.2 sexf}")