import os
import logging

def allowed_file(filename, allowed_extensions):
    """
    Check if the filename has an allowed extension and is safe.
    """
    if not filename or '..' in filename:
        return False
    
    return ('.' in filename and 
            filename.rsplit('.', 1)[1].lower() in allowed_extensions and
            len(filename) < 255)  # Prevent extremely long filenames

def ensure_folder(folder_path):
    """
    Ensure a folder exists, create if it does not.
    Prevents directory traversal attacks.
    """
    # Normalize and validate the path
    folder_path = os.path.normpath(folder_path)
    
    # Prevent going outside the project directory
    if '..' in folder_path or folder_path.startswith('/'):
        raise ValueError("Invalid folder path")
    
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path, mode=0o755)  # Restrict permissions
        except OSError as e:
            logging.error(f"Failed to create directory {folder_path}: {e}")
            raise
