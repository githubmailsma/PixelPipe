"""
Pytest configuration for PixelPipe tests.

This file is automatically loaded by pytest and provides
shared configuration and fixtures for all test files.
"""

import os
import sys
import pytest

# Add the current directory to Python path
# This allows tests to import application modules
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up the test environment before running tests.
    
    This fixture runs once per test session and ensures
    all necessary directories exist for testing.
    """
    # Ensure required directories exist
    test_dirs = ['images', 'uploads', 'converted', 'static', 'templates']
    for dir_name in test_dirs:
        dir_path = os.path.join(project_root, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
    
    yield
    
    # Cleanup can be added here if needed
