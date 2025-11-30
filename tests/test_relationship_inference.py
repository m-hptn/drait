"""
Tests for Phase 3: Relationship Inference in Python AST Parser.

Tests all relationship types:
- Inheritance
- Composition
- Aggregation
- Dependency
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from drait.metamodel import RelationshipType
from drait.parsers.python_parser import PythonParser


class TestInheritanceInference:
    """Test inheritance relationship detection."""

    def test_simple_inheritance(self):
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

        # Check classes
        assert len(package.classes) == 2
        assert any(cls.name == "Dog" for cls in package.classes)
        assert any(cls.name == "Animal" for cls in package.classes)

        # Check inheritance relationship
        assert len(package.relationships) == 1
        rel = package.relationships[0]
        assert rel.type == RelationshipType.INHERITANCE

        # Get class names
        class_map = {cls.id: cls.name for cls in package.classes}
        source_name = class_map[rel.source_id]
        target_name = class_map[rel.target_id]

        assert source_name == "Dog"
        assert target_name == "Animal"

    def test_multiple_inheritance(self):
        """Test multiple inheritance."""
        source = """
class Flyable:
    pass

class Swimmable:
    pass

class Duck(Flyable, Swimmable):
    pass
"""
        parser = PythonParser()
        package = parser.parse_source(source)

        # Should have 2 inheritance relationships (Duck -> Flyable, Duck -> Swimmable)
        inheritance_rels = [
            r for r in package.relationships if r.type == RelationshipType.INHERITANCE
        ]
        assert len(inheritance_rels) == 2

    def test_inheritance_chain(self):
        """Test inheritance chain A -> B -> C."""
        source = """
class Animal:
    pass

class Mammal(Animal):
    pass

class Dog(Mammal):
    pass
"""
        parser = PythonParser()
        package = parser.parse_source(source)

        # Should have 2 inheritance relationships
        inheritance_rels = [
            r for r in package.relationships if r.type == RelationshipType.INHERITANCE
        ]
        assert len(inheritance_rels) == 2


class TestCompositionInference:
    """Test composition relationship detection."""

    def test_composition_simple(self):
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

        # Check composition relationship
        composition_rels = [
            r for r in package.relationships if r.type == RelationshipType.COMPOSITION
        ]
        assert len(composition_rels) == 1

        rel = composition_rels[0]
        class_map = {cls.id: cls.name for cls in package.classes}
        assert class_map[rel.source_id] == "Car"
        assert class_map[rel.target_id] == "Engine"

    def test_composition_multiple(self):
        """Test class with multiple composed parts."""
        source = """
class Engine:
    pass

class Wheels:
    pass

class Car:
    def __init__(self):
        self.engine: Engine = Engine()
        self.wheels: Wheels = Wheels()
"""
        parser = PythonParser()
        package = parser.parse_source(source)

        composition_rels = [
            r for r in package.relationships if r.type == RelationshipType.COMPOSITION
        ]
        assert len(composition_rels) == 2


class TestAggregationInference:
    """Test aggregation relationship detection."""

    def test_aggregation_optional(self):
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

        # Check aggregation relationship (Optional indicates shared, not owned)
        aggregation_rels = [
            r for r in package.relationships if r.type == RelationshipType.AGGREGATION
        ]
        assert len(aggregation_rels) == 1

        rel = aggregation_rels[0]
        class_map = {cls.id: cls.name for cls in package.classes}
        assert class_map[rel.source_id] == "Employee"
        assert class_map[rel.target_id] == "Department"

    def test_aggregation_list(self):
        """Test aggregation with List type."""
        source = """
from typing import List

class Student:
    pass

class Course:
    def __init__(self):
        self.students: List[Student] = []
