"""
Parse relationships_example.py and generate PlantUML with all relationships.

This demonstrates Phase 3: Relationship Inference
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from drait.parsers.python_parser import parse_file_to_project
from drait.exporters.plantuml import PlantUMLExporter


def main():
    # Parse the relationships example
    example_file = Path(__file__).parent / "relationships_example.py"

    print("Parsing relationships_example.py...")
    project = parse_file_to_project(str(example_file), "RelationshipsExample")

    # Show what was found
    package = project.packages[0]
    print(f"\nFound {len(package.classes)} classes:")
    for cls in package.classes:
        print(f"  - {cls.name}")
        if cls.base_classes:
            print(f"    Base classes: {', '.join(cls.base_classes)}")

    # Create ID to name mapping
    id_to_name = {cls.id: cls.name for cls in package.classes}

    print(f"\nFound {len(package.relationships)} relationships:")
    for rel in package.relationships:
        source_name = id_to_name.get(rel.source_id, "Unknown")
        target_name = id_to_name.get(rel.target_id, "Unknown")
        role = rel.source_role or "relates to"
        print(f"  - {source_name} {rel.type.value} {target_name} ({role})")

    # Export to PlantUML
    exporter = PlantUMLExporter()
    plantuml_code = exporter.export_project(project)

    # Save to file
    output_file = Path(__file__).parent / "relationships.puml"
    output_file.write_text(plantuml_code)

    print(f"\nPlantUML diagram saved to: {output_file}")
    print("\nYou can visualize it at: https://www.plantuml.com/plantuml/uml/")
    print("\nRelationship Legend:")
    print("  <|--  : Inheritance")
    print("  *--   : Composition (strong ownership)")
    print("  o--   : Aggregation (weak ownership)")
    print("  ..>   : Dependency (uses)")

    print("\n" + "=" * 70)
    print("Expected relationships:")
    print("=" * 70)
    print("✓ Manager <|-- Employee (Inheritance)")
    print("✓ Car *-- Engine (Composition - Car owns Engine)")
    print("✓ Person o-- Department (Aggregation - Person has Department)")
    print("✓ OrderProcessor ..> Order (Dependency - uses in method)")
    print("✓ OrderProcessor ..> Customer (Dependency - uses in method)")
    print("✓ Company *-- Address (Composition - owns headquarters)")
    print("✓ Company o-- Employee (Aggregation - has employees list)")
    print("✓ Company ..> OrderProcessor (Dependency - uses in method)")


if __name__ == "__main__":
    main()
