"""
Tests for Phase 4: Advanced Python Features

Tests:
- Abstract classes (ABC)
- Abstract methods (@abstractmethod)
- Decorators (all types)
- Properties (@property)
- Dataclasses (@dataclass)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from drait.parsers.python_parser import PythonParser


def test_abstract_class_detection():
    """Test ABC detection."""
    source = """
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    assert len(package.classes) == 1
    cls = package.classes[0]
    assert cls.name == "Shape"
    assert cls.is_abstract == True
    assert "ABC" in cls.base_classes

    # Check abstract method
    assert len(cls.methods) == 1
    method = cls.methods[0]
    assert method.name == "area"
    assert method.is_abstract == True
    print("✓ test_abstract_class_detection passed")


def test_dataclass_decorator():
    """Test @dataclass detection."""
    source = """
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    cls = package.classes[0]
    assert len(cls.decorators) == 1
    assert cls.decorators[0].name == "dataclass"
    print("✓ test_dataclass_decorator passed")


def test_dataclass_with_arguments():
    """Test @dataclass with arguments."""
    source = """
from dataclasses import dataclass

@dataclass(frozen=True)
class ImmutablePoint:
    x: float
    y: float
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    cls = package.classes[0]
    assert len(cls.decorators) == 1
    dec = cls.decorators[0]
    assert dec.name == "dataclass"
    assert "frozen" in dec.arguments
    assert dec.arguments["frozen"] == "True"
    print("✓ test_dataclass_with_arguments passed")


def test_property_decorator():
    """Test @property detection."""
    source = """
class Temperature:
    def __init__(self):
        self._value = 0

    @property
    def celsius(self):
        return self._value

    @celsius.setter
    def celsius(self, value):
        self._value = value
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    cls = package.classes[0]
    # Should have 3 methods: __init__, celsius (getter), celsius (setter)
    assert len(cls.methods) >= 2

    # Find property getter
    property_methods = [m for m in cls.methods if any(d.name == "property" for d in m.decorators)]
    assert len(property_methods) == 1
    assert property_methods[0].name == "celsius"
    print("✓ test_property_decorator passed")


def test_static_method_decorator():
    """Test @staticmethod detection."""
    source = """
class MathUtils:
    @staticmethod
    def add(a, b):
        return a + b
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    cls = package.classes[0]
    method = cls.methods[0]
    assert method.is_static == True
    # Should have staticmethod in decorators
    assert any(d.name == "staticmethod" for d in method.decorators)
    print("✓ test_static_method_decorator passed")


def test_class_method_decorator():
    """Test @classmethod detection."""
    source = """
class MyClass:
    @classmethod
    def from_string(cls, s):
        return cls()
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    cls = package.classes[0]
    method = cls.methods[0]
    assert method.is_class_method == True
    assert any(d.name == "classmethod" for d in method.decorators)
    print("✓ test_class_method_decorator passed")


def test_multiple_decorators():
    """Test multiple decorators on one method."""
    source = """
from functools import lru_cache

class MyClass:
    @staticmethod
    @lru_cache(maxsize=128)
    def fibonacci(n):
        if n < 2:
            return n
        return MyClass.fibonacci(n-1) + MyClass.fibonacci(n-2)
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    method = package.classes[0].methods[0]
    assert len(method.decorators) >= 2
    decorator_names = [d.name for d in method.decorators]
    assert "staticmethod" in decorator_names
    assert "lru_cache" in decorator_names
    print("✓ test_multiple_decorators passed")


def test_abstract_dataclass():
    """Test combining ABC with @dataclass."""
    source = """
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Employee(ABC):
    name: str

    @abstractmethod
    def calculate_bonus(self):
        pass
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    cls = package.classes[0]
    # Should be abstract
    assert cls.is_abstract == True
    # Should have dataclass decorator
    assert any(d.name == "dataclass" for d in cls.decorators)
    # Should have abstract method
    abstract_methods = [m for m in cls.methods if m.is_abstract]
    assert len(abstract_methods) == 1
    print("✓ test_abstract_dataclass passed")


def test_custom_decorator():
    """Test custom decorator detection."""
    source = """
def my_decorator(func):
    return func

class MyClass:
    @my_decorator
    def my_method(self):
        pass
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    method = package.classes[0].methods[0]
    assert len(method.decorators) == 1
    assert method.decorators[0].name == "my_decorator"
    print("✓ test_custom_decorator passed")


def test_qualified_decorator():
    """Test module.decorator format."""
    source = """
import abc

class MyClass(abc.ABC):
    @abc.abstractmethod
    def my_method(self):
        pass
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    cls = package.classes[0]
    assert cls.is_abstract == True

    method = cls.methods[0]
    assert method.is_abstract == True
    # Check decorator has module info
    abstract_dec = [d for d in method.decorators if d.name == "abstractmethod"][0]
    assert abstract_dec.module == "abc"
    print("✓ test_qualified_decorator passed")


def main():
    """Run all tests."""
    print("=" * 70)
    print("Running Phase 4 Advanced Features Tests")
    print("=" * 70)

    tests = [
        test_abstract_class_detection,
        test_dataclass_decorator,
        test_dataclass_with_arguments,
        test_property_decorator,
        test_static_method_decorator,
        test_class_method_decorator,
        test_multiple_decorators,
        test_abstract_dataclass,
        test_custom_decorator,
        test_qualified_decorator,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1

    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
