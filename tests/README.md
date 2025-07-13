# Run tests with coverage
pytest

# Run tests with coverage and open report automatically
pytest --cov=. --cov-report=html && start htmlcov\index.html

# Run tests with detailed coverage report
pytest --cov=. --cov-report=html --cov-report=term-missing

# Run specific test classes with coverage
pytest tests/test_pixelpipe.py::TestImageConversion --cov=image_to_ansi

# Generate only HTML coverage report
pytest --cov=. --cov-report=html

The coverage report will be generated in the htmlcov/ directory and you can open htmlcov/index.html in your browser to see a detailed coverage report showing which lines of code are covered by tests.

# Exclude certain files from coverage
pytest --cov=. --cov-report=html --cov-exclude=tests/*