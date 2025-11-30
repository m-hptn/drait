"""
DRAIT - Model-Driven Development Tool

Diagram Real-time Architecture Interaction Tool
"""

__version__ = "0.1.0"
__author__ = "DRAIT Development Team"

# Metamodel
# Exporters
from .exporters.plantuml import PlantUMLExporter
from .metamodel import (
    Attribute,
    Class,
    Decorator,
    Import,
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

# Parser
from .parsers.python_parser import PythonParser, parse_file_to_project, parse_folder_to_project

__all__ = [
    # Metamodel
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
    # Parser
    "PythonParser",
    "parse_file_to_project",
    "parse_folder_to_project",
    # Exporters
    "PlantUMLExporter",
]
