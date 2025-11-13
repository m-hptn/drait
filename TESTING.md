# Testing Guide for DRAIT

## Overview

DRAIT uses pytest for testing. The test suite ensures correctness of the core metamodel and future components.

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
# Using pytest directly
pytest

# Using Python module
python3 -m pytest

# Using the test runner script
./run_tests.sh
```

## VSCode Integration

See [.vscode/README.md](.vscode/README.md) for detailed VSCode setup instructions.

### Quick VSCode Setup

1. Install Python extension for VSCode
2. Install pytest: `pip install pytest pytest-cov`
3. Open Testing panel (flask icon in left sidebar)
4. Tests should auto-discover
5. Click play buttons to run tests

## Test Structure

```
tests/
├── __init__.py
├── test_metamodel.py      # Core metamodel tests (40+ tests)
└── README.md
```

## Test Categories

Tests use pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower)
- `@pytest.mark.slow` - Long-running tests

Run specific categories:

```bash
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m "not slow"    # Skip slow tests
```

## Current Test Coverage

### Metamodel Tests (test_metamodel.py)

✅ **TypeReference**
- Simple types (`str`, `int`)
- Optional types (`Optional[str]`)
- Generic types (`List[str]`, `Dict[str, int]`)
- Nested generics (`Dict[str, List[int]]`)
- Serialization/deserialization

✅ **Position**
- Creation with coordinates
- Width and height
- Serialization roundtrip

✅ **Decorator**
- Simple decorators (`@property`)
- Decorators with modules (`@dataclass`)
- Decorator arguments
- Serialization

✅ **Parameter**
- Positional parameters
- Keyword parameters
- Default values
- Type annotations
- Serialization

✅ **Attribute**
- Public, protected, private visibility
- Type references
- Default values
- Static attributes
- Readonly properties
- Serialization with UUID preservation

✅ **Method**
- Regular methods
- Static methods (`@staticmethod`)
- Class methods (`@classmethod`)
- Abstract methods (`@abstractmethod`)
- Parameters and return types
- Method body preservation
- Serialization

✅ **Class**
- Basic class creation
- Attributes and methods
- Inheritance (base classes)
- Abstract classes
- Diagram positions
- Stereotypes
- Decorators
- Complete serialization

✅ **Relationship**
- Inheritance
- Association
- Aggregation
- Composition
- Dependency
- Multiplicity
- Navigability
- Role names
- Serialization

✅ **Package**
- Package creation
- Multiple classes
- Relationships between classes
- Imports
- Serialization

✅ **Project**
- Project metadata
- Multiple packages
- Version information
- Complete model roundtrip

✅ **Integration Tests**
- Complete model creation
- Full serialization/deserialization
- Model with relationships
- Data integrity verification

**Total: 40+ unit tests covering all metamodel components**

## Running Tests

### All Tests

```bash
pytest
```

### Verbose Output

```bash
pytest -v
```

### With Coverage

```bash
pytest --cov=src/drait --cov-report=term-missing --cov-report=html
```

Then open `htmlcov/index.html` for detailed coverage report.

### Specific Test File

```bash
pytest tests/test_metamodel.py
```

### Specific Test Class

```bash
pytest tests/test_metamodel.py::TestClass
```

### Specific Test Function

```bash
pytest tests/test_metamodel.py::TestClass::test_method
```

### Stop on First Failure

```bash
pytest -x
```

### Show Print Statements

```bash
pytest -s
```

### Re-run Last Failed

```bash
pytest --lf
```

## Writing Tests

### Test File Naming

- Files: `test_*.py`
- Classes: `Test*`
- Functions: `test_*`

### Example Test

```python
import pytest
from drait.metamodel import Class, Attribute, TypeReference

class TestMyFeature:
    """Test suite for my feature."""

    @pytest.mark.unit
    def test_something(self):
        """Test description following Given-When-Then pattern."""
        # Given (Arrange)
        cls = Class(name="TestClass")

        # When (Act)
        result = cls.to_dict()

        # Then (Assert)
        assert result["name"] == "TestClass"
        assert "id" in result
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Clear test names** describing what is tested
3. **Use markers** to categorize tests
4. **Test edge cases** not just happy paths
5. **Test serialization** for data classes
6. **Verify immutability** where applicable

## CI/CD Integration

Tests can be integrated into GitHub Actions (when configured).

Example workflow:

```yaml
- name: Run tests
  run: pytest --cov=src/drait
```

## Troubleshooting

### pytest not found

```bash
pip install pytest pytest-cov
```

### Import errors

Ensure `PYTHONPATH` includes `src`:

```bash
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
pytest
```

### VSCode not discovering tests

1. Check Python interpreter is selected
2. Reload window: Ctrl+Shift+P → "Developer: Reload Window"
3. Check Output → Python for errors
4. Manually configure: Ctrl+Shift+P → "Python: Configure Tests"

## Next Steps

- Add integration tests for code generator (when implemented)
- Add integration tests for AST parser (when implemented)
- Add end-to-end tests for synchronization engine
- Set up continuous testing in CI/CD
- Add performance benchmarks
