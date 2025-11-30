"""
Unit tests for the DRAIT metamodel.

Tests cover:
- Creation of metamodel objects
- JSON serialization/deserialization
- Type references with generics
- Relationships between classes
- Data integrity and validation
"""

import sys
from pathlib import Path
from uuid import UUID

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from drait.metamodel import (
    Attribute,
    Class,
    Decorator,
    Method,
    Multiplicity,
    Package,
    Parameter,
    ParameterKind,
    Position,
    Project,
    Relationship,
    RelationshipType,
    TypeReference,
    Visibility,
)


class TestTypeReference:
    """Test TypeReference functionality."""

    @pytest.mark.unit
    def test_simple_type(self):
        """Test simple type reference."""
        type_ref = TypeReference(name="str")
        assert type_ref.name == "str"
        assert type_ref.module is None
        assert type_ref.is_optional is False
        assert str(type_ref) == "str"

    @pytest.mark.unit
    def test_optional_type(self):
        """Test optional type reference."""
        type_ref = TypeReference(name="int", is_optional=True)
        assert str(type_ref) == "int | None"

    @pytest.mark.unit
    def test_generic_type(self):
        """Test generic type with type arguments."""
        type_ref = TypeReference(
            name="List",
            module="typing",
            type_arguments=[TypeReference(name="str")],
        )
        assert str(type_ref) == "List[str]"

    @pytest.mark.unit
    def test_nested_generic_type(self):
        """Test nested generic types."""
        type_ref = TypeReference(
            name="Dict",
            module="typing",
            type_arguments=[
                TypeReference(name="str"),
                TypeReference(
                    name="List",
                    module="typing",
                    type_arguments=[TypeReference(name="int")],
                ),
            ],
        )
        assert str(type_ref) == "Dict[str, List[int]]"

    @pytest.mark.unit
    def test_type_serialization(self):
        """Test TypeReference serialization and deserialization."""
        type_ref = TypeReference(
            name="List",
            module="typing",
            type_arguments=[TypeReference(name="str")],
            is_optional=True,
        )

        # Serialize
        data = type_ref.to_dict()
        assert data["name"] == "List"
        assert data["module"] == "typing"
        assert data["is_optional"] is True
        assert len(data["type_arguments"]) == 1

        # Deserialize
        loaded = TypeReference.from_dict(data)
        assert loaded.name == type_ref.name
        assert loaded.module == type_ref.module
        assert loaded.is_optional == type_ref.is_optional
        assert str(loaded) == str(type_ref)


class TestPosition:
    """Test Position functionality."""

    @pytest.mark.unit
    def test_position_creation(self):
        """Test creating a position."""
        pos = Position(x=100.0, y=200.0, width=150.0, height=100.0)
        assert pos.x == 100.0
        assert pos.y == 200.0
        assert pos.width == 150.0
        assert pos.height == 100.0

    @pytest.mark.unit
    def test_position_serialization(self):
        """Test Position serialization and deserialization."""
        pos = Position(x=50.0, y=75.0)
        data = pos.to_dict()

        loaded = Position.from_dict(data)
        assert loaded.x == pos.x
        assert loaded.y == pos.y
        assert loaded.width == pos.width
        assert loaded.height == pos.height


class TestDecorator:
    """Test Decorator functionality."""

    @pytest.mark.unit
    def test_simple_decorator(self):
        """Test simple decorator without arguments."""
        dec = Decorator(name="property")
        assert dec.name == "property"
        assert dec.module is None
        assert dec.arguments == {}

    @pytest.mark.unit
    def test_decorator_with_module(self):
        """Test decorator with module."""
        dec = Decorator(name="dataclass", module="dataclasses")
        assert dec.name == "dataclass"
        assert dec.module == "dataclasses"

    @pytest.mark.unit
    def test_decorator_serialization(self):
        """Test Decorator serialization."""
        dec = Decorator(
            name="validator",
            arguments={"field": "name", "check": "not_empty"},
        )
        data = dec.to_dict()
        loaded = Decorator.from_dict(data)

        assert loaded.name == dec.name
        assert loaded.arguments == dec.arguments


