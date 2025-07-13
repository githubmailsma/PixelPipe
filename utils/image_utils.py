"""
Image utility functions for PixelPipe.

This module provides functionality for downloading and processing images
from URLs and handling file operations safely.
"""

import os
import time
import requests
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from .file_utils import allowed_file

def download_and_save_image(url, upload_folder, allowed_extensions):
    """
    Download an image from a URL and save it to the upload folder.
    
    Args:
        url (str): URL of the image to download
        upload_folder (str): Directory to save the image
        allowed_extensions (set): Set of allowed file extensions
        
    Returns:
        tuple: (filename, file_url) - the saved filename and its URL path
        
    Raises:
        ValueError: If file extension is not allowed
        requests.exceptions.RequestException: If download fails
    """
    # Parse URL to get filename
    parsed_url = urlparse(url)
    original_filename = os.path.basename(parsed_url.path)
    
    # Determine file extension
    if '.' in original_filename:
        extension = original_filename.rsplit('.', 1)[1].lower()
    else:
        extension = None
    
    # Download the image
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    # Try to determine extension from content-type if not in URL
    if not extension or extension not in allowed_extensions:
        content_type = response.headers.get('content-type', '')
        if content_type.startswith('image/'):
            mime_to_ext = {
                'image/jpeg': 'jpg',
                'image/jpg': 'jpg', 
                'image/png': 'png',
                'image/gif': 'gif',
                'image/bmp': 'bmp',
                'image/webp': 'webp'
            }
            extension = mime_to_ext.get(content_type)
    
    # Validate extension
    if not extension or extension not in allowed_extensions:
        raise ValueError(f"Unsupported file extension: {extension}")
    
    # Generate unique filename
    base_name = original_filename.rsplit('.', 1)[0] if '.' in original_filename else 'image'
    base_name = base_name[:50]  # Limit length
    
    # Remove unsafe characters
    safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
    base_name = ''.join(c if c in safe_chars else '_' for c in base_name)
    
    # Generate unique filename to avoid collisions
    timestamp = str(int(time.time()))
    filename = f"{base_name}_{timestamp}.{extension}"
    
    # Ensure filename is unique
    counter = 1
    original_filename = filename
    while os.path.exists(os.path.join(upload_folder, filename)):
        name_part = original_filename.rsplit('.', 1)[0]
        filename = f"{name_part}_{counter}.{extension}"
        counter += 1
    
    # Save the file
    file_path = os.path.join(upload_folder, filename)
    with open(file_path, 'wb') as f:
        f.write(response.content)
    
    # Return filename and URL path
    file_url = f'/uploads/{filename}'
    return filename, file_url
