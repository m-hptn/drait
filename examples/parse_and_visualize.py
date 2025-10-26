"""
Example: Parse Python code and visualize as UML diagram.

This example demonstrates the complete workflow:
1. Parse Python source code
2. Extract metamodel
3. Export to PlantUML
4. Visualize the diagram
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from drait.parsers.python_parser import PythonParser, parse_file_to_project
from drait.exporters.plantuml import PlantUMLExporter


# Sample Python code to parse
SAMPLE_CODE = '''
class Person:
    """Represents a person with basic information."""

    def __init__(self, name: str, age: int):
        """Initialize a person."""
        self.name = name
        self.age = age
        self._id = 0

    def greet(self) -> str:
        """Return a greeting message."""
        return f"Hello, I'm {self.name}"

    def celebrate_birthday(self):
        """Increment age by 1."""
        self.age += 1


class Employee(Person):
    """An employee with additional work-related information."""

    company_name = "ACME Corp"  # Class variable

    def __init__(self, name: str, age: int, employee_id: str):
        """Initialize an employee."""
        super().__init__(name, age)
        self.employee_id = employee_id
        self.__salary = 0.0  # Private attribute

    def get_info(self) -> str:
        """Get employee information."""
        return f"{self.name} (ID: {self.employee_id})"

    @staticmethod
    def get_company() -> str:
        """Get company name."""
        return Employee.company_name

    @classmethod
    def create_intern(cls, name: str, age: int):
        """Factory method for creating an intern."""
        return cls(name, age, "INTERN")
'''


def main():
    """Main function demonstrating parse and visualize workflow."""
    print("=" * 70)
    print("DRAIT: Parse Python Code and Visualize")
    print("=" * 70)

    # Parse the sample code
    print("\n1. Parsing Python code...")
    parser = PythonParser()
    package = parser.parse_source(SAMPLE_CODE, "sample.py")

    print(f"   ✓ Found {len(package.classes)} classes")
    for cls in package.classes:
        print(f"     - {cls.name}")
        print(f"       • {len(cls.attributes)} attributes")
        print(f"       • {len(cls.methods)} methods")
        if cls.base_classes:
            print(f"       • Inherits from: {', '.join(cls.base_classes)}")

    # Create project from package
    from drait.metamodel import Project
    project = Project(
        name="SampleProject",
        packages=[package],
    )

    # Export to PlantUML
    print("\n2. Exporting to PlantUML...")
    exporter = PlantUMLExporter()
    plantuml_content = exporter.export_project(project)

    # Save to file
    output_file = Path(__file__).parent / "parsed_sample.puml"
    with open(output_file, 'w') as f:
        f.write(plantuml_content)

    print(f"   ✓ Saved to: {output_file}")

    # Display the PlantUML content
    print("\n3. Generated PlantUML diagram:")
    print("=" * 70)
    print(plantuml_content)
    print("=" * 70)

    print("\n4. To visualize:")
    print(f"   • Paste into: https://www.plantuml.com/plantuml/uml/")
    print(f"   • Or run: plantuml {output_file}")

    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print(f"  Classes parsed: {len(package.classes)}")
    print(f"  Total attributes: {sum(len(c.attributes) for c in package.classes)}")
    print(f"  Total methods: {sum(len(c.methods) for c in package.classes)}")
    print(f"  Inheritance relationships: {sum(1 for c in package.classes if c.base_classes)}")
    print("=" * 70)

    print("\n✓ Complete! You can now parse any Python file and visualize it!")


def parse_file_example():
    """Example of parsing an actual Python file."""
    print("\n" + "=" * 70)
    print("Bonus: Parse the metamodel itself!")
    print("=" * 70)

    # Parse the metamodel file
    metamodel_file = Path(__file__).parent.parent / "src" / "drait" / "metamodel.py"

    if metamodel_file.exists():
        print(f"\nParsing: {metamodel_file}")
        project = parse_file_to_project(str(metamodel_file), "DRAIT Metamodel")

        print(f"\nFound {len(project.packages[0].classes)} classes in metamodel:")
        for cls in project.packages[0].classes[:5]:  # Show first 5
            print(f"  • {cls.name}")

        # Export to PlantUML
        exporter = PlantUMLExporter()
        plantuml_content = exporter.export_project(project)

        output_file = Path(__file__).parent / "metamodel_diagram.puml"
        with open(output_file, 'w') as f:
            f.write(plantuml_content)

        print(f"\n✓ Metamodel diagram saved to: {output_file}")
        print(f"  This shows the structure of DRAIT itself!")


if __name__ == "__main__":
    main()
    parse_file_example()
