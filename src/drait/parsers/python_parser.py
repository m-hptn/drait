"""
Python AST Parser for DRAIT.

Parses Python source code and extracts class information into DRAIT metamodel.
Phase 1: Basic class, attribute, and method extraction.
"""

import ast
from pathlib import Path
from typing import List, Optional, Dict, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from drait.metamodel import (
    Project,
    Package,
    Class,
    Attribute,
    Method,
    Parameter,
    TypeReference,
    Visibility,
)


class PythonParser:
    """
    Parse Python source code to DRAIT metamodel.

    Phase 1 Features:
    - Extract class definitions
    - Extract attributes from __init__ and class variables
    - Extract methods with parameters
    - Basic visibility detection from naming conventions
    """

    def __init__(self):
        """Initialize the parser."""
        self.current_class = None
        self.classes = []

    def parse_file(self, file_path: str) -> Package:
        """
        Parse a Python file and extract classes.

        Args:
            file_path: Path to Python source file

        Returns:
            Package containing extracted classes
        """
        with open(file_path, 'r') as f:
            source_code = f.read()

        return self.parse_source(source_code, file_path)

    def parse_source(self, source_code: str, source_name: str = "<string>") -> Package:
        """
        Parse Python source code and extract classes.

        Args:
            source_code: Python source code as string
            source_name: Name/path of source (for error messages)

        Returns:
            Package containing extracted classes
        """
        # Parse source code to AST
        try:
            tree = ast.parse(source_code, filename=source_name)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in {source_name}: {e}")

        # Extract classes
        self.classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                cls = self._extract_class(node)
                if cls:
                    self.classes.append(cls)

        # Create package
        package_name = Path(source_name).stem if source_name != "<string>" else "parsed"
        package = Package(
            name=package_name,
            classes=self.classes,
            docstring=ast.get_docstring(tree),
        )

        return package

    def _extract_class(self, node: ast.ClassDef) -> Optional[Class]:
        """
        Extract class information from AST node.

        Args:
            node: AST ClassDef node

        Returns:
            Class object or None
        """
        # Extract docstring
        docstring = ast.get_docstring(node)

        # Extract base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                # Handle cases like module.ClassName
                base_classes.append(self._get_attribute_name(base))

        # Extract attributes from class body
        attributes = self._extract_class_attributes(node)

        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method = self._extract_method(item)
                if method:
                    methods.append(method)

                    # Extract attributes from __init__
                    if item.name == "__init__":
                        init_attrs = self._extract_init_attributes(item)
                        attributes.extend(init_attrs)

        # Create class
        cls = Class(
            name=node.name,
            base_classes=base_classes,
            attributes=attributes,
            methods=methods,
            docstring=docstring,
        )

        return cls

    def _extract_class_attributes(self, node: ast.ClassDef) -> List[Attribute]:
        """
        Extract class-level attributes (not from __init__).

        Args:
            node: ClassDef node

        Returns:
            List of attributes
        """
        attributes = []

        for item in node.body:
            # Look for assignments at class level
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attr = self._create_attribute_from_assignment(
                            target.id,
                            item.value,
                            is_static=True
                        )
                        if attr:
                            attributes.append(attr)

            # Look for annotated assignments (with type hints)
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    attr = self._create_attribute_from_annotated_assignment(
                        item.target.id,
                        item.annotation,
                        item.value,
                        is_static=True
                    )
                    if attr:
                        attributes.append(attr)

        return attributes

    def _extract_init_attributes(self, node: ast.FunctionDef) -> List[Attribute]:
        """
        Extract instance attributes from __init__ method.

        Args:
            node: FunctionDef node for __init__

        Returns:
            List of attributes
        """
        attributes = []

        for item in node.body:
            # Look for self.attribute = value
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == "self":
                            attr = self._create_attribute_from_assignment(
                                target.attr,
                                item.value,
                                is_static=False
                            )
                            if attr:
                                attributes.append(attr)

            # Look for self.attribute: Type = value
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Attribute):
                    if isinstance(item.target.value, ast.Name) and item.target.value.id == "self":
                        attr = self._create_attribute_from_annotated_assignment(
                            item.target.attr,
                            item.annotation,
                            item.value,
                            is_static=False
                        )
                        if attr:
                            attributes.append(attr)

        return attributes

    def _create_attribute_from_assignment(
        self,
        name: str,
        value_node: ast.expr,
        is_static: bool
    ) -> Optional[Attribute]:
        """Create attribute from simple assignment."""
        # Infer type from value if possible
        type_ref = self._infer_type_from_value(value_node)

        # Determine visibility from name
        visibility = self._get_visibility_from_name(name)

        # Get default value as string
        default_value = None
        if value_node:
            try:
                default_value = ast.unparse(value_node)
            except:
                default_value = None

        return Attribute(
            name=name,
            type=type_ref,
            visibility=visibility,
            is_static=is_static,
            default_value=default_value,
        )

    def _create_attribute_from_annotated_assignment(
        self,
        name: str,
        annotation: ast.expr,
        value_node: Optional[ast.expr],
        is_static: bool
    ) -> Optional[Attribute]:
        """Create attribute from annotated assignment (with type hint)."""
        # Parse type annotation
        type_ref = self._parse_type_annotation(annotation)

        # Determine visibility from name
        visibility = self._get_visibility_from_name(name)

        # Get default value as string
        default_value = None
        if value_node:
            try:
                default_value = ast.unparse(value_node)
            except:
                default_value = None

        return Attribute(
            name=name,
            type=type_ref,
            visibility=visibility,
            is_static=is_static,
            default_value=default_value,
        )

    def _extract_method(self, node: ast.FunctionDef) -> Optional[Method]:
        """
        Extract method information from AST node.

        Args:
            node: FunctionDef node

        Returns:
            Method object or None
        """
        # Extract docstring
        docstring = ast.get_docstring(node)

        # Determine visibility
        visibility = self._get_visibility_from_name(node.name)

        # Check for special method types
        is_static = self._is_static_method(node)
        is_class_method = self._is_class_method(node)

        # Extract parameters (skip 'self' or 'cls')
        parameters = []
        skip_first = not is_static  # Skip self/cls for instance and class methods

        for i, arg in enumerate(node.args.args):
            if skip_first and i == 0:
                continue  # Skip self/cls

            param = self._extract_parameter(arg)
            if param:
                parameters.append(param)

        # Extract return type annotation
        return_type = None
        if node.returns:
            return_type = self._parse_type_annotation(node.returns)

        # Create method
        method = Method(
            name=node.name,
            parameters=parameters,
            return_type=return_type,
            visibility=visibility,
            is_static=is_static,
            is_class_method=is_class_method,
            docstring=docstring,
        )

        return method

    def _extract_parameter(self, arg: ast.arg) -> Optional[Parameter]:
        """
        Extract parameter information.

        Args:
            arg: ast.arg node

        Returns:
            Parameter object or None
        """
        # Parse type annotation if present
        type_ref = None
        if arg.annotation:
            type_ref = self._parse_type_annotation(arg.annotation)

        return Parameter(
            name=arg.arg,
            type=type_ref,
        )

    def _parse_type_annotation(self, annotation: ast.expr) -> TypeReference:
        """
        Parse type annotation to TypeReference.

        Phase 1: Basic support for simple types.
        Returns generic 'str' representation for complex types.
        """
        if isinstance(annotation, ast.Name):
            # Simple type like 'str', 'int'
            return TypeReference(name=annotation.id)

        elif isinstance(annotation, ast.Constant):
            # String annotation like 'SomeClass'
            return TypeReference(name=str(annotation.value))

        else:
            # Complex type - convert to string for now
            try:
                type_str = ast.unparse(annotation)
                return TypeReference(name=type_str)
            except:
                return TypeReference(name="Any")

    def _infer_type_from_value(self, value_node: ast.expr) -> TypeReference:
        """
        Infer type from assigned value.

        Simple inference for Phase 1.
        """
        if isinstance(value_node, ast.Constant):
            # Infer from constant value
            value_type = type(value_node.value).__name__
            return TypeReference(name=value_type)

        elif isinstance(value_node, ast.List):
            return TypeReference(name="list")

        elif isinstance(value_node, ast.Dict):
            return TypeReference(name="dict")

        elif isinstance(value_node, ast.Set):
            return TypeReference(name="set")

        elif isinstance(value_node, ast.Tuple):
            return TypeReference(name="tuple")

        else:
            # Default to Any
            return TypeReference(name="Any")

    def _get_visibility_from_name(self, name: str) -> Visibility:
        """
        Determine visibility from Python naming conventions.

        - __name: private
        - _name: protected
        - name: public
        """
        if name.startswith("__") and not name.endswith("__"):
            return Visibility.PRIVATE
        elif name.startswith("_"):
            return Visibility.PROTECTED
        else:
            return Visibility.PUBLIC

    def _is_static_method(self, node: ast.FunctionDef) -> bool:
        """Check if method has @staticmethod decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "staticmethod":
                return True
        return False

    def _is_class_method(self, node: ast.FunctionDef) -> bool:
        """Check if method has @classmethod decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "classmethod":
                return True
        return False

    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get full attribute name like module.ClassName."""
        parts = []
        current = node

        while isinstance(current, ast.Attribute):
            parts.insert(0, current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.insert(0, current.id)

        return ".".join(parts)


def parse_file_to_project(file_path: str, project_name: Optional[str] = None) -> Project:
    """
    Convenience function to parse a Python file to a complete Project.

    Args:
        file_path: Path to Python file
        project_name: Optional project name (defaults to filename)

    Returns:
        Project containing parsed classes
    """
    parser = PythonParser()
    package = parser.parse_file(file_path)

    if project_name is None:
        project_name = Path(file_path).stem

    project = Project(
        name=project_name,
        packages=[package],
    )

    return project
