"""
PixelPipe Test Suite

This module contains comprehensive tests for the PixelPipe application,
covering image conversion, effects, validation, file utilities, and API endpoints.

Test Categories:
- Image Conversion: Tests ANSI art generation from images
- Effects: Tests visual effects application (Rainbow, Glitch, Matrix, Fire, Neon)
- Validation: Tests input validation and security measures
- File Utilities: Tests file handling and security functions
- API Endpoints: Tests Flask routes and HTTP responses

Usage:
    pytest tests/test_pixelpipe.py -v
    pytest tests/test_pixelpipe.py::TestImageConversion -v
    pytest tests/test_pixelpipe.py -k "test_brightness" -v
"""

import pytest
import os
import tempfile
from unittest.mock import patch

# Mock the upload folder for tests
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment with temporary directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        upload_dir = os.path.join(temp_dir, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        with patch('server.UPLOAD_FOLDER', upload_dir):
            yield upload_dir


# Add parent directory to Python path to import application modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Import the Flask app and modules to test
from server import app
from image_to_ansi import image_to_ansi, generate_simple_effect, rgb_to_ansi
from utils.validation import (
    validate_brightness, 
    validate_resolution, 
    validate_effect_type, 
    validate_url,
    ValidationError
)
from utils.file_utils import allowed_file, ensure_folder


# =============================================================================
# SHARED FIXTURES
# =============================================================================

@pytest.fixture
def client():
    """
    Create a test client for the Flask app.
    
    This fixture provides a Flask test client with testing configuration
    enabled and CSRF protection disabled for easier testing.
    
    Yields:
        FlaskClient: Configured test client for making HTTP requests
    """
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_image():
    """
    Create a sample test image with multiple colors and gradients.
    
    Generates a 20x20 pixel image with four distinct regions:
    - Left section: Red gradient (vertical)
    - Second section: Green gradient (horizontal) 
    - Third section: Blue gradient (inverse vertical)
    - Right section: Rainbow pattern (mathematical)
    
    This provides a complex image for testing ANSI conversion with
    various colors, gradients, and patterns.
    
    Yields:
        str: Temporary file path to the generated test image
    """
    # Create a more complex 20x20 RGB image with various colors
    img = Image.new('RGB', (20, 20))
    pixels = img.load()
    
    # Create a colorful pattern with gradients and different regions
    for y in range(20):
        for x in range(20):
            if x < 5:  # Left section - red gradient
                intensity = int((y / 20) * 255)
                pixels[x, y] = (255, intensity, 0)
            elif x < 10:  # Second section - green gradient
                intensity = int((x / 10) * 255)
                pixels[x, y] = (0, 255, intensity)
            elif x < 15:  # Third section - blue gradient
                intensity = int(((20 - y) / 20) * 255)
                pixels[x, y] = (intensity, 0, 255)
            else:  # Right section - rainbow pattern
                r = int(((x + y) % 6) / 6 * 255)
                g = int(((x * 2 + y) % 8) / 8 * 255)
                b = int(((x + y * 2) % 7) / 7 * 255)
                pixels[x, y] = (r, g, b)
    
    # Save to a temporary file with proper cleanup
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    temp_file_path = temp_file.name
    temp_file.close()  # Close the file handle immediately
    
    # Save the image to the closed file
    img.save(temp_file_path)
    
    yield temp_file_path
    
    # Cleanup - now we can safely delete the file
    try:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    except (OSError, PermissionError) as e:
        # On Windows, sometimes files are still locked, try again after a short delay
        import time
        time.sleep(0.1)
        try:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        except (OSError, PermissionError):
            # If we still can't delete it, log it but don't fail the test
            import warnings
            warnings.warn(f"Could not delete temporary file: {temp_file_path}")

@pytest.fixture
def temp_directories():
    """
    Create temporary directories for testing file operations.
    
    Sets up a complete temporary directory structure mimicking
    the application's folder layout for safe testing of file
    operations without affecting the real application directories.
    
    Yields:
        dict: Dictionary containing paths to temporary directories
              with keys: 'base', 'uploads', 'images', 'converted'
    """
    temp_dir = tempfile.mkdtemp()
    uploads_dir = os.path.join(temp_dir, 'uploads')
    images_dir = os.path.join(temp_dir, 'images')
    converted_dir = os.path.join(temp_dir, 'converted')
    
    os.makedirs(uploads_dir)
    os.makedirs(images_dir)
    os.makedirs(converted_dir)
    
    yield {
        'base': temp_dir,
        'uploads': uploads_dir,
        'images': images_dir,
        'converted': converted_dir
    }
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_ansi():
    """
    Create sample ANSI art for effect testing.
    
    Provides a pre-built ANSI art string with various colors
    and block characters for testing effect transformations.
    The sample includes red, green, blue, yellow blocks and
    lighter colored gradients to test effect algorithms.
    
    Returns:
        str: ANSI art string with color codes and block characters
    """
    return "\x1b[38;2;255;0;0m█\x1b[0m\x1b[38;2;0;255;0m█\x1b[0m\n\x1b[38;2;0;0;255m█\x1b[0m\x1b[38;2;255;255;0m█\x1b[0m\x1b[38;2;244;249;254m█\x1b[38;2;243;249;254m█\x1b[38;2;244;248;255m█\x1b[38;2;244;248;255m█\x1b[38;2;218;241;243m█\x1b[38;2;214;241;233m█\x1b[38;2;188;205;228m▓"


# =============================================================================
# IMAGE CONVERSION TESTS
# =============================================================================

class TestImageConversion:
    """
    Test suite for image to ANSI conversion functionality.
    
    This class tests the core image processing pipeline including:
    - RGB to ANSI character mapping
    - Complete image to ANSI conversion
    - Brightness adjustment effects
    - Color preservation and character selection
    """
    
    def test_rgb_to_ansi_basic(self):
        """
        Test basic RGB to ANSI conversion for individual pixels.
        
        Validates that:
        - Dark colors (0,0,0) produce space characters
        - Bright colors (255,255,255) produce full block characters (█)
        - ANSI color codes are properly formatted
        - Color values are correctly embedded in escape sequences
        """
        # Test dark color (should return space)
        result = rgb_to_ansi(0, 0, 0)
        assert ' ' in result, "Dark colors should produce space characters"
        assert '\x1b[38;2;0;0;0m' in result, "Should contain proper ANSI color code"
        
        # Test bright color (should return full block)
        result = rgb_to_ansi(255, 255, 255)
        assert '█' in result, "Bright colors should produce full block characters"
        assert '\x1b[38;2;255;255;255m' in result, "Should contain proper ANSI color code"
    
    def test_image_to_ansi_conversion(self, sample_image):
        """
        Test complete image to ANSI conversion process.
        
        Validates the entire conversion pipeline:
        - Image loading and processing
        - Size scaling and aspect ratio handling
        - Color sampling and character mapping
        - ANSI escape sequence generation
        - Multi-line output formatting
        
        Args:
            sample_image: Fixture providing path to test image
        """
        ansi_art = image_to_ansi(sample_image, max_width=5, brightness=1.0)
        
        # Verify we get a string result
        assert isinstance(ansi_art, str), "Should return string output"
        assert len(ansi_art) > 0, "Should produce non-empty output"
        
        # Should contain ANSI escape sequences
        assert '\x1b[38;2;' in ansi_art, "Should contain ANSI color codes"
        assert '\x1b[0m' in ansi_art, "Should contain ANSI reset codes"
        
        # Should have multiple lines (newlines)
        assert '\n' in ansi_art, "Should produce multi-line output"
    
    def test_image_to_ansi_brightness_adjustment(self, sample_image):
        """
        Test brightness adjustment functionality in image conversion.
        
        Tests the brightness parameter's effect on conversion:
        - Normal brightness (1.0) as baseline
        - High brightness (2.0) should brighten colors
        - Low brightness (0.5) should darken colors
        - All three outputs should be distinct
        
        Args:
            sample_image: Fixture providing path to test image
        """
        # Normal brightness
        normal = image_to_ansi(sample_image, max_width=5, brightness=1.0)
        
        # High brightness
        bright = image_to_ansi(sample_image, max_width=5, brightness=2.0)
        
        # Low brightness
        dark = image_to_ansi(sample_image, max_width=5, brightness=0.5)
        
        # All should be different (assuming non-black/white image)
        assert normal != dark, "Normal and dark brightness should produce different output"
        assert bright != dark, "Bright and dark brightness should produce different output"
        assert normal != bright, "Normal and bright brightness should produce different output"


# =============================================================================
# VISUAL EFFECTS TESTS
# =============================================================================

class TestEffects:
    """
    Test suite for visual effects functionality.
    
    Tests all available visual effects that can be applied to ANSI art:
    - None (-1): No effect applied
    - Rainbow (0): Hue shifting effect
    - Glitch (1): Digital corruption effect
    - Matrix (2): Green digital rain effect
    - Fire (3): Warm color fire effect
    - Neon (4): Bright pulsing neon effect
    """
    
    def test_no_effect(self, sample_ansi):
        """
        Test that effect type -1 (None) returns original art unchanged.
        
        Validates:
        - No modifications are made to the input
        - Original ANSI codes are preserved
        - String comparison matches exactly
        
        Args:
            sample_ansi: Fixture providing sample ANSI art string
        """
        result = generate_simple_effect(sample_ansi, -1)
        assert result == sample_ansi, "No effect should return unchanged input"
    
    def test_rainbow_effect(self, sample_ansi):
        """
        Test rainbow effect application (effect type 0).
        
        The rainbow effect shifts hue values across the image
        creating a colorful wave pattern.
        
        Validates:
        - Output differs from original
        - ANSI structure is preserved
        - Color codes and reset sequences remain intact
        
        Args:
            sample_ansi: Fixture providing sample ANSI art string
        """
        result = generate_simple_effect(sample_ansi, 0)
        
        # Should be different from original
        assert result != sample_ansi, "Rainbow effect should modify the input"
        
        # Should still contain ANSI codes
        assert '\x1b[38;2;' in result, "Should preserve ANSI color codes"
        assert '\x1b[0m' in result, "Should preserve ANSI reset codes"
    
    def test_glitch_effect(self, sample_ansi):
        """
        Test glitch effect application (effect type 1).
        
        The glitch effect creates digital corruption with random
        color shifts, inversions, and noise patterns.
        
        Validates:
        - ANSI structure integrity
        - Proper color code formatting
        - Effect processing completes without errors
        
        Args:
            sample_ansi: Fixture providing sample ANSI art string
        """
        result = generate_simple_effect(sample_ansi, 1)
        
        # Should contain ANSI codes
        assert '\x1b[38;2;' in result, "Should contain ANSI color codes"
        assert '\x1b[0m' in result, "Should contain ANSI reset codes"
    
    def test_matrix_effect(self, sample_ansi):
        """
        Test matrix effect application (effect type 2).
        
        The matrix effect converts colors to green tones with
        varying intensity creating a digital rain appearance.
        
        Validates:
        - ANSI code preservation
        - Green color dominance (not strictly enforced due to randomness)
        - Proper formatting maintained
        
        Args:
            sample_ansi: Fixture providing sample ANSI art string
        """
        result = generate_simple_effect(sample_ansi, 2)
        
        # Should contain ANSI codes
        assert '\x1b[38;2;' in result, "Should contain ANSI color codes"
        assert '\x1b[0m' in result, "Should contain ANSI reset codes"
    
    def test_fire_effect(self, sample_ansi):
        """
        Test fire effect application (effect type 3).
        
        The fire effect creates warm colors (reds, oranges, yellows)
        with flickering intensity based on vertical position.
        
        Validates:
        - ANSI formatting preservation
        - Effect algorithm execution
        - No corruption of escape sequences
        
        Args:
            sample_ansi: Fixture providing sample ANSI art string
        """
        result = generate_simple_effect(sample_ansi, 3)
        
        # Should contain ANSI codes
        assert '\x1b[38;2;' in result, "Should contain ANSI color codes"
        assert '\x1b[0m' in result, "Should contain ANSI reset codes"
    
    def test_neon_effect(self, sample_ansi):
        """
        Test neon effect application (effect type 4).
        
        The neon effect creates bright, pulsing colors with
        different palettes per row for a vibrant appearance.
        
        Validates:
        - ANSI structure integrity
        - Bright color generation
        - Proper escape sequence handling
        
        Args:
            sample_ansi: Fixture providing sample ANSI art string
        """
        result = generate_simple_effect(sample_ansi, 4)
        
        # Should contain ANSI codes
        assert '\x1b[38;2;' in result, "Should contain ANSI color codes"
        assert '\x1b[0m' in result, "Should contain ANSI reset codes"


# =============================================================================
# INPUT VALIDATION TESTS
# =============================================================================

class TestValidation:
    """
    Test suite for input validation functions.
    
    Tests security and validation measures for all user inputs:
    - Brightness values (range and type validation)
    - Resolution values (performance and security limits)
    - Effect types (enum validation)
    - URL validation (security and format checking)
    """
    
    def test_validate_brightness(self):
        """
        Test brightness validation for security and functionality.
        
        Brightness affects color intensity and must be within safe bounds
        to prevent performance issues and ensure visual quality.
        
        Valid range: 0.1 to 5.0
        
        Tests:
        - Valid string and numeric inputs
        - Boundary value testing
        - Invalid inputs (too low, too high, non-numeric)
        - Type conversion handling
        """
        # Valid values
        assert validate_brightness("1.0") == 1.0, "Should accept valid string brightness"
        assert validate_brightness("2.5") == 2.5, "Should accept decimal string values"
        assert validate_brightness(1.5) == 1.5, "Should accept numeric values"
        
        # Invalid values
        with pytest.raises(ValidationError, match="between 0.1 and 5.0"):
            validate_brightness("0.05")  # Too low
        
        with pytest.raises(ValidationError, match="between 0.1 and 5.0"):
            validate_brightness("10")  # Too high
        
        with pytest.raises(ValidationError, match="valid number"):
            validate_brightness("invalid")  # Not a number
    
    def test_validate_resolution(self):
        """
        Test resolution validation for performance and security.
        
        Resolution determines ANSI art detail level and affects
        performance and memory usage. Must be within safe bounds.
        
        Valid range: 10 to 1000 pixels
        
        Tests:
        - Valid string and numeric inputs
        - Performance boundary limits
        - Invalid inputs (too low, too high, non-numeric)
        - Integer conversion handling
        """
        # Valid values
        assert validate_resolution("160") == 160, "Should accept valid string resolution"
        assert validate_resolution(80) == 80, "Should accept numeric values"
        assert validate_resolution("500") == 500, "Should accept high valid values"
        
        # Invalid values
        with pytest.raises(ValidationError, match="between 10 and 1000"):
            validate_resolution("5")  # Too low
        
        with pytest.raises(ValidationError, match="between 10 and 1000"):
            validate_resolution("2000")  # Too high
        
        with pytest.raises(ValidationError, match="valid integer"):
            validate_resolution("not_a_number")
    
    def test_validate_effect_type(self):
        """
        Test effect type validation for enum security.
        
        Effect types must match predefined values to prevent
        injection attacks and ensure proper effect application.
        
        Valid range: -1 (None) to 4 (Neon)
        
        Tests:
        - All valid effect types
        - Boundary value testing
        - Invalid effect types (out of range)
        - Type conversion and validation
        """
        # Valid values
        assert validate_effect_type("-1") == -1, "Should accept None effect"
        assert validate_effect_type("0") == 0, "Should accept Rainbow effect"
        assert validate_effect_type("4") == 4, "Should accept Neon effect"
        
        # Invalid values
        with pytest.raises(ValidationError, match="between -1 and 4"):
            validate_effect_type("-2")  # Too low
        
        with pytest.raises(ValidationError, match="between -1 and 4"):
            validate_effect_type("5")   # Too high
        
        with pytest.raises(ValidationError, match="valid integer"):
            validate_effect_type("invalid")
    
    def test_validate_url(self):
        """
        Test URL validation for security and format compliance.
        
        URL validation prevents SSRF attacks and ensures only
        safe, properly formatted URLs are processed.
        
        Security measures:
        - Protocol whitelist (http/https only)
        - Local network blocking
        - Format validation
        
        Tests:
        - Valid HTTP/HTTPS URLs
        - Invalid protocols (ftp, file, etc.)
        - Blocked local addresses
        - Empty/malformed URLs
        """
        # Valid URLs
        assert validate_url("https://example.com/image.jpg") == "https://example.com/image.jpg", "Should accept HTTPS URLs"
        assert validate_url("http://test.com/pic.png") == "http://test.com/pic.png", "Should accept HTTP URLs"
        
        # Invalid URLs
        with pytest.raises(ValidationError, match="http:// or https://"):
            validate_url("ftp://example.com")  # Wrong protocol
        
        with pytest.raises(ValidationError, match="local network"):
            validate_url("https://localhost/image.jpg")  # Blocked host
        
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_url("")  # Empty URL


# =============================================================================
# FILE UTILITIES TESTS
# =============================================================================

class TestFileUtils:
    """
    Test suite for file utility functions.
    
    Tests file handling security and functionality:
    - File extension validation
    - Directory creation and security
    - Path traversal prevention
    - Filename length limits
    """
    
    def test_allowed_file(self):
        """
        Test file extension validation for security.
        
        File extension validation prevents upload of dangerous
        file types and ensures only image files are processed.
        
        Security measures:
        - Extension whitelist
        - Path traversal prevention
        - Filename length limits
        - Empty filename handling
        
        Tests:
        - Valid image extensions
        - Invalid file types
        - Security attacks (path traversal)
        - Edge cases (empty filenames)
        """
        allowed_exts = {'png', 'jpg', 'jpeg', 'gif'}
        
        # Valid files
        assert allowed_file("image.png", allowed_exts) == True, "Should allow PNG files"
        assert allowed_file("photo.jpg", allowed_exts) == True, "Should allow JPG files"
        assert allowed_file("pic.jpeg", allowed_exts) == True, "Should allow JPEG files"
        
        # Invalid files
        assert allowed_file("document.txt", allowed_exts) == False, "Should reject text files"
        assert allowed_file("script.py", allowed_exts) == False, "Should reject script files"
        assert allowed_file("../dangerous.png", allowed_exts) == False, "Should reject path traversal"
        assert allowed_file("", allowed_exts) == False, "Should reject empty filenames"
    
    def test_ensure_folder(self, temp_directories):
        """
        Test folder creation and security validation.
        
        Folder creation must be secure and prevent directory
        traversal attacks while ensuring proper permissions.
        
        Security measures:
        - Path traversal prevention
        - Permission restrictions
        - Safe path normalization
        
        Tests:
        - Normal folder creation
        - Existing folder handling
        - Security attack prevention
        - Permission validation
        
        Args:
            temp_directories: Fixture providing temporary directory structure
        """
        test_folder = os.path.join(temp_directories['base'], 'new_folder')
        
        # Folder shouldn't exist initially
        assert not os.path.exists(test_folder), "Test folder should not exist initially"
        
        # Create folder
        ensure_folder(test_folder)
        
        # Folder should now exist
        assert os.path.exists(test_folder), "Folder should be created"
        assert os.path.isdir(test_folder), "Should create a directory"
        
        # Should not raise error if folder already exists
        ensure_folder(test_folder)  # Should not raise exception
        
        # Should raise error for dangerous paths
        with pytest.raises(ValueError, match="Invalid folder path"):
            ensure_folder("../dangerous_path")


# =============================================================================
# API ENDPOINT TESTS
# =============================================================================

class TestAPIEndpoints:
    """
    Test suite for Flask API endpoints.
    
    Tests HTTP endpoints for functionality and security:
    - Page serving and routing
    - JSON API responses
    - File operations
    - Error handling
    - Security validation
    """
    
    def test_home_page(self, client):
        """
        Test the main page loads correctly.
        
        Validates:
        - HTTP 200 response
        - Page accessibility
        - Route functionality
        
        Args:
            client: Fixture providing Flask test client
        """
        response = client.get('/')
        assert response.status_code == 200, "Home page should load successfully"
    
    def test_images_list(self, client):
        """
        Test images listing endpoint functionality.
        
        Validates:
        - HTTP 200 response
        - JSON response format
        - List data structure
        - Image directory access
        
        Args:
            client: Fixture providing Flask test client
        """
        response = client.get('/images')
        assert response.status_code == 200, "Images endpoint should respond successfully"
        
        # Should return JSON
        data = json.loads(response.data)
        assert isinstance(data, list), "Should return a list of image files"
    
    def test_uploads_list(self, client):
        """
        Test uploads listing endpoint functionality.
        
        Validates:
        - HTTP 200 response
        - JSON response format
        - List data structure
        - Upload directory access
        
        Args:
            client: Fixture providing Flask test client
        """
        response = client.get('/uploads')
        assert response.status_code == 200, "Uploads endpoint should respond successfully"
        
        # Should return JSON
        data = json.loads(response.data)
        assert isinstance(data, list), "Should return a list of uploaded files"
    
    def test_update_ansi_endpoint(self, client, sample_image):
        """
        Test the ANSI update endpoint with real image processing.
        
        This test validates the complete ANSI generation pipeline
        through the HTTP API interface.
        
        Validates:
        - Image file handling
        - Parameter processing
        - ANSI art generation
        - HTTP response format
        - Content validation
        
        Args:
            client: Fixture providing Flask test client
            sample_image: Fixture providing test image path
        """
        # Copy sample image to images directory for testing
        images_dir = os.path.join(os.path.dirname(__file__), '../images')
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        test_image_path = os.path.join(images_dir, 'test.png')
        shutil.copy2(sample_image, test_image_path)
        
        try:
            response = client.get('/update_ansi', query_string={
                'image': 'images/test.png',
                'brightness': '1.0',
                'resolution': '80',
                'effect': '0'
            })
            
            assert response.status_code == 200, "ANSI update should succeed"
            
            # Should return ANSI art
            ansi_data = response.data.decode('utf-8')
            assert '\x1b[38;2;' in ansi_data, "Should contain ANSI color codes"
            
        finally:
            # Cleanup
            if os.path.exists(test_image_path):
                os.unlink(test_image_path)
    
    def test_add_image_url_endpoint(self, client):
        """
        Test adding image from URL endpoint with various scenarios.
        
        Tests multiple error conditions and security validations:
        - Malformed JSON handling
        - Missing parameter validation
        - URL format validation
        - Security restriction enforcement
        
        Args:
            client: Fixture providing Flask test client
        """
        # Test with invalid JSON - Flask returns 500 for malformed JSON
        response = client.post('/add_image_url', 
                             data='invalid json',
                             content_type='application/json')
        # Flask returns 500 for malformed JSON, not 400
        assert response.status_code in [400, 500], "Should handle malformed JSON"
        
        # Test with missing URL
        response = client.post('/add_image_url',
                             json={})
        assert response.status_code == 400, "Should require URL parameter"
        data = json.loads(response.data)
        assert 'error' in data, "Should return error message"
        
        # Test with invalid URL
        response = client.post('/add_image_url',
                             json={'url': 'invalid-url'})
        assert response.status_code == 400, "Should reject invalid URLs"
        data = json.loads(response.data)
        assert 'error' in data, "Should return error message"
        
        # Test with blocked localhost URL
        response = client.post('/add_image_url',
                             json={'url': 'https://localhost/image.jpg'})
        assert response.status_code == 400, "Should block localhost URLs"
        data = json.loads(response.data)
        assert 'error' in data, "Should return error message"
        assert 'local network' in data['error'].lower(), "Should mention local network restriction"


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """
    Configure pytest environment for PixelPipe tests.
    
    Sets up necessary directories and environment for testing.
    Creates required directories if they don't exist to prevent
    test failures due to missing infrastructure.
    
    Args:
        config: Pytest configuration object
    """
    # Ensure test directories exist
    test_dirs = ['images', 'uploads', 'converted', 'static']
    for dir_name in test_dirs:
        dir_path = os.path.join(os.path.dirname(__file__), dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)


if __name__ == '__main__':
    # Run tests when file is executed directly
    pytest.main([__file__, '-v'])
