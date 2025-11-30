"""
PlantUML exporter for DRAIT metamodel.

Converts DRAIT metamodel to PlantUML class diagram syntax for visualization.
"""


from drait.metamodel import (
    Project,
    Package,
    Class,
    Attribute,
    Method,
    Parameter,
    Relationship,
    TypeReference,
    Visibility,
    RelationshipType,
)


class PlantUMLExporter:
    """
    Export DRAIT metamodel to PlantUML format.

    Supports:
    - Classes with attributes and methods
    - Visibility modifiers (public, protected, private)
    - Relationships (inheritance, association, composition, etc.)
    - Type information
    - Stereotypes
    - Abstract classes
    """

    def __init__(self, include_methods: bool = True, include_attributes: bool = True):
        """
        Initialize PlantUML exporter.

        Args:
            include_methods: Whether to include methods in output
            include_attributes: Whether to include attributes in output
        """
        self.include_methods = include_methods
        self.include_attributes = include_attributes

    def export_project(self, project: Project) -> str:
        """
        Export entire project to PlantUML.

        Args:
            project: Project to export

        Returns:
            PlantUML diagram as string
        """
        lines = ["@startuml"]
        lines.append(f"title {project.name}")
        lines.append("")

        # Add styling
        lines.extend(self._get_styling())
        lines.append("")

        # Export all packages
        for package in project.packages:
            lines.extend(self.export_package(package))
            lines.append("")

        lines.append("@enduml")
        return "\n".join(lines)

    def export_package(self, package: Package) -> list[str]:
        """
        Export package to PlantUML.

        Args:
            package: Package to export

        Returns:
            List of PlantUML lines
        """
        lines = []

        # Package declaration (if not default)
        if package.name and package.name != "default":
            lines.append(f"package {package.name} {{")
            indent = "  "
        else:
            indent = ""

        # Export classes
        for cls in package.classes:
            class_lines = self.export_class(cls)
            lines.extend([indent + line for line in class_lines])
            lines.append("")

        # Close package
        if package.name and package.name != "default":
            lines.append("}")
            lines.append("")

        # Export relationships
        for rel in package.relationships:
            lines.append(self.export_relationship(rel, package.classes))

        return lines

    def export_class(self, cls: Class) -> list[str]:
        """
        Export class to PlantUML.

        Args:
            cls: Class to export

        Returns:
            List of PlantUML lines
        """
        lines = []

        # Class declaration with modifiers
        class_type = "abstract class" if cls.is_abstract else "class"
        class_name = cls.name

        # Add stereotypes
        if cls.stereotypes:
            stereotype_str = " <<" + ", ".join(cls.stereotypes) + ">>"
            lines.append(f"{class_type} {class_name} {stereotype_str} {{")
        else:
            lines.append(f"{class_type} {class_name} {{")

        # Add attributes
        if self.include_attributes and cls.attributes:
            for attr in cls.attributes:
                lines.append("  " + self._format_attribute(attr))

            # Separator between attributes and methods
            if self.include_methods and cls.methods:
                lines.append("  --")

        # Add methods
        if self.include_methods and cls.methods:
            for method in cls.methods:
                lines.append("  " + self._format_method(method))

        lines.append("}")

        return lines

    def export_relationship(self, rel: Relationship, classes: list[Class]) -> str:
        """
        Export relationship to PlantUML.

        Args:
            rel: Relationship to export
            classes: List of classes to find source and target names

        Returns:
            PlantUML relationship line
        """
        # Find class names
        source_name = self._find_class_name(rel.source_id, classes)
        target_name = self._find_class_name(rel.target_id, classes)

        if not source_name or not target_name:
            return f"' Relationship skipped: source or target not found"

        # Map relationship type to PlantUML syntax
        arrow = self._get_relationship_arrow(rel.type)

        # Build relationship line
        parts = [source_name]

        # Add source multiplicity and role
        if rel.source_multiplicity:
            parts.append(f'"{rel.source_multiplicity.value}"')

        # Add arrow
        parts.append(arrow)

        # Add target multiplicity and role
        if rel.target_multiplicity:
            parts.append(f'"{rel.target_multiplicity.value}"')

        parts.append(target_name)

        # Add label if roles are specified
        labels = []
        if rel.source_role:
            labels.append(f"{rel.source_role}")
        if rel.target_role:
            labels.append(f"{rel.target_role}")

        line = " ".join(parts)
        if labels:
            line += f" : {' / '.join(labels)}"

        return line

    def _format_attribute(self, attr: Attribute) -> str:
        """Format attribute for PlantUML."""
        visibility = self._get_visibility_symbol(attr.visibility)
        type_str = self._format_type(attr.type)

        # Build attribute string
        parts = [visibility, attr.name, ":", type_str]

        # Add static modifier
        if attr.is_static:
            parts.insert(1, "{static}")

        # Add default value
        if attr.default_value:
            parts.extend(["=", attr.default_value])

        return " ".join(parts)

    def _format_method(self, method: Method) -> str:
        """Format method for PlantUML."""
        visibility = self._get_visibility_symbol(method.visibility)

        # Format parameters
        params = []
        for param in method.parameters:
            param_str = param.name
            if param.type:
                param_str += f": {self._format_type(param.type)}"
            if param.default_value:
                param_str += f" = {param.default_value}"
            params.append(param_str)

        params_str = ", ".join(params)

        # Format return type
        return_type = ""
        if method.return_type:
            return_type = f" : {self._format_type(method.return_type)}"

        # Build method string
        method_str = f"{visibility} {method.name}({params_str}){return_type}"

        # Add modifiers
        modifiers = []
        if method.is_static:
            modifiers.append("{static}")
        if method.is_abstract:
            modifiers.append("{abstract}")

        if modifiers:
            method_str = f"{visibility} {' '.join(modifiers)} {method.name}({params_str}){return_type}"

        return method_str

    def _format_type(self, type_ref: TypeReference) -> str:
        """Format type reference for PlantUML."""
        type_str = type_ref.name

        # Add type arguments for generics
        if type_ref.type_arguments:
            args = [self._format_type(arg) for arg in type_ref.type_arguments]
            type_str += f"[{', '.join(args)}]"

        # Add Optional wrapper
        if type_ref.is_optional:
            type_str = f"Optional[{type_str}]"

        return type_str

    def _get_visibility_symbol(self, visibility: Visibility) -> str:
        """Get PlantUML visibility symbol."""
        mapping = {
            Visibility.PUBLIC: "+",
            Visibility.PROTECTED: "#",
            Visibility.PRIVATE: "-",
        }
        return mapping.get(visibility, "+")

    def _get_relationship_arrow(self, rel_type: RelationshipType) -> str:
        """Get PlantUML arrow for relationship type."""
        mapping = {
            RelationshipType.INHERITANCE: "<|--",
            RelationshipType.REALIZATION: "<|..",
            RelationshipType.ASSOCIATION: "-->",
            RelationshipType.AGGREGATION: "o--",
            RelationshipType.COMPOSITION: "*--",
            RelationshipType.DEPENDENCY: "..>",
        }
        return mapping.get(rel_type, "-->")

    def _find_class_name(self, class_id, classes: list[Class]) -> str | None:
        """Find class name by ID."""
        for cls in classes:
            if cls.id == class_id:
                return cls.name
        return None

    def _get_styling(self) -> list[str]:
        """Get default PlantUML styling."""
        return [
            "skinparam classAttributeIconSize 0",
            "skinparam class {",
            "  BackgroundColor White",
            "  BorderColor Black",
            "  ArrowColor Black",
            "}",
        ]


def export_to_file(project: Project, output_file: str, **kwargs) -> None:
    """
    Export project to PlantUML file.

    Args:
        project: Project to export
        output_file: Output file path (.puml or .plantuml)
        **kwargs: Additional arguments for PlantUMLExporter
    """
    exporter = PlantUMLExporter(**kwargs)
    plantuml_content = exporter.export_project(project)

    with open(output_file, 'w') as f:
        f.write(plantuml_content)

    print(f"PlantUML diagram exported to: {output_file}")
    print(f"To generate image: plantuml {output_file}")
    print(f"Or use online: https://www.plantuml.com/plantuml/uml/")
