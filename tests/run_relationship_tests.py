"""
Simple test runner for relationship inference tests (without pytest).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from drait.parsers.python_parser import PythonParser
from drait.metamodel import RelationshipType


def test_simple_inheritance():
    """Test basic single inheritance."""
    source = """
class Animal:
    def __init__(self):
        self.alive = True

class Dog(Animal):
    def __init__(self):
        super().__init__()
        self.breed = "Unknown"
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    assert len(package.classes) == 2
    assert len(package.relationships) == 1
    rel = package.relationships[0]
    assert rel.type == RelationshipType.INHERITANCE

    class_map = {cls.id: cls.name for cls in package.classes}
    assert class_map[rel.source_id] == "Dog"
    assert class_map[rel.target_id] == "Animal"
    print("✓ test_simple_inheritance passed")


def test_composition():
    """Test composition with owned object."""
    source = """
class Engine:
    def __init__(self, hp: int):
        self.horsepower = hp

class Car:
    def __init__(self):
        self.engine: Engine = Engine(200)
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    composition_rels = [r for r in package.relationships if r.type == RelationshipType.COMPOSITION]
    assert len(composition_rels) == 1

    rel = composition_rels[0]
    class_map = {cls.id: cls.name for cls in package.classes}
    assert class_map[rel.source_id] == "Car"
    assert class_map[rel.target_id] == "Engine"
    print("✓ test_composition passed")


def test_aggregation():
    """Test aggregation with Optional type."""
    source = """
from typing import Optional

class Department:
    pass

class Employee:
    def __init__(self, dept: Optional[Department] = None):
        self.department: Optional[Department] = dept
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    aggregation_rels = [r for r in package.relationships if r.type == RelationshipType.AGGREGATION]
    assert len(aggregation_rels) == 1

    rel = aggregation_rels[0]
    class_map = {cls.id: cls.name for cls in package.classes}
    assert class_map[rel.source_id] == "Employee"
    assert class_map[rel.target_id] == "Department"
    print("✓ test_aggregation passed")


def test_dependency():
    """Test dependency from method parameter."""
    source = """
class Order:
    pass

class OrderProcessor:
    def process(self, order: Order) -> bool:
        return True
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    dependency_rels = [r for r in package.relationships if r.type == RelationshipType.DEPENDENCY]
    assert len(dependency_rels) == 1

    rel = dependency_rels[0]
    class_map = {cls.id: cls.name for cls in package.classes}
    assert class_map[rel.source_id] == "OrderProcessor"
    assert class_map[rel.target_id] == "Order"
    print("✓ test_dependency passed")


def test_no_dependency_for_attributes():
    """Test that attributes don't create dependencies."""
    source = """
class Engine:
    pass

class Car:
    def __init__(self):
        self.engine: Engine = Engine()

    def tune_engine(self, engine: Engine) -> None:
        pass
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    composition_rels = [r for r in package.relationships if r.type == RelationshipType.COMPOSITION]
    assert len(composition_rels) == 1

    dependency_rels = [r for r in package.relationships if r.type == RelationshipType.DEPENDENCY]
    assert len(dependency_rels) == 0  # Engine is an attribute, not a dependency
    print("✓ test_no_dependency_for_attributes passed")


def test_mixed_relationships():
    """Test class with multiple relationship types."""
    source = """
from typing import Optional

class Address:
    pass

class Department:
    pass

class Project:
    pass

class Employee:
    def __init__(self, dept: Optional[Department] = None):
        self.home_address: Address = Address()
        self.department: Optional[Department] = dept

    def assign_project(self, project: Project) -> None:
        pass
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    composition = [r for r in package.relationships if r.type == RelationshipType.COMPOSITION]
    aggregation = [r for r in package.relationships if r.type == RelationshipType.AGGREGATION]
    dependency = [r for r in package.relationships if r.type == RelationshipType.DEPENDENCY]

    assert len(composition) == 1  # Address
    assert len(aggregation) == 1  # Department
    assert len(dependency) == 1   # Project
    print("✓ test_mixed_relationships passed")


def test_nested_generic():
    """Test relationships with nested generic types."""
    source = """
from typing import List

class Task:
    pass

class Project:
    def __init__(self):
        self.tasks: List[Task] = []
"""
    parser = PythonParser()
    package = parser.parse_source(source)

    aggregation = [r for r in package.relationships if r.type == RelationshipType.AGGREGATION]
    assert len(aggregation) == 1

    rel = aggregation[0]
    class_map = {cls.id: cls.name for cls in package.classes}
    assert class_map[rel.target_id] == "Task"
    print("✓ test_nested_generic passed")


def main():
    """Run all tests."""
    print("=" * 70)
    print("Running Relationship Inference Tests")
    print("=" * 70)

    tests = [
        test_simple_inheritance,
        test_composition,
        test_aggregation,
        test_dependency,
        test_no_dependency_for_attributes,
        test_mixed_relationships,
        test_nested_generic,
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
