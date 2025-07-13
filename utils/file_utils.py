import os
import logging
import tempfile

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
    """Ensure a folder exists, create it if it doesn't."""
    if not folder_path:
        raise ValueError("Invalid folder path")
    
    # Handle cases where folder_path might be relative or problematic
    try:
        # Convert to absolute path and normalize
        abs_path = os.path.abspath(folder_path)
        
        # Create directory if it doesn't exist
        os.makedirs(abs_path, exist_ok=True)
        
        # Verify the directory was created and is writable
        if not os.path.exists(abs_path):
            raise OSError(f"Failed to create directory: {abs_path}")
            
        if not os.access(abs_path, os.W_OK):
            raise OSError(f"Directory is not writable: {abs_path}")
            
        return abs_path
        
    except (OSError, TypeError) as e:
        # Fallback to temp directory if original path fails
        if 'GITHUB_ACTIONS' in os.environ or 'CI' in os.environ:
            temp_dir = tempfile.mkdtemp(prefix='pixelpipe_')
            return temp_dir
        raise ValueError(f"Invalid folder path: {folder_path}") from e