class TestParameter:
    """Test Parameter functionality."""

    @pytest.mark.unit
    def test_parameter_creation(self):
        """Test creating a parameter."""
        param = Parameter(
            name="username",
            type=TypeReference(name="str"),
            kind=ParameterKind.POSITIONAL,
        )
        assert param.name == "username"
        assert param.type.name == "str"
        assert param.default_value is None

    @pytest.mark.unit
    def test_parameter_with_default(self):
        """Test parameter with default value."""
        param = Parameter(
            name="age",
            type=TypeReference(name="int"),
            default_value="0",
            kind=ParameterKind.KEYWORD,
        )
        assert param.default_value == "0"

    @pytest.mark.unit
    def test_parameter_serialization(self):
        """Test Parameter serialization."""
        param = Parameter(
            name="count",
            type=TypeReference(name="int"),
            default_value="10",
        )
        data = param.to_dict()
        loaded = Parameter.from_dict(data)

        assert loaded.name == param.name
        assert loaded.type.name == param.type.name
        assert loaded.default_value == param.default_value


class TestAttribute:
    """Test Attribute functionality."""

    @pytest.mark.unit
    def test_attribute_creation(self):
        """Test creating an attribute."""
        attr = Attribute(
            name="username",
            type=TypeReference(name="str"),
            visibility=Visibility.PUBLIC,
            docstring="User's username",
        )
        assert attr.name == "username"
        assert attr.type.name == "str"
        assert attr.visibility == Visibility.PUBLIC
        assert attr.is_static is False

    @pytest.mark.unit
    def test_protected_attribute(self):
        """Test protected attribute."""
        attr = Attribute(
            name="_password",
            type=TypeReference(name="str"),
            visibility=Visibility.PROTECTED,
        )
        assert attr.visibility == Visibility.PROTECTED

    @pytest.mark.unit
    def test_attribute_with_default(self):
        """Test attribute with default value."""
        attr = Attribute(
            name="count",
            type=TypeReference(name="int"),
            default_value="0",
        )
        assert attr.default_value == "0"

    @pytest.mark.unit
    def test_attribute_serialization(self):
        """Test Attribute serialization."""
        attr = Attribute(
            name="email",
            type=TypeReference(name="str"),
            visibility=Visibility.PUBLIC,
            docstring="Email address",
        )
        data = attr.to_dict()

        # Check UUID is serialized as string
        assert isinstance(data["id"], str)
        UUID(data["id"])  # Should not raise

        loaded = Attribute.from_dict(data)
        assert loaded.name == attr.name
        assert loaded.type.name == attr.type.name
        assert loaded.visibility == attr.visibility
        assert loaded.docstring == attr.docstring
        assert loaded.id == attr.id


class TestMethod:
    """Test Method functionality."""

    @pytest.mark.unit
    def test_method_creation(self):
        """Test creating a method."""
        method = Method(
            name="greet",
            return_type=TypeReference(name="str"),
            docstring="Return greeting message",
        )
        assert method.name == "greet"
        assert method.return_type.name == "str"
        assert len(method.parameters) == 0

    @pytest.mark.unit
    def test_method_with_parameters(self):
        """Test method with parameters."""
        method = Method(
            name="authenticate",
            parameters=[
                Parameter(name="password", type=TypeReference(name="str")),
            ],
            return_type=TypeReference(name="bool"),
        )
        assert len(method.parameters) == 1
        assert method.parameters[0].name == "password"

    @pytest.mark.unit
    def test_static_method(self):
        """Test static method."""
        method = Method(
            name="create_default",
            is_static=True,
            return_type=TypeReference(name="User"),
        )
        assert method.is_static is True
        assert method.is_class_method is False

    @pytest.mark.unit
    def test_abstract_method(self):
        """Test abstract method."""
        method = Method(
            name="process",
            is_abstract=True,
        )
        assert method.is_abstract is True

    @pytest.mark.unit
    def test_method_serialization(self):
        """Test Method serialization."""
        method = Method(
            name="calculate",
            parameters=[
                Parameter(name="x", type=TypeReference(name="int")),
                Parameter(name="y", type=TypeReference(name="int")),
            ],
            return_type=TypeReference(name="int"),
            visibility=Visibility.PUBLIC,
        )
        data = method.to_dict()
        loaded = Method.from_dict(data)

        assert loaded.name == method.name
        assert loaded.id == method.id
        assert len(loaded.parameters) == 2
        assert loaded.return_type.name == "int"


