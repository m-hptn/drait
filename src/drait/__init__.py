"""
DRAIT - Model-Driven Development Tool

Diagram Real-time Architecture Interaction Tool
"""

__version__ = "0.1.0"
__author__ = "DRAIT Development Team"

from .metamodel import (
    Project,
    Package,
    Class,
    Attribute,
    Method,
    Parameter,
    Relationship,
    TypeReference,
    Decorator,
    Import,
    Position,
    Visibility,
    RelationshipType,
    ParameterKind,
    Multiplicity,
)

__all__ = [
    "Project",
    "Package",
    "Class",
    "Attribute",
    "Method",
    "Parameter",
    "Relationship",
    "TypeReference",
    "Decorator",
    "Import",
    "Position",
    "Visibility",
    "RelationshipType",
    "ParameterKind",
    "Multiplicity",
]
