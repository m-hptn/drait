"""
Unit tests for PlantUML exporter.

Tests cover:
- Class export with attributes and methods
- Relationship export
- Visibility formatting
- Type formatting
- Complete project export
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from drait.metamodel import (
    Project,
    Package,
    Class,
    Attribute,
    Method,
    Parameter,
    Relationship,
    TypeReference,
    Visibility,
    RelationshipType,
    Multiplicity,
)
from drait.exporters.plantuml import PlantUMLExporter


class TestPlantUMLExporter:
    """Test PlantUML exporter functionality."""

    @pytest.mark.unit
    def test_export_simple_class(self):
        """Test exporting a simple class."""
        cls = Class(
            name="Person",
            attributes=[
                Attribute(name="name", type=TypeReference(name="str")),
            ],
            methods=[
                Method(name="greet", return_type=TypeReference(name="str")),
            ],
        )

        exporter = PlantUMLExporter()
        lines = exporter.export_class(cls)
        content = "\n".join(lines)

        assert "class Person" in content
        assert "+ name : str" in content
        assert "+ greet() : str" in content

    @pytest.mark.unit
    def test_export_abstract_class(self):
        """Test exporting an abstract class."""
        cls = Class(
            name="BaseClass",
            is_abstract=True,
            methods=[
                Method(name="process", is_abstract=True),
            ],
        )

        exporter = PlantUMLExporter()
        lines = exporter.export_class(cls)
        content = "\n".join(lines)

        assert "abstract class BaseClass" in content
        assert "{abstract}" in content

    @pytest.mark.unit
    def test_visibility_symbols(self):
        """Test visibility symbol mapping."""
        cls = Class(
            name="TestClass",
            attributes=[
                Attribute(
                    name="public_attr",
                    type=TypeReference(name="str"),
                    visibility=Visibility.PUBLIC,
                ),
                Attribute(
                    name="protected_attr",
                    type=TypeReference(name="str"),
                    visibility=Visibility.PROTECTED,
                ),
                Attribute(
                    name="private_attr",
                    type=TypeReference(name="str"),
                    visibility=Visibility.PRIVATE,
                ),
            ],
        )

        exporter = PlantUMLExporter()
        lines = exporter.export_class(cls)
        content = "\n".join(lines)

        assert "+ public_attr" in content
        assert "# protected_attr" in content
        assert "- private_attr" in content

    @pytest.mark.unit
    def test_export_generic_types(self):
        """Test exporting generic type references."""
        cls = Class(
            name="Container",
            attributes=[
                Attribute(
                    name="items",
                    type=TypeReference(
                        name="List",
                        type_arguments=[TypeReference(name="str")],
                    ),
                ),
            ],
        )

        exporter = PlantUMLExporter()
        lines = exporter.export_class(cls)
        content = "\n".join(lines)

        assert "List[str]" in content

    @pytest.mark.unit
    def test_export_method_with_parameters(self):
        """Test exporting method with parameters."""
        method = Method(
            name="calculate",
            parameters=[
                Parameter(name="x", type=TypeReference(name="int")),
                Parameter(name="y", type=TypeReference(name="int"), default_value="0"),
            ],
            return_type=TypeReference(name="int"),
        )

        cls = Class(name="Math", methods=[method])

        exporter = PlantUMLExporter()
        lines = exporter.export_class(cls)
        content = "\n".join(lines)

        assert "calculate(" in content
        assert "x: int" in content
        assert "y: int = 0" in content
        assert ": int" in content  # return type

    @pytest.mark.unit
    def test_export_static_method(self):
        """Test exporting static method."""
        cls = Class(
            name="Utils",
            methods=[
                Method(name="helper", is_static=True),
            ],
        )

        exporter = PlantUMLExporter()
        lines = exporter.export_class(cls)
        content = "\n".join(lines)

        assert "{static}" in content

    @pytest.mark.unit
    def test_export_inheritance_relationship(self):
        """Test exporting inheritance relationship."""
        parent = Class(name="Parent")
        child = Class(name="Child")

        rel = Relationship(
            type=RelationshipType.INHERITANCE,
            source_id=child.id,
            target_id=parent.id,
        )

        exporter = PlantUMLExporter()
        line = exporter.export_relationship(rel, [parent, child])

        assert "Child" in line
        assert "<|--" in line
        assert "Parent" in line

    @pytest.mark.unit
    def test_export_composition_relationship(self):
        """Test exporting composition relationship."""
        container = Class(name="Container")
        item = Class(name="Item")

        rel = Relationship(
            type=RelationshipType.COMPOSITION,
            source_id=container.id,
            target_id=item.id,
            source_multiplicity=Multiplicity.ONE,
            target_multiplicity=Multiplicity.MANY,
        )

        exporter = PlantUMLExporter()
        line = exporter.export_relationship(rel, [container, item])

        assert "Container" in line
        assert "*--" in line
        assert "Item" in line
        assert '"1"' in line
        assert '"*"' in line

    @pytest.mark.unit
    def test_export_relationship_with_roles(self):
        """Test exporting relationship with role names."""
        dept = Class(name="Department")
        emp = Class(name="Employee")

        rel = Relationship(
            type=RelationshipType.ASSOCIATION,
            source_id=dept.id,
            target_id=emp.id,
            source_role="employer",
            target_role="employees",
        )

        exporter = PlantUMLExporter()
        line = exporter.export_relationship(rel, [dept, emp])

        assert "employer" in line
        assert "employees" in line

    @pytest.mark.unit
    def test_export_package(self):
        """Test exporting a package."""
        cls = Class(name="TestClass")
        package = Package(
            name="mypackage",
            classes=[cls],
        )

        exporter = PlantUMLExporter()
        lines = exporter.export_package(package)
        content = "\n".join(lines)

        assert "package mypackage" in content
        assert "class TestClass" in content

    @pytest.mark.unit
    def test_export_project(self):
        """Test exporting complete project."""
        cls = Class(name="Person")
        package = Package(name="models", classes=[cls])
        project = Project(
            name="TestProject",
            packages=[package],
        )

        exporter = PlantUMLExporter()
        content = exporter.export_project(project)

        assert "@startuml" in content
        assert "@enduml" in content
        assert "title TestProject" in content
        assert "class Person" in content

    @pytest.mark.unit
    def test_export_with_stereotypes(self):
        """Test exporting class with stereotypes."""
        cls = Class(
            name="Entity",
            stereotypes=["entity", "persistent"],
        )

        exporter = PlantUMLExporter()
        lines = exporter.export_class(cls)
        content = "\n".join(lines)

        assert "<<entity, persistent>>" in content

    @pytest.mark.unit
    def test_export_without_methods(self):
        """Test exporting with methods disabled."""
        cls = Class(
            name="DataClass",
            attributes=[
                Attribute(name="value", type=TypeReference(name="int")),
            ],
            methods=[
                Method(name="process"),
            ],
        )

        exporter = PlantUMLExporter(include_methods=False)
        lines = exporter.export_class(cls)
        content = "\n".join(lines)

        assert "+ value : int" in content
        assert "process" not in content

    @pytest.mark.unit
    def test_export_without_attributes(self):
        """Test exporting with attributes disabled."""
        cls = Class(
            name="Service",
            attributes=[
                Attribute(name="data", type=TypeReference(name="str")),
            ],
            methods=[
                Method(name="run"),
            ],
        )

        exporter = PlantUMLExporter(include_attributes=False)
        lines = exporter.export_class(cls)
        content = "\n".join(lines)

        assert "data" not in content
        assert "+ run()" in content

    @pytest.mark.unit
    def test_complete_model_export(self):
        """Test exporting a complete model with multiple elements."""
        # Create classes
        person = Class(
            name="Person",
            is_abstract=True,
            attributes=[
                Attribute(name="name", type=TypeReference(name="str")),
            ],
            methods=[
                Method(name="get_info", is_abstract=True),
            ],
        )

        employee = Class(
            name="Employee",
            base_classes=["Person"],
            attributes=[
                Attribute(name="employee_id", type=TypeReference(name="int")),
            ],
        )

        # Create relationship
        rel = Relationship(
            type=RelationshipType.INHERITANCE,
            source_id=employee.id,
            target_id=person.id,
        )

        # Create package and project
        package = Package(
            name="hr",
            classes=[person, employee],
            relationships=[rel],
        )

        project = Project(name="HRSystem", packages=[package])

        # Export
        exporter = PlantUMLExporter()
        content = exporter.export_project(project)

        # Verify all elements are present
        assert "@startuml" in content
        assert "title HRSystem" in content
        assert "abstract class Person" in content
        assert "class Employee" in content
        assert "Employee <|-- Person" in content
        assert "@enduml" in content


class TestPlantUMLFormatting:
    """Test PlantUML formatting helpers."""

    @pytest.mark.unit
    def test_format_simple_type(self):
        """Test formatting simple types."""
        exporter = PlantUMLExporter()
        type_ref = TypeReference(name="str")

        result = exporter._format_type(type_ref)
        assert result == "str"

    @pytest.mark.unit
    def test_format_optional_type(self):
        """Test formatting optional types."""
        exporter = PlantUMLExporter()
        type_ref = TypeReference(name="int", is_optional=True)

        result = exporter._format_type(type_ref)
        assert result == "Optional[int]"

    @pytest.mark.unit
    def test_format_nested_generic(self):
        """Test formatting nested generic types."""
        exporter = PlantUMLExporter()
        type_ref = TypeReference(
            name="Dict",
            type_arguments=[
                TypeReference(name="str"),
                TypeReference(
                    name="List",
                    type_arguments=[TypeReference(name="int")],
                ),
            ],
        )

        result = exporter._format_type(type_ref)
        assert result == "Dict[str, List[int]]"

    @pytest.mark.unit
    def test_relationship_arrow_types(self):
        """Test all relationship arrow mappings."""
        exporter = PlantUMLExporter()

        assert exporter._get_relationship_arrow(RelationshipType.INHERITANCE) == "<|--"
        assert exporter._get_relationship_arrow(RelationshipType.REALIZATION) == "<|.."
        assert exporter._get_relationship_arrow(RelationshipType.ASSOCIATION) == "-->"
        assert exporter._get_relationship_arrow(RelationshipType.AGGREGATION) == "o--"
        assert exporter._get_relationship_arrow(RelationshipType.COMPOSITION) == "*--"
        assert exporter._get_relationship_arrow(RelationshipType.DEPENDENCY) == "..>"
