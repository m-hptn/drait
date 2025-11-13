"""
Core metamodel for DRAIT - defines the abstract representation of class diagrams.

This module contains all metamodel classes that represent UML class diagrams
and their mapping to Python code.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


# Enumerations

class Visibility(str, Enum):
    """Visibility levels for class members."""
    PUBLIC = "public"       # No underscore
    PROTECTED = "protected"  # Single underscore _
    PRIVATE = "private"     # Double underscore __


class RelationshipType(str, Enum):
    """Types of relationships between classes."""
    INHERITANCE = "inheritance"
    ASSOCIATION = "association"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"
    DEPENDENCY = "dependency"
    REALIZATION = "realization"  # Interface implementation


class ParameterKind(str, Enum):
    """Kind of method parameters."""
    POSITIONAL = "positional"
    KEYWORD = "keyword"
    VAR_POSITIONAL = "var_positional"  # *args
    VAR_KEYWORD = "var_keyword"        # **kwargs


class Multiplicity(str, Enum):
    """Multiplicity/cardinality for relationships."""
    ZERO_TO_ONE = "0..1"
    ONE = "1"
    ZERO_TO_MANY = "0..*"
    ONE_TO_MANY = "1..*"
    MANY = "*"


# Supporting Types

@dataclass
class Position:
    """Position and size information for diagram elements."""
    x: float
    y: float
    width: Optional[float] = None
    height: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Position":
        """Create from dictionary."""
        return cls(
            x=data["x"],
            y=data["y"],
            width=data.get("width"),
            height=data.get("height"),
        )


@dataclass
class Import:
    """Represents a Python import statement."""
    module: str
    symbols: List[str] = field(default_factory=list)
    alias: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "module": self.module,
            "symbols": self.symbols,
            "alias": self.alias,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Import":
        """Create from dictionary."""
        return cls(
            module=data["module"],
            symbols=data.get("symbols", []),
            alias=data.get("alias"),
        )


@dataclass
class TypeReference:
    """
    Represents type information with support for generics and unions.

    Examples:
        - str: TypeReference(name="str")
        - List[str]: TypeReference(name="List", module="typing", type_arguments=[TypeReference(name="str")])
        - Optional[int]: TypeReference(name="int", is_optional=True)
    """
    name: str
    module: Optional[str] = None
    type_arguments: List["TypeReference"] = field(default_factory=list)
    is_optional: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "module": self.module,
            "type_arguments": [arg.to_dict() for arg in self.type_arguments],
            "is_optional": self.is_optional,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TypeReference":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            module=data.get("module"),
            type_arguments=[
                cls.from_dict(arg) for arg in data.get("type_arguments", [])
            ],
            is_optional=data.get("is_optional", False),
        )

    def __str__(self) -> str:
        """String representation of the type."""
        if self.type_arguments:
            args_str = ", ".join(str(arg) for arg in self.type_arguments)
            base = f"{self.name}[{args_str}]"
        else:
            base = self.name

        if self.is_optional:
            return f"Optional[{base}]"
        return base


@dataclass
class Decorator:
    """Represents a Python decorator."""
    name: str
    module: Optional[str] = None
    arguments: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "module": self.module,
            "arguments": self.arguments,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Decorator":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            module=data.get("module"),
            arguments=data.get("arguments", {}),
        )


# Core Entities

@dataclass
class Parameter:
    """Represents a method parameter."""
    name: str
    type: Optional[TypeReference] = None
    default_value: Optional[str] = None
    kind: ParameterKind = ParameterKind.POSITIONAL

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "type": self.type.to_dict() if self.type else None,
            "default_value": self.default_value,
            "kind": self.kind.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Parameter":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            type=TypeReference.from_dict(data["type"]) if data.get("type") else None,
            default_value=data.get("default_value"),
            kind=ParameterKind(data.get("kind", "positional")),
        )


@dataclass
class Attribute:
    """Represents a class attribute/field."""
    name: str
    type: TypeReference
    id: UUID = field(default_factory=uuid4)
    visibility: Visibility = Visibility.PUBLIC
    default_value: Optional[str] = None
    is_static: bool = False
    is_readonly: bool = False
    decorators: List[Decorator] = field(default_factory=list)
    docstring: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.type.to_dict(),
            "visibility": self.visibility.value,
            "default_value": self.default_value,
            "is_static": self.is_static,
            "is_readonly": self.is_readonly,
            "decorators": [d.to_dict() for d in self.decorators],
            "docstring": self.docstring,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attribute":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            type=TypeReference.from_dict(data["type"]),
            visibility=Visibility(data.get("visibility", "public")),
            default_value=data.get("default_value"),
            is_static=data.get("is_static", False),
            is_readonly=data.get("is_readonly", False),
            decorators=[Decorator.from_dict(d) for d in data.get("decorators", [])],
            docstring=data.get("docstring"),
        )


@dataclass
class Method:
    """Represents a class method/function."""
    name: str
    id: UUID = field(default_factory=uuid4)
    parameters: List[Parameter] = field(default_factory=list)
    return_type: Optional[TypeReference] = None
    visibility: Visibility = Visibility.PUBLIC
    is_static: bool = False
    is_class_method: bool = False
    is_abstract: bool = False
    decorators: List[Decorator] = field(default_factory=list)
    docstring: Optional[str] = None
    body: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "parameters": [p.to_dict() for p in self.parameters],
            "return_type": self.return_type.to_dict() if self.return_type else None,
            "visibility": self.visibility.value,
            "is_static": self.is_static,
            "is_class_method": self.is_class_method,
            "is_abstract": self.is_abstract,
            "decorators": [d.to_dict() for d in self.decorators],
            "docstring": self.docstring,
            "body": self.body,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Method":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            parameters=[Parameter.from_dict(p) for p in data.get("parameters", [])],
            return_type=TypeReference.from_dict(data["return_type"]) if data.get("return_type") else None,
            visibility=Visibility(data.get("visibility", "public")),
            is_static=data.get("is_static", False),
            is_class_method=data.get("is_class_method", False),
            is_abstract=data.get("is_abstract", False),
            decorators=[Decorator.from_dict(d) for d in data.get("decorators", [])],
            docstring=data.get("docstring"),
            body=data.get("body"),
        )


@dataclass
class Class:
    """Represents a Python class with attributes, methods, and metadata."""
    name: str
    id: UUID = field(default_factory=uuid4)
    attributes: List[Attribute] = field(default_factory=list)
    methods: List[Method] = field(default_factory=list)
    decorators: List[Decorator] = field(default_factory=list)
    stereotypes: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    is_abstract: bool = False
    docstring: Optional[str] = None
    position: Optional[Position] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "attributes": [a.to_dict() for a in self.attributes],
            "methods": [m.to_dict() for m in self.methods],
            "decorators": [d.to_dict() for d in self.decorators],
            "stereotypes": self.stereotypes,
            "base_classes": self.base_classes,
            "is_abstract": self.is_abstract,
            "docstring": self.docstring,
            "position": self.position.to_dict() if self.position else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Class":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            attributes=[Attribute.from_dict(a) for a in data.get("attributes", [])],
            methods=[Method.from_dict(m) for m in data.get("methods", [])],
            decorators=[Decorator.from_dict(d) for d in data.get("decorators", [])],
            stereotypes=data.get("stereotypes", []),
            base_classes=data.get("base_classes", []),
            is_abstract=data.get("is_abstract", False),
            docstring=data.get("docstring"),
            position=Position.from_dict(data["position"]) if data.get("position") else None,
            metadata=data.get("metadata", {}),
        )


@dataclass
class Relationship:
    """Represents relationships between classes."""
    type: RelationshipType
    source_id: UUID
    target_id: UUID
    id: UUID = field(default_factory=uuid4)
    source_role: Optional[str] = None
    target_role: Optional[str] = None
    source_multiplicity: Optional[Multiplicity] = None
    target_multiplicity: Optional[Multiplicity] = None
    is_navigable_from_source: bool = True
    is_navigable_from_target: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "type": self.type.value,
            "source_id": str(self.source_id),
            "target_id": str(self.target_id),
            "source_role": self.source_role,
            "target_role": self.target_role,
            "source_multiplicity": self.source_multiplicity.value if self.source_multiplicity else None,
            "target_multiplicity": self.target_multiplicity.value if self.target_multiplicity else None,
            "is_navigable_from_source": self.is_navigable_from_source,
            "is_navigable_from_target": self.is_navigable_from_target,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relationship":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]),
            type=RelationshipType(data["type"]),
            source_id=UUID(data["source_id"]),
            target_id=UUID(data["target_id"]),
            source_role=data.get("source_role"),
            target_role=data.get("target_role"),
            source_multiplicity=Multiplicity(data["source_multiplicity"]) if data.get("source_multiplicity") else None,
            target_multiplicity=Multiplicity(data["target_multiplicity"]) if data.get("target_multiplicity") else None,
            is_navigable_from_source=data.get("is_navigable_from_source", True),
            is_navigable_from_target=data.get("is_navigable_from_target", True),
        )


@dataclass
class Package:
    """Represents a Python package/module containing classes."""
    name: str
    id: UUID = field(default_factory=uuid4)
    classes: List[Class] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    imports: List[Import] = field(default_factory=list)
    docstring: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "classes": [c.to_dict() for c in self.classes],
            "relationships": [r.to_dict() for r in self.relationships],
            "imports": [i.to_dict() for i in self.imports],
            "docstring": self.docstring,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Package":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            classes=[Class.from_dict(c) for c in data.get("classes", [])],
            relationships=[Relationship.from_dict(r) for r in data.get("relationships", [])],
            imports=[Import.from_dict(i) for i in data.get("imports", [])],
            docstring=data.get("docstring"),
        )


@dataclass
class Project:
    """Represents a complete software project with multiple packages and diagrams."""
    name: str
    id: UUID = field(default_factory=uuid4)
    version: str = "1.0.0"
    packages: List[Package] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "version": self.version,
            "packages": [p.to_dict() for p in self.packages],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            version=data.get("version", "1.0.0"),
            packages=[Package.from_dict(p) for p in data.get("packages", [])],
            metadata=data.get("metadata", {}),
        )