class TestClass:
    """Test Class functionality."""

    @pytest.mark.unit
    def test_class_creation(self):
        """Test creating a class."""
        cls = Class(
            name="Person",
            docstring="Represents a person",
        )
        assert cls.name == "Person"
        assert len(cls.attributes) == 0
        assert len(cls.methods) == 0
        assert cls.is_abstract is False

    @pytest.mark.unit
    def test_class_with_attributes(self):
        """Test class with attributes."""
        cls = Class(
            name="User",
            attributes=[
                Attribute(name="username", type=TypeReference(name="str")),
                Attribute(name="email", type=TypeReference(name="str")),
            ],
        )
        assert len(cls.attributes) == 2
        assert cls.attributes[0].name == "username"

    @pytest.mark.unit
    def test_class_with_inheritance(self):
        """Test class with base classes."""
        cls = Class(
            name="Admin",
            base_classes=["User"],
        )
        assert "User" in cls.base_classes

    @pytest.mark.unit
    def test_abstract_class(self):
        """Test abstract class."""
        cls = Class(
            name="BaseHandler",
            is_abstract=True,
            methods=[
                Method(name="handle", is_abstract=True),
            ],
        )
        assert cls.is_abstract is True
        assert cls.methods[0].is_abstract is True

    @pytest.mark.unit
    def test_class_with_position(self):
        """Test class with diagram position."""
        cls = Class(
            name="Entity",
            position=Position(x=100.0, y=200.0),
        )
        assert cls.position is not None
        assert cls.position.x == 100.0

    @pytest.mark.unit
    def test_class_serialization(self):
        """Test Class serialization."""
        cls = Class(
            name="Person",
            attributes=[
                Attribute(name="name", type=TypeReference(name="str")),
            ],
            methods=[
                Method(name="greet", return_type=TypeReference(name="str")),
            ],
            docstring="A person class",
        )
        data = cls.to_dict()
        loaded = Class.from_dict(data)

        assert loaded.name == cls.name
        assert loaded.id == cls.id
        assert len(loaded.attributes) == 1
        assert len(loaded.methods) == 1
        assert loaded.docstring == cls.docstring


class TestRelationship:
    """Test Relationship functionality."""

    @pytest.mark.unit
    def test_inheritance_relationship(self):
        """Test inheritance relationship."""
        parent = Class(name="Parent")
        child = Class(name="Child")

        rel = Relationship(
            type=RelationshipType.INHERITANCE,
            source_id=child.id,
            target_id=parent.id,
        )
        assert rel.type == RelationshipType.INHERITANCE
        assert rel.source_id == child.id
        assert rel.target_id == parent.id

    @pytest.mark.unit
    def test_association_with_multiplicity(self):
        """Test association with multiplicity."""
        user = Class(name="User")
        role = Class(name="Role")

        rel = Relationship(
            type=RelationshipType.ASSOCIATION,
            source_id=user.id,
            target_id=role.id,
            source_multiplicity=Multiplicity.ONE,
            target_multiplicity=Multiplicity.MANY,
        )
        assert rel.source_multiplicity == Multiplicity.ONE
        assert rel.target_multiplicity == Multiplicity.MANY

    @pytest.mark.unit
    def test_relationship_serialization(self):
        """Test Relationship serialization."""
        cls1 = Class(name="Class1")
        cls2 = Class(name="Class2")

        rel = Relationship(
            type=RelationshipType.COMPOSITION,
            source_id=cls1.id,
            target_id=cls2.id,
            source_role="container",
            target_role="contained",
        )
        data = rel.to_dict()
        loaded = Relationship.from_dict(data)

        assert loaded.type == rel.type
        assert loaded.source_id == rel.source_id
        assert loaded.target_id == rel.target_id
        assert loaded.source_role == rel.source_role


