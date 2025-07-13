"""Application constants and configuration."""

import os

# File extensions (whitelist only safe image formats)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Directory paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
IMAGES_FOLDER = os.path.join(BASE_DIR, 'images')
CONVERTED_FOLDER = os.path.join(BASE_DIR, 'converted')
TEMPLATES_FOLDER = os.path.join(BASE_DIR, 'templates')

# Security limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_RESOLUTION = 1000
MIN_RESOLUTION = 10
MAX_FILENAME_LENGTH = 255

# ANSI conversion defaults
DEFAULT_BRIGHTNESS = 1.0
DEFAULT_RESOLUTION = 160
DEFAULT_FONT_SIZE = 8

# Effect types
EFFECT_TYPES = {
    0: 'rainbow',
    1: 'glitch', 
    2: 'matrix',
    3: 'fire',
    4: 'neon'
}
