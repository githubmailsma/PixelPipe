"""Input validation utilities."""

import os
from typing import Union
from .constants import ALLOWED_EXTENSIONS

class ValidationError(Exception):
    """Custom validation error."""
    pass

def validate_image_path(image_path: str) -> str:
    """Validate and return clean image path."""
    if not image_path:
        raise ValidationError("Image path cannot be empty")
    
    # Prevent path traversal attacks
    if '..' in image_path or image_path.startswith('/'):
        raise ValidationError("Invalid image path")
    
    if not os.path.exists(image_path):
        raise ValidationError(f"Image file not found: {image_path}")
    
    return os.path.abspath(image_path)

def validate_brightness(brightness: Union[str, float]) -> float:
    """Validate brightness value."""
    try:
        value = float(brightness)
        if not 0.1 <= value <= 5.0:
            raise ValidationError("Brightness must be between 0.1 and 5.0")
        return value
    except (ValueError, TypeError):
        raise ValidationError("Brightness must be a valid number")

def validate_resolution(resolution: Union[str, int]) -> int:
    """Validate resolution value."""
    try:
        value = int(resolution)
        if not 10 <= value <= 1000:
            raise ValidationError("Resolution must be between 10 and 1000")
        return value
    except (ValueError, TypeError):
        raise ValidationError("Resolution must be a valid integer")

def validate_effect_type(effect_type: Union[str, int]) -> int:
    """Validate effect type."""
    try:
        value = int(effect_type)
        if not -1 <= value <= 4:
            raise ValidationError("Effect type must be between -1 and 4")
        return value
    except (ValueError, TypeError):
        raise ValidationError("Effect type must be a valid integer")

def validate_url(url: str) -> str:
    """Validate URL for image downloads."""
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")
    
    # Basic URL validation
    if not (url.startswith('http://') or url.startswith('https://')):
        raise ValidationError("URL must start with http:// or https://")
    
    # Prevent local network access
    blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
    for blocked in blocked_hosts:
        if blocked in url.lower():
            raise ValidationError("Access to local network is not allowed")
    
    return url
