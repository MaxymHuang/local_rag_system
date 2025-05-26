# Testing Documentation

This document describes the comprehensive testing setup for the Local RAG System.

## Overview

The testing suite includes:
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows and component interactions
- **Security Tests**: Vulnerability scanning and security analysis
- **CI/CD Pipeline**: Automated testing on code changes

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_app.py              # Flask application tests
├── test_file_finder.py      # FileSystemRAG class tests
└── test_integration.py      # End-to-end integration tests
```

## Quick Start

### 1. Install Test Dependencies

```bash
pip install -r test_requirements.txt
```

### 2. Run All Tests

```bash
# Using pytest directly
pytest

# Using the test runner script
python run_tests.py all
```

### 3. Run Specific Test Types

```bash
# Unit tests only
python run_tests.py unit

# Integration tests only
python run_tests.py integration

# Quick tests (fast unit tests)
python run_tests.py quick
```

## Test Runner Script

The `run_tests.py` script provides convenient test execution modes:

### Available Modes

| Mode | Description |
|------|-------------|
| `install` | Install test dependencies |
| `unit` | Run unit tests for individual components |
| `integration` | Run integration tests for complete workflows |
| `all` | Run all tests with coverage reporting |
| `quick` | Run fast unit tests only |
| `lint` | Run code linting and style checks |
| `security` | Run security vulnerability scans |
| `ci` | Run complete CI pipeline locally |

### Usage Examples

```bash
# Install dependencies
python run_tests.py install

# Run unit tests
python run_tests.py unit

# Run all tests with coverage
python run_tests.py all

# Run CI pipeline locally
python run_tests.py ci

# Skip dependency installation
python run_tests.py unit --no-install
```

## Test Categories

### Unit Tests

#### Flask Application Tests (`test_app.py`)
- **Route Testing**: All Flask endpoints (`/`, `/status`, `/initialize`, `/search`, `/summarize`)
- **Error Handling**: Invalid inputs, missing parameters, server errors
- **Ollama Integration**: Connection testing, response parsing, error scenarios
- **Authentication**: Request validation and response formatting

#### FileSystemRAG Tests (`test_file_finder.py`)
- **Initialization**: Valid/invalid directories, Ollama connection
- **File Operations**: Reading different file types (PDF, DOCX, PPTX, text)
- **Index Building**: FAISS index creation, file discovery, error handling
- **Search Functionality**: Query processing, result ranking, edge cases
- **Summarization**: File content processing, Ollama integration, error handling

### Integration Tests (`test_integration.py`)

#### Complete Workflows
- **Full System Workflow**: Initialize → Search → Summarize
- **Error Recovery**: System behavior during failures
- **Concurrent Operations**: Thread safety and resource management

#### End-to-End Scenarios
- **Researcher Workflow**: Document discovery and analysis
- **Developer Workflow**: Codebase exploration and understanding
- **System Recovery**: Handling service interruptions

### Security Tests

- **Dependency Scanning**: Check for known vulnerabilities in dependencies
- **Code Analysis**: Static analysis for security issues
- **Input Validation**: Test for injection attacks and malformed inputs

## Coverage Reporting

### Generate Coverage Reports

```bash
# Terminal coverage report
pytest --cov=. --cov-report=term-missing

# HTML coverage report
pytest --cov=. --cov-report=html

# XML coverage report (for CI)
pytest --cov=. --cov-report=xml
```

### Coverage Targets

- **Overall Coverage**: > 85%
- **Critical Components**: > 90%
  - `app.py` (Flask routes)
  - `file_finder.py` (Core RAG functionality)

## Continuous Integration

### GitHub Actions Workflow

The CI pipeline (`.github/workflows/ci.yml`) includes:

1. **Multi-Python Testing**: Tests on Python 3.8, 3.9, 3.10, 3.11
2. **Dependency Caching**: Faster builds with pip cache
3. **Code Quality**: Linting with flake8
4. **Security Scanning**: Vulnerability checks with safety and bandit
5. **Docker Testing**: Container build and basic functionality tests
6. **Coverage Reporting**: Automatic coverage upload to Codecov

### Triggering CI

CI runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Local CI Simulation

```bash
# Run the complete CI pipeline locally
python run_tests.py ci
```

## Mocking Strategy

### External Dependencies

All external dependencies are mocked in tests:

- **Ollama API**: Mocked responses for chat and connection testing
- **File System**: Temporary directories and mock file operations
- **Network Requests**: Mocked HTTP requests to external services

### Fixtures

Key pytest fixtures in `conftest.py`:

- `client`: Flask test client
- `temp_dir`: Temporary directory for file operations
- `sample_files`: Pre-created test files
- `mock_ollama`: Mocked Ollama responses
- `rag_system`: Initialized FileSystemRAG instance
- `initialized_rag`: RAG system with built index

## Writing New Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test Structure

```python
class TestNewFeature:
    """Test cases for new feature."""
    
    def test_basic_functionality(self, fixture_name):
        """Test basic functionality works correctly."""
        # Arrange
        setup_data = "test data"
        
        # Act
        result = function_under_test(setup_data)
        
        # Assert
        assert result == expected_value
    
    @patch('module.external_dependency')
    def test_error_handling(self, mock_dependency):
        """Test error handling scenarios."""
        mock_dependency.side_effect = Exception("Test error")
        
        with pytest.raises(Exception):
            function_under_test()
```

### Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies
3. **Clear Names**: Test names should describe what they test
4. **Documentation**: Include docstrings for complex tests
5. **Edge Cases**: Test boundary conditions and error scenarios

## Debugging Tests

### Running Specific Tests

```bash
# Run a specific test file
pytest tests/test_app.py

# Run a specific test class
pytest tests/test_app.py::TestFlaskApp

# Run a specific test method
pytest tests/test_app.py::TestFlaskApp::test_index_route

# Run tests matching a pattern
pytest -k "test_ollama"
```

### Verbose Output

```bash
# Verbose output with print statements
pytest -v -s

# Show local variables on failure
pytest --tb=long

# Stop on first failure
pytest -x
```

### Debug Mode

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest --pdb -x
```

## Performance Testing

### Running Performance Tests

```bash
# Mark slow tests
pytest -m "not slow"  # Skip slow tests
pytest -m "slow"      # Run only slow tests
```

### Benchmarking

For performance-critical components, consider adding benchmark tests:

```python
import time

def test_search_performance(initialized_rag):
    """Test search performance."""
    start_time = time.time()
    results = initialized_rag.search("test query", k=100)
    end_time = time.time()
    
    assert end_time - start_time < 2.0  # Should complete in under 2 seconds
    assert len(results) <= 100
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `PYTHONPATH` includes project root
2. **Missing Dependencies**: Run `pip install -r test_requirements.txt`
3. **Ollama Mocking**: Ensure Ollama calls are properly mocked
4. **File Permissions**: Temporary directories may have permission issues

### Environment Setup

```bash
# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Create virtual environment
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# or
test_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r test_requirements.txt
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all existing tests pass
3. Add integration tests for new workflows
4. Update documentation
5. Verify CI pipeline passes

### Test Coverage Requirements

- New code must have > 90% test coverage
- All public methods must have tests
- Error conditions must be tested
- Integration points must be tested

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.3.x/testing/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/) 