def calculate_bmi(weight_kg, height_m):
    """
    Calculates the Body Mass Index (BMI).

    Args:
        weight_kg (float): The weight of the person in kilograms.

    Returns:
        float: The calculated BMI value.
    """
    return weight_kg / (height_m ** 2)
