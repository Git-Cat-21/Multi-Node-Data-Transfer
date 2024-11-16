import os
from threading import Lock

# Lock for concurrency control
lock = Lock()

def delete_file(directory, file_name):
    """
    Deletes a file in the specified directory.
    Args:
    - directory (str): The path to the directory containing the file.
    - file_name (str): The name of the file to be deleted.

    Returns:
    - str: A message indicating the result of the operation.
    """
    with lock:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return f"File '{file_name}' deleted successfully."
        else:
            return "File not found."
