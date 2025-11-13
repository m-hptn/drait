"""
Parse advanced_features_example.py and demonstrate Phase 4 features.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from drait.parsers.python_parser import parse_file_to_project
from drait.exporters.plantuml import PlantUMLExporter


def main():
    # Parse the advanced features example
    example_file = Path(__file__).parent / "advanced_features_example.py"

    print("Parsing advanced_features_example.py...")
    print("=" * 70)
    project = parse_file_to_project(str(example_file), "AdvancedFeaturesExample")

    package = project.packages[0]
    print(f"\nFound {len(package.classes)} classes\n")

    # Show abstract classes
    print("Abstract Classes:")
    print("-" * 70)
    for cls in package.classes:
        if cls.is_abstract:
            print(f"  ✓ {cls.name} (is_abstract=True)")
            if cls.decorators:
                print(f"    Decorators: {', '.join(f'@{d.name}' for d in cls.decorators)}")
            # Show abstract methods
            abstract_methods = [m for m in cls.methods if m.is_abstract]
            if abstract_methods:
                print(f"    Abstract methods: {', '.join(m.name for m in abstract_methods)}")

    # Show classes with decorators
    print("\nClasses with Decorators:")
    print("-" * 70)
    for cls in package.classes:
        if cls.decorators:
            dec_str = ', '.join(
                f"@{d.name}({', '.join(f'{k}={v}' for k, v in d.arguments.items())})"
                if d.arguments else f"@{d.name}"
                for d in cls.decorators
            )
            print(f"  {cls.name}: {dec_str}")

    # Show properties
    print("\nMethods with @property:")
    print("-" * 70)
    for cls in package.classes:
        properties = [m for m in cls.methods if any(d.name == "property" for d in m.decorators)]
        if properties:
            print(f"  {cls.name}:")
            for prop in properties:
                print(f"    - {prop.name}: {prop.return_type}")

    # Show static/class methods
    print("\nStatic and Class Methods:")
    print("-" * 70)
    for cls in package.classes:
        static_methods = [m for m in cls.methods if m.is_static]
        class_methods = [m for m in cls.methods if m.is_class_method]
        if static_methods or class_methods:
            print(f"  {cls.name}:")
            for m in static_methods:
                decorators = ', '.join(f'@{d.name}' for d in m.decorators)
                print(f"    @staticmethod {m.name}()")
                if len(m.decorators) > 1:
                    print(f"      Additional decorators: {decorators}")
            for m in class_methods:
                print(f"    @classmethod {m.name}()")

    # Show all unique decorator types found
    print("\nAll Decorators Found:")
    print("-" * 70)
    all_decorators = set()
    for cls in package.classes:
        for dec in cls.decorators:
            all_decorators.add(f"@{dec.name}" + (f" ({dec.module})" if dec.module else ""))
        for method in cls.methods:
            for dec in method.decorators:
                all_decorators.add(f"@{dec.name}" + (f" ({dec.module})" if dec.module else ""))

    for dec in sorted(all_decorators):
        print(f"  {dec}")

    # Export to PlantUML
    exporter = PlantUMLExporter()
    plantuml_code = exporter.export_project(project)

    output_file = Path(__file__).parent / "advanced_features.puml"
    output_file.write_text(plantuml_code)

    print(f"\n{'=' * 70}")
    print(f"PlantUML diagram saved to: {output_file}")
    print("=" * 70)

    # Show Phase 4 feature summary
    print("\nPhase 4 Features Detected:")
    print("=" * 70)
    abstract_classes = sum(1 for cls in package.classes if cls.is_abstract)
    dataclasses = sum(1 for cls in package.classes if any(d.name == "dataclass" for d in cls.decorators))
    properties = sum(1 for cls in package.classes for m in cls.methods if any(d.name == "property" for d in m.decorators))
    abstract_methods = sum(1 for cls in package.classes for m in cls.methods if m.is_abstract)

    print(f"✓ Abstract classes (ABC): {abstract_classes}")
    print(f"✓ Dataclasses (@dataclass): {dataclasses}")
    print(f"✓ Properties (@property): {properties}")
    print(f"✓ Abstract methods (@abstractmethod): {abstract_methods}")
    print(f"✓ Total decorators: {len(all_decorators)}")


if __name__ == "__main__":
    main()