class TestPackage:
    """Test Package functionality."""

    @pytest.mark.unit
    def test_package_creation(self):
        """Test creating a package."""
        pkg = Package(
            name="models.user",
            docstring="User models",
        )
        assert pkg.name == "models.user"
        assert len(pkg.classes) == 0
        assert len(pkg.relationships) == 0

    @pytest.mark.unit
    def test_package_with_classes(self):
        """Test package with classes."""
        cls1 = Class(name="User")
        cls2 = Class(name="Role")

        pkg = Package(
            name="auth",
            classes=[cls1, cls2],
        )
        assert len(pkg.classes) == 2

    @pytest.mark.unit
    def test_package_serialization(self):
        """Test Package serialization."""
        cls = Class(name="Person")
        pkg = Package(
            name="models",
            classes=[cls],
            docstring="Domain models",
        )
        data = pkg.to_dict()
        loaded = Package.from_dict(data)

        assert loaded.name == pkg.name
        assert loaded.id == pkg.id
        assert len(loaded.classes) == 1
        assert loaded.classes[0].name == "Person"


class TestProject:
    """Test Project functionality."""

    @pytest.mark.unit
    def test_project_creation(self):
        """Test creating a project."""
        project = Project(
            name="MyProject",
            version="1.0.0",
        )
        assert project.name == "MyProject"
        assert project.version == "1.0.0"
        assert len(project.packages) == 0

    @pytest.mark.unit
    def test_project_with_packages(self):
        """Test project with packages."""
        pkg = Package(name="models")
        project = Project(
            name="App",
            packages=[pkg],
        )
        assert len(project.packages) == 1

    @pytest.mark.unit
    def test_project_serialization(self):
        """Test Project serialization."""
        cls = Class(name="User")
        pkg = Package(name="models", classes=[cls])
        project = Project(
            name="TestApp",
            version="1.0.0",
            packages=[pkg],
            metadata={"author": "Test Author"},
        )
        data = project.to_dict()
        loaded = Project.from_dict(data)

        assert loaded.name == project.name
        assert loaded.version == project.version
        assert loaded.id == project.id
        assert len(loaded.packages) == 1
        assert loaded.packages[0].classes[0].name == "User"
        assert loaded.metadata["author"] == "Test Author"


class TestCompleteModel:
    """Test complete model with all elements."""

    @pytest.mark.unit
    def test_complete_model_roundtrip(self):
        """Test creating, serializing, and deserializing a complete model."""
        # Create a complete class
        person_class = Class(
            name="Person",
            docstring="Person class",
            position=Position(x=100.0, y=100.0),
            attributes=[
                Attribute(
                    name="name",
                    type=TypeReference(name="str"),
                    visibility=Visibility.PUBLIC,
                ),
                Attribute(
                    name="age",
                    type=TypeReference(name="int"),
                    visibility=Visibility.PUBLIC,
                ),
            ],
            methods=[
                Method(
                    name="greet",
                    return_type=TypeReference(name="str"),
                    parameters=[],
                ),
            ],
        )

        # Create package
        package = Package(
            name="example",
            classes=[person_class],
        )

        # Create project
        project = Project(
            name="TestProject",
            version="1.0.0",
            packages=[package],
        )

        # Serialize
        data = project.to_dict()

        # Deserialize
        loaded_project = Project.from_dict(data)

        # Verify
        assert loaded_project.name == project.name
        assert loaded_project.version == project.version
        assert len(loaded_project.packages) == 1

        loaded_package = loaded_project.packages[0]
        assert loaded_package.name == package.name
        assert len(loaded_package.classes) == 1

        loaded_class = loaded_package.classes[0]
        assert loaded_class.name == person_class.name
        assert len(loaded_class.attributes) == 2
        assert len(loaded_class.methods) == 1
        assert loaded_class.position.x == 100.0

    @pytest.mark.unit
    def test_model_with_relationships(self):
        """Test model with class relationships."""
        parent = Class(name="Parent")
        child = Class(name="Child", base_classes=["Parent"])

        rel = Relationship(
            type=RelationshipType.INHERITANCE,
            source_id=child.id,
            target_id=parent.id,
        )

        package = Package(
            name="test",
            classes=[parent, child],
            relationships=[rel],
        )

        project = Project(name="Test", packages=[package])

        # Roundtrip
        data = project.to_dict()
        loaded = Project.from_dict(data)

        loaded_pkg = loaded.packages[0]
        assert len(loaded_pkg.classes) == 2
        assert len(loaded_pkg.relationships) == 1
        assert loaded_pkg.relationships[0].type == RelationshipType.INHERITANCE
