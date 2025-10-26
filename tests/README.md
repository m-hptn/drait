# DRAIT Tests

Unit and integration tests for the DRAIT Model-Driven Development Tool.

## Setup

Install test dependencies:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install pytest pytest-cov
```

## Running Tests

### All tests

```bash
pytest
```

Or use the test runner script:

```bash
./run_tests.sh
```

### Specific test file

```bash
pytest tests/test_metamodel.py
```

### With coverage

```bash
pytest --cov=src/drait --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

### Unit tests only

```bash
pytest -m unit
```

### Verbose output

```bash
pytest -v
```

## Test Structure

```
tests/
├── __init__.py
├── test_metamodel.py      # Metamodel unit tests
└── README.md             # This file
```

## Test Categories

Tests are marked with pytest markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Tests that take longer to run

## Writing Tests

Example test:

```python
import pytest
from drait.metamodel import Class, Attribute, TypeReference

class TestMyFeature:
    @pytest.mark.unit
    def test_something(self):
        """Test description."""
        # Arrange
        cls = Class(name="TestClass")

        # Act
        result = cls.to_dict()

        # Assert
        assert result["name"] == "TestClass"
```

## Current Test Coverage

The test suite covers:

- ✅ TypeReference (simple, optional, generic, nested)
- ✅ Position
- ✅ Decorator
- ✅ Parameter
- ✅ Attribute (all visibility levels)
- ✅ Method (regular, static, class methods, abstract)
- ✅ Class (with attributes, methods, inheritance, positions)
- ✅ Relationship (all types, multiplicity)
- ✅ Package
- ✅ Project
- ✅ Complete model serialization/deserialization

## CI/CD

Tests will run automatically on GitHub Actions when pushing to the repository (when configured).
