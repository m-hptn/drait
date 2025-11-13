"""
Example: Export metamodel to PlantUML

This example demonstrates how to export a DRAIT metamodel to PlantUML format
for visualization.
"""

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
    Position,
    Visibility,
    RelationshipType,
    Multiplicity,
)
from drait.exporters.plantuml import PlantUMLExporter, export_to_file


def create_example_model() -> Project:
    """Create a more comprehensive example model."""

    # Create Person class
    person_class = Class(
        name="Person",
        docstring="Represents a person",
        is_abstract=True,
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
            Attribute(
                name="_id",
                type=TypeReference(name="int"),
                visibility=Visibility.PROTECTED,
            ),
        ],
        methods=[
            Method(
                name="__init__",
                parameters=[
                    Parameter(name="name", type=TypeReference(name="str")),
                    Parameter(name="age", type=TypeReference(name="int")),
                ],
                visibility=Visibility.PUBLIC,
            ),
            Method(
                name="get_info",
                return_type=TypeReference(name="str"),
                visibility=Visibility.PUBLIC,
                is_abstract=True,
            ),
        ],
    )

    # Create Employee class (inherits from Person)
    employee_class = Class(
        name="Employee",
        docstring="An employee",
        base_classes=["Person"],
        attributes=[
            Attribute(
                name="employee_id",
                type=TypeReference(name="str"),
                visibility=Visibility.PUBLIC,
            ),
            Attribute(
                name="salary",
                type=TypeReference(name="float"),
                visibility=Visibility.PRIVATE,
            ),
        ],
        methods=[
            Method(
                name="get_info",
                return_type=TypeReference(name="str"),
                visibility=Visibility.PUBLIC,
            ),
            Method(
                name="calculate_bonus",
                return_type=TypeReference(name="float"),
                visibility=Visibility.PUBLIC,
            ),
        ],
    )

    # Create Department class
    department_class = Class(
        name="Department",
        docstring="A department containing employees",
        attributes=[
            Attribute(
                name="name",
                type=TypeReference(name="str"),
                visibility=Visibility.PUBLIC,
            ),
            Attribute(
                name="employees",
                type=TypeReference(
                    name="List",
                    module="typing",
                    type_arguments=[TypeReference(name="Employee")],
                ),
                visibility=Visibility.PUBLIC,
            ),
        ],
        methods=[
            Method(
                name="add_employee",
                parameters=[
                    Parameter(name="employee", type=TypeReference(name="Employee")),
                ],
                return_type=None,
                visibility=Visibility.PUBLIC,
            ),
            Method(
                name="get_total_salary",
                return_type=TypeReference(name="float"),
                visibility=Visibility.PUBLIC,
            ),
        ],
    )

    # Create relationships
    inheritance_rel = Relationship(
        type=RelationshipType.INHERITANCE,
        source_id=employee_class.id,
        target_id=person_class.id,
    )

    composition_rel = Relationship(
        type=RelationshipType.COMPOSITION,
        source_id=department_class.id,
        target_id=employee_class.id,
        source_role="department",
        target_role="employees",
        source_multiplicity=Multiplicity.ONE,
        target_multiplicity=Multiplicity.MANY,
    )

    # Create package
    package = Package(
        name="company",
        classes=[person_class, employee_class, department_class],
        relationships=[inheritance_rel, composition_rel],
        docstring="Company domain model",
    )

    # Create project
    project = Project(
        name="CompanyModel",
        version="1.0.0",
        packages=[package],
        metadata={
            "author": "DRAIT",
            "description": "Example company domain model",
        },
    )

    return project


def main():
    """Main function to demonstrate PlantUML export."""
    print("Creating example model...")
    project = create_example_model()

    print(f"\nProject: {project.name}")
    print(f"Classes: {sum(len(p.classes) for p in project.packages)}")
    print(f"Relationships: {sum(len(p.relationships) for p in project.packages)}")

    # Export to PlantUML
    print("\nExporting to PlantUML...")
    exporter = PlantUMLExporter()
    plantuml_content = exporter.export_project(project)

    # Save to file
    output_file = Path(__file__).parent / "company_model.puml"
    with open(output_file, 'w') as f:
        f.write(plantuml_content)

    print(f"\n✓ PlantUML diagram saved to: {output_file}")
    print("\nTo view the diagram:")
    print(f"  1. Install PlantUML: https://plantuml.com/download")
    print(f"  2. Run: plantuml {output_file}")
    print(f"  3. Or paste content into: https://www.plantuml.com/plantuml/uml/")
    print("\nPlantUML content preview:")
    print("=" * 60)
    print(plantuml_content)
    print("=" * 60)


if __name__ == "__main__":
    main()
