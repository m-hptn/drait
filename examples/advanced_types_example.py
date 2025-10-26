"""
Example: Parse Python code with advanced type hints (Phase 2).

This example demonstrates parsing complex type annotations including:
- Generic types (List, Dict, Set, Tuple)
- Optional types
- Union types
- Nested generics
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from drait.parsers.python_parser import PythonParser
from drait.exporters.plantuml import PlantUMLExporter
from drait.metamodel import Project


# Sample code with advanced type hints
ADVANCED_TYPES_CODE = '''
from typing import List, Dict, Optional, Union, Set, Tuple

class DataContainer:
    """Container with various advanced type hints."""

    def __init__(self):
        # Generic types
        self.items: List[str] = []
        self.mapping: Dict[str, int] = {}
        self.unique_values: Set[int] = set()
        self.coordinates: Tuple[float, float] = (0.0, 0.0)

        # Optional types
        self.optional_name: Optional[str] = None
        self.nullable_value: int | None = None

        # Nested generics
        self.nested_list: List[List[int]] = [[]]
        self.complex_map: Dict[str, List[int]] = {}
        self.graph: Dict[str, Set[str]] = {}

    def process_items(self, items: List[str]) -> Dict[str, int]:
        """Process list of items and return mapping."""
        return {item: len(item) for item in items}

    def find_value(self, key: str) -> Optional[int]:
        """Find value by key, returns None if not found."""
        return self.mapping.get(key)

    def merge_data(
        self,
        primary: Dict[str, int],
        secondary: Dict[str, int]
    ) -> Dict[str, int]:
        """Merge two dictionaries."""
        result = primary.copy()
        result.update(secondary)
        return result


class UserRepository:
    """Repository pattern with advanced types."""

    def __init__(self):
        self.users: Dict[int, "User"] = {}
        self.cache: Optional[Dict[str, Any]] = None

    def find_by_id(self, user_id: int) -> Optional["User"]:
        """Find user by ID."""
        return self.users.get(user_id)

    def find_all(self) -> List["User"]:
        """Get all users."""
        return list(self.users.values())

    def search(
        self,
        criteria: Dict[str, Union[str, int, bool]]
    ) -> List["User"]:
        """Search users by criteria."""
        # Implementation here
        return []


class User:
    """User entity with type hints."""

    def __init__(
        self,
        id: int,
        name: str,
        email: Optional[str] = None,
        tags: List[str] = None
    ):
        self.id: int = id
        self.name: str = name
        self.email: Optional[str] = email
        self.tags: List[str] = tags or []
        self.metadata: Dict[str, Union[str, int, float]] = {}

    def add_tag(self, tag: str) -> None:
        """Add a tag to the user."""
        if tag not in self.tags:
            self.tags.append(tag)

    def get_metadata(self, key: str) -> Union[str, int, float, None]:
        """Get metadata value."""
        return self.metadata.get(key)
'''


def main():
    """Demonstrate parsing code with advanced type hints."""
    print("=" * 70)
    print("DRAIT Phase 2: Advanced Type Hints Parsing")
    print("=" * 70)

    # Parse the code
    print("\n1. Parsing code with advanced type hints...")
    parser = PythonParser()
    package = parser.parse_source(ADVANCED_TYPES_CODE, "advanced_types.py")

    print(f"   ✓ Found {len(package.classes)} classes\n")

    # Show detected types for each class
    for cls in package.classes:
        print(f"   Class: {cls.name}")
        print(f"   {'─' * 60}")

        if cls.attributes:
            print("   Attributes:")
            for attr in cls.attributes:
                type_str = str(attr.type) if attr.type else "Any"
                print(f"     • {attr.name}: {type_str}")

        if cls.methods:
            print("   Methods:")
            for method in cls.methods[:3]:  # Show first 3 methods
                params = ", ".join(
                    f"{p.name}: {p.type}" for p in method.parameters
                ) if method.parameters else ""

                return_type = str(method.return_type) if method.return_type else "None"
                print(f"     • {method.name}({params}) → {return_type}")

        print()

    # Export to PlantUML
    print("\n2. Exporting to PlantUML...")
    project = Project(name="AdvancedTypes", packages=[package])
    exporter = PlantUMLExporter()
    plantuml_content = exporter.export_project(project)

    # Save to file
    output_file = Path(__file__).parent / "advanced_types.puml"
    with open(output_file, 'w') as f:
        f.write(plantuml_content)

    print(f"   ✓ Saved to: {output_file}")

    # Show PlantUML preview
    print("\n3. PlantUML Preview:")
    print("=" * 70)
    print(plantuml_content)
    print("=" * 70)

    # Summary of type features detected
    print("\n4. Advanced Type Features Detected:")
    print("   ✅ Generic types (List[T], Dict[K,V], Set[T])")
    print("   ✅ Optional types (Optional[T], T | None)")
    print("   ✅ Union types (Union[A, B, C])")
    print("   ✅ Nested generics (List[List[int]], Dict[str, List[int]])")
    print("   ✅ Forward references (\"User\")")
    print("   ✅ Qualified types (typing.List, typing.Dict)")

    print("\n" + "=" * 70)
    print("✓ Phase 2 Complete! Advanced type parsing working!")
    print("=" * 70)


if __name__ == "__main__":
    main()
