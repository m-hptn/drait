"""
Example: Simple Class Diagram

This example demonstrates how to use the DRAIT metamodel to create
a simple class diagram - a Person class with basic attributes and methods.
This serves as a minimal example of the metamodel's capabilities.
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
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
    Decorator,
    Position,
    Visibility,
    RelationshipType,
    ParameterKind,
)


def create_simple_class_diagram() -> Project:
    """Create a simple class diagram with a Person class."""

    # Create a simple Person class
    person_class = Class(
        name="Person",
        docstring="Represents a person with basic information.",
        position=Position(x=100.0, y=100.0, width=200.0, height=150.0),
        attributes=[
            Attribute(
                name="name",
                type=TypeReference(name="str"),
                visibility=Visibility.PUBLIC,
                docstring="Person's name",
            ),
            Attribute(
                name="age",
                type=TypeReference(name="int"),
                visibility=Visibility.PUBLIC,
                docstring="Person's age",
            ),
        ],
        methods=[
            Method(
                name="__init__",
                parameters=[
                    Parameter(name="name", type=TypeReference(name="str")),
                    Parameter(name="age", type=TypeReference(name="int")),
                ],
                return_type=None,
                docstring="Initialize a new person.",
            ),
            Method(
                name="greet",
                parameters=[],
                return_type=TypeReference(name="str"),
                visibility=Visibility.PUBLIC,
                docstring="Return a greeting message.",
            ),
        ],
    )

    # Create package
    package = Package(
        name="example",
        classes=[person_class],
        relationships=[],
        docstring="Simple example package",
    )

    # Create project
    project = Project(
        name="SimpleExample",
        version="1.0.0",
        packages=[package],
        metadata={
            "author": "DRAIT Team",
            "description": "Simple class diagram example",
        },
    )

    return project


def main():
    """Main function to demonstrate the metamodel."""
    print("Creating simple class diagram...")
    project = create_simple_class_diagram()

    print(f"\nProject: {project.name} v{project.version}")
    print(f"Packages: {len(project.packages)}")

    for package in project.packages:
        print(f"\nPackage: {package.name}")
        print(f"  Classes: {len(package.classes)}")
        for cls in package.classes:
            print(f"    - {cls.name}")
            print(f"      Attributes: {', '.join(a.name for a in cls.attributes)}")
            print(f"      Methods: {', '.join(m.name for m in cls.methods)}")

    # Serialize to JSON
    print("\nSerializing to JSON...")
    json_data = project.to_dict()
    json_str = json.dumps(json_data, indent=2)

    # Save to file
    output_file = Path(__file__).parent / "simple_class_diagram.json"
    with open(output_file, "w") as f:
        f.write(json_str)

    print(f"Saved to: {output_file}")
    print(f"File size: {len(json_str)} bytes")

    # Demonstrate deserialization
    print("\nDeserializing from JSON...")
    loaded_project = Project.from_dict(json_data)
    print(f"Loaded project: {loaded_project.name}")
    print(f"Classes: {[c.name for c in loaded_project.packages[0].classes]}")

    print("\n✓ Metamodel example completed successfully!")


if __name__ == "__main__":
    main()
