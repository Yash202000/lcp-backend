import os

def create_directory(directory_path):
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)  # Create nested directories if needed
    except OSError as e:
        raise OSError(f"Error creating directory '{directory_path}': {e}") from e
