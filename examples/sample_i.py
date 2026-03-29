"""File system utility helpers for reading and writing local data."""

import os


def read_file(filepath):
    """Read and return the full contents of a file

    Opens the file at the given path in read mode
    and returns the entire text contents as a string.

    Args:
        filepath (str): Absolute or relative path to the file.

    Returns:
        str: The file contents.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    with open(filepath, "r") as f:
        return f.read()


def write_file(filepath, content):
    """Write content to a file at the specified path

    Creates the file if it does not exist, or overwrites
    it if it already exists.

    Args:
        filepath (str): Path where the file should be written.
        content (str): Text content to write into the file.
    """
    with open(filepath, "w") as f:
        f.write(content)


def file_exists(filepath):
    """Check whether a file exists at the provided path

    Args:
        filepath (str): The path to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.isfile(filepath)


def delete_file(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)


def get_file_size(filepath):
    """Retrieve the size of the file in bytes

    Args:
        filepath (str): Path to the target file.

    Returns:
        int: File size in bytes.

    Raises:
        FileNotFoundError: If no file exists at the given path.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"No file found at: {filepath}")
    return os.path.getsize(filepath)