"""
        parser = PythonParser()
        package = parser.parse_source(source)

        # List indicates collection/aggregation
        aggregation_rels = [
            r for r in package.relationships if r.type == RelationshipType.AGGREGATION
        ]
        assert len(aggregation_rels) == 1

        rel = aggregation_rels[0]
        class_map = {cls.id: cls.name for cls in package.classes}
        assert class_map[rel.source_id] == "Course"
        assert class_map[rel.target_id] == "Student"


class TestDependencyInference:
    """Test dependency relationship detection."""

    def test_dependency_method_parameter(self):
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

        # Check dependency relationship
        dependency_rels = [
            r for r in package.relationships if r.type == RelationshipType.DEPENDENCY
        ]
        assert len(dependency_rels) == 1

        rel = dependency_rels[0]
        class_map = {cls.id: cls.name for cls in package.classes}
        assert class_map[rel.source_id] == "OrderProcessor"
        assert class_map[rel.target_id] == "Order"

    def test_dependency_return_type(self):
        """Test dependency from return type."""
        source = """
class Customer:
    pass

class CustomerFactory:
    def create_customer(self) -> Customer:
        return Customer()
"""
        parser = PythonParser()
        package = parser.parse_source(source)

        dependency_rels = [
            r for r in package.relationships if r.type == RelationshipType.DEPENDENCY
        ]
        assert len(dependency_rels) == 1

    def test_no_dependency_for_attributes(self):
        """Test that attributes don't create dependencies (they create composition/aggregation)."""
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

        # Should have composition (from attribute), not dependency
        composition_rels = [
            r for r in package.relationships if r.type == RelationshipType.COMPOSITION
        ]
        assert len(composition_rels) == 1

        # Should NOT have dependency for Engine (already an attribute)
        dependency_rels = [
            r for r in package.relationships if r.type == RelationshipType.DEPENDENCY
        ]
        assert len(dependency_rels) == 0

    def test_dependency_multiple_uses(self):
        """Test class using multiple other classes."""
        source = """
class Order:
    pass

class Customer:
    pass

class Payment:
    pass

class CheckoutService:
    def process_checkout(self, order: Order, customer: Customer) -> Payment:
        return Payment()
"""
        parser = PythonParser()
        package = parser.parse_source(source)

        dependency_rels = [
            r for r in package.relationships if r.type == RelationshipType.DEPENDENCY
        ]
        # Should have 3 dependencies: Order, Customer, Payment
        assert len(dependency_rels) == 3


class TestComplexScenarios:
    """Test complex relationship scenarios."""

    def test_mixed_relationships(self):
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
        self.home_address: Address = Address()  # Composition
        self.department: Optional[Department] = dept  # Aggregation

    def assign_project(self, project: Project) -> None:  # Dependency
        pass
"""
        parser = PythonParser()
        package = parser.parse_source(source)

        # Count relationship types
        composition = [r for r in package.relationships if r.type == RelationshipType.COMPOSITION]
        aggregation = [r for r in package.relationships if r.type == RelationshipType.AGGREGATION]
        dependency = [r for r in package.relationships if r.type == RelationshipType.DEPENDENCY]

        assert len(composition) == 1  # Address
        assert len(aggregation) == 1  # Department
        assert len(dependency) == 1  # Project

    def test_external_class_ignored(self):
        """Test that relationships to external classes are not created."""
        source = """
from datetime import datetime

class Event:
    def __init__(self):
        self.timestamp: datetime = datetime.now()  # External class, no relationship
"""
        parser = PythonParser()
        package = parser.parse_source(source)

        # Should have no relationships (datetime is external)
        assert len(package.relationships) == 0

    def test_nested_generic_types(self):
        """Test relationships with nested generic types."""
        source = """
from typing import List, Dict

class Task:
    pass

class Project:
    def __init__(self):
        self.tasks: List[Task] = []
"""
        parser = PythonParser()
        package = parser.parse_source(source)

        # Should extract Task from List[Task]
        aggregation = [r for r in package.relationships if r.type == RelationshipType.AGGREGATION]
        assert len(aggregation) == 1

        rel = aggregation[0]
        class_map = {cls.id: cls.name for cls in package.classes}
        assert class_map[rel.target_id] == "Task"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
