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

Tests are automatically run via GitHub Actions on every push and pull request to `main` or `develop` branches.

### Automated Testing

The CI pipeline (`.github/workflows/test.yml`) includes:

1. **Code Quality Checks** (fail-fast):
   - Ruff linting (`ruff check`)
   - Ruff formatting (`ruff format --check`)
   - mypy type checking (`mypy src/drait/`)

2. **Multi-version Testing**:
   - Python versions: 3.10, 3.11, 3.12, 3.13
   - Operating systems: Ubuntu (all versions), macOS (3.10, 3.13), Windows (3.10, 3.13)
   - 82 test cases across all combinations

3. **Coverage Verification**:
   - Minimum 80% code coverage required
   - Coverage reports uploaded to Codecov (if configured)
   - Fails if coverage drops below threshold

### Viewing CI Results

Check the Actions tab on GitHub: https://github.com/m-hptn/drait/actions

## Desktop Application Testing

⚠️ **Manual Testing Required - Desktop App Not in CI**

The Electron desktop application is **not automatically tested** by GitHub Actions. Contributors must test manually before submitting PRs.

### Why Not Automated?

- Electron GUI testing requires more complex setup
- Visual verification needed for UI components
- Different testing tools required (e.g., Spectron, Playwright)
- May be added in future iterations

### Manual Testing Process

#### Prerequisites

```bash
cd src/desktop
npm install
```

#### Running the Desktop App

```bash
# Development mode with hot reload
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Desktop App Testing Checklist

Before submitting PRs that touch the desktop app (`src/desktop/`), verify:

**Core Functionality:**
- [ ] Application launches without errors
- [ ] No errors in DevTools console (Ctrl+Shift+I / Cmd+Option+I)

**File Operations:**
- [ ] Single Python file import works
- [ ] Folder/directory import works
- [ ] File picker dialog functions correctly

**Diagram Visualization:**
- [ ] UML diagram renders with React Flow
- [ ] Classes display correctly with attributes and methods
- [ ] Package grouping shows proper hierarchy
- [ ] Relationships (arrows) render correctly

**Interaction:**
- [ ] Drag-and-drop node positioning works
- [ ] Zoom in/out functions properly
- [ ] Pan/scroll through large diagrams
- [ ] Resize package containers

**Data Persistence:**
- [ ] Layout positions are saved automatically
- [ ] Positions restore correctly on re-open
- [ ] No data loss on app restart

**UI/UX:**
- [ ] Interface is responsive and intuitive
- [ ] Buttons and controls work as expected
- [ ] Error messages are clear and helpful

### Platform-Specific Testing

If possible, test on multiple platforms:
- **Linux** (primary development platform)
- **macOS** (if available)
- **Windows** (if available)

Different platforms may have different behaviors with:
- File path handling
- Window rendering
- Keyboard shortcuts

### Reporting Desktop App Issues

When reporting bugs for the desktop app:
1. Specify OS and version
2. Include steps to reproduce
3. Attach screenshots if relevant
4. Check browser console for error messages
5. Note any relevant configuration

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
