"""
Python AST Parser for DRAIT.

Parses Python source code and extracts class information into DRAIT metamodel.
Phase 1: Basic class, attribute, and method extraction.
"""

import ast
from pathlib import Path
from typing import Any

from drait.metamodel import (
    Project,
    Package,
    Class,
    Attribute,
    Method,
    Parameter,
    TypeReference,
    Visibility,
    Relationship,
    RelationshipType,
    Decorator,
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

        # Phase 3: Infer relationships between classes
        relationships = self._infer_relationships()

        # Create package
        package_name = Path(source_name).stem if source_name != "<string>" else "parsed"
        package = Package(
            name=package_name,
            classes=self.classes,
            relationships=relationships,
            docstring=ast.get_docstring(tree),
        )

        return package

    def _extract_class(self, node: ast.ClassDef) -> Class | None:
        """
        Extract class information from AST node.

        Args:
            node: AST ClassDef node

        Returns:
            Class object or None
        """
        # Extract docstring
        docstring = ast.get_docstring(node)

        # Phase 4: Extract decorators
        decorators = self._extract_decorators(node.decorator_list)

        # Extract base classes
        base_classes = []
        is_abstract = False
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
                # Check for ABC base class
                if base.id in ("ABC", "ABCMeta"):
                    is_abstract = True
            elif isinstance(base, ast.Attribute):
                # Handle cases like abc.ABC
                base_name = self._get_attribute_name(base)
                base_classes.append(base_name)
                if "ABC" in base_name:
                    is_abstract = True

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
            decorators=decorators,
            is_abstract=is_abstract,
        )

        return cls

    def _extract_class_attributes(self, node: ast.ClassDef) -> list[Attribute]:
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

    def _extract_init_attributes(self, node: ast.FunctionDef) -> list[Attribute]:
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
    ) -> Attribute | None:
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
        value_node: ast.expr | None,
        is_static: bool
    ) -> Attribute | None:
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

    def _extract_method(self, node: ast.FunctionDef) -> Method | None:
        """
        Extract method information from AST node.

        Args:
            node: FunctionDef node

        Returns:
            Method object or None
        """
        # Extract docstring
        docstring = ast.get_docstring(node)

        # Phase 4: Extract decorators
        decorators = self._extract_decorators(node.decorator_list)

        # Determine visibility
        visibility = self._get_visibility_from_name(node.name)

        # Check for special method types
        is_static = self._is_static_method(node)
        is_class_method = self._is_class_method(node)
        is_abstract = self._is_abstract_method(node)

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
            is_abstract=is_abstract,
            decorators=decorators,
            docstring=docstring,
        )

        return method

    def _extract_parameter(self, arg: ast.arg) -> Parameter | None:
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

        Phase 2: Advanced support for generics, Optional, Union, etc.
        """
        if isinstance(annotation, ast.Name):
            # Simple type like 'str', 'int', 'Any'
            return TypeReference(name=annotation.id)

        elif isinstance(annotation, ast.Constant):
            # String annotation like 'SomeClass'
            return TypeReference(name=str(annotation.value))

        elif isinstance(annotation, ast.Subscript):
            # Generic type like List[str], Dict[str, int], Optional[int]
            return self._parse_subscript_type(annotation)

        elif isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
            # Union type using | operator (Python 3.10+): str | int
            return self._parse_union_type(annotation)

        elif isinstance(annotation, ast.Attribute):
            # Qualified type like typing.List, collections.OrderedDict
            return self._parse_attribute_type(annotation)

        else:
            # Fallback: convert to string
            try:
                type_str = ast.unparse(annotation)
                return TypeReference(name=type_str)
            except:
                return TypeReference(name="Any")

    def _parse_subscript_type(self, node: ast.Subscript) -> TypeReference:
        """
        Parse subscripted type like List[str], Dict[str, int], Optional[int].

        Args:
            node: Subscript AST node

        Returns:
            TypeReference with type arguments
        """
        # Get the base type name
        if isinstance(node.value, ast.Name):
            base_name = node.value.id
            module = None
        elif isinstance(node.value, ast.Attribute):
            # Handle typing.List, etc.
            base_name = node.value.attr
            module = self._get_module_from_attribute(node.value)
        else:
            # Fallback
            try:
                base_name = ast.unparse(node.value)
                module = None
            except:
                base_name = "Any"
                module = None

        # Parse type arguments
        type_args = []
        if isinstance(node.slice, ast.Tuple):
            # Multiple arguments like Dict[str, int]
            for elt in node.slice.elts:
                type_args.append(self._parse_type_annotation(elt))
        else:
            # Single argument like List[str]
            type_args.append(self._parse_type_annotation(node.slice))

        # Handle Optional specially
        if base_name == "Optional":
            # Optional[T] -> TypeReference with is_optional=True
            if type_args:
                type_ref = type_args[0]
                type_ref.is_optional = True
                return type_ref
            else:
                return TypeReference(name="Any", is_optional=True)

        # Handle Union
        if base_name == "Union":
            # For now, represent Union as string
            # Future: could create a UnionType
            types_str = ", ".join(str(arg) for arg in type_args)
            return TypeReference(name=f"Union[{types_str}]")

        # Regular generic type
        return TypeReference(
            name=base_name,
            module=module,
            type_arguments=type_args,
        )

    def _parse_union_type(self, node: ast.BinOp) -> TypeReference:
        """
        Parse Union type using | operator (Python 3.10+).

        Example: str | int | None

        Args:
            node: BinOp node with BitOr operator

        Returns:
            TypeReference representing union
        """
        # Collect all types in the union
        types = []

        def collect_union_types(n):
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.BitOr):
                collect_union_types(n.left)
                collect_union_types(n.right)
            else:
                types.append(self._parse_type_annotation(n))

        collect_union_types(node)

        # Check if None is in the union (makes it optional)
        has_none = any(
            isinstance(t, TypeReference) and t.name == "None"
            for t in types
        )

        if has_none:
            # Filter out None
            non_none_types = [t for t in types if t.name != "None"]

            if len(non_none_types) == 1:
                # Optional[T]
                type_ref = non_none_types[0]
                type_ref.is_optional = True
                return type_ref
            else:
                # Union with None
                types_str = " | ".join(str(t) for t in types)
                return TypeReference(name=types_str)
        else:
            # Regular union without None
            types_str = " | ".join(str(t) for t in types)
            return TypeReference(name=types_str)

    def _parse_attribute_type(self, node: ast.Attribute) -> TypeReference:
        """
        Parse attribute type like typing.List, collections.OrderedDict.

        Args:
            node: Attribute node

        Returns:
            TypeReference with module information
        """
        type_name = node.attr
        module = self._get_module_from_attribute(node)

        return TypeReference(name=type_name, module=module)

    def _get_module_from_attribute(self, node: ast.Attribute) -> str | None:
        """
        Extract module name from attribute node.

        Args:
            node: Attribute node

        Returns:
            Module name or None
        """
        if isinstance(node.value, ast.Name):
            return node.value.id
        elif isinstance(node.value, ast.Attribute):
            # Nested attributes like a.b.c
            parts = []
            current = node.value
            while isinstance(current, ast.Attribute):
                parts.insert(0, current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.insert(0, current.id)
            return ".".join(parts)
        return None

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

    def _is_abstract_method(self, node: ast.FunctionDef) -> bool:
        """Check if method has @abstractmethod decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "abstractmethod":
                return True
            elif isinstance(decorator, ast.Attribute):
                if decorator.attr == "abstractmethod":
                    return True
        return False

    def _extract_decorators(self, decorator_list: list[ast.expr]) -> list[Decorator]:
        """
        Extract decorators from decorator list.

        Args:
            decorator_list: List of decorator AST nodes

        Returns:
            List of Decorator objects
        """
        decorators = []

        for dec_node in decorator_list:
            if isinstance(dec_node, ast.Name):
                # Simple decorator like @property, @staticmethod
                decorators.append(Decorator(name=dec_node.id))

            elif isinstance(dec_node, ast.Attribute):
                # Qualified decorator like @abc.abstractmethod
                name = dec_node.attr
                module = self._get_module_from_attribute(dec_node)
                decorators.append(Decorator(name=name, module=module))

            elif isinstance(dec_node, ast.Call):
                # Decorator with arguments like @dataclass(frozen=True)
                if isinstance(dec_node.func, ast.Name):
                    name = dec_node.func.id
                    module = None
                elif isinstance(dec_node.func, ast.Attribute):
                    name = dec_node.func.attr
                    module = self._get_module_from_attribute(dec_node.func)
                else:
                    continue

                # Extract arguments (simplified - just capture as strings)
                arguments = {}
                for i, arg in enumerate(dec_node.args):
                    try:
                        arguments[f"arg{i}"] = ast.unparse(arg)
                    except:
                        arguments[f"arg{i}"] = str(arg)

                for keyword in dec_node.keywords:
                    try:
                        arguments[keyword.arg] = ast.unparse(keyword.value)
                    except:
                        arguments[keyword.arg] = str(keyword.value)

                decorators.append(Decorator(name=name, module=module, arguments=arguments))

        return decorators

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

    def _infer_relationships(self) -> list[Relationship]:
        """
        Infer relationships between classes based on code patterns.

        Phase 3: Relationship inference
        - Inheritance: from base classes
        - Composition: attributes created in __init__
        - Aggregation: attributes passed as parameters
        - Dependency: method parameters and return types

        Returns:
            List of inferred relationships
        """
        relationships = []

        # Create class name to ID lookup
        class_map = {cls.name: cls.id for cls in self.classes}
        class_names = set(class_map.keys())

        for cls in self.classes:
            # 1. Inheritance relationships (from base_classes)
            relationships.extend(self._infer_inheritance(cls, class_names, class_map))

            # 2. Composition/Aggregation (from attributes)
            relationships.extend(self._infer_composition_aggregation(cls, class_names, class_map))

            # 3. Dependency (from method signatures)
            relationships.extend(self._infer_dependencies(cls, class_names, class_map))

        return relationships

    def _infer_inheritance(self, cls: Class, class_names: set, class_map: dict) -> list[Relationship]:
        """
        Infer inheritance relationships from base_classes.

        Args:
            cls: Source class
            class_names: Set of all class names in package
            class_map: Map of class names to UUIDs

        Returns:
            List of inheritance relationships
        """
        relationships = []

        for base_class in cls.base_classes:
            # Only create relationship if target class is in same package
            if base_class in class_names:
                rel = Relationship(
                    type=RelationshipType.INHERITANCE,
                    source_id=cls.id,
                    target_id=class_map[base_class],
                    source_role="derived",
                    target_role="base",
                )
                relationships.append(rel)

        return relationships

    def _infer_composition_aggregation(self, cls: Class, class_names: set, class_map: dict) -> list[Relationship]:
        """
        Infer composition/aggregation relationships from attributes.

        Heuristic:
        - Composition: Attribute type is instantiated in __init__ (ownership)
        - Aggregation: Attribute type is passed as parameter (shared)

        Args:
            cls: Source class
            class_names: Set of all class names in package
            class_map: Map of class names to UUIDs

        Returns:
            List of composition/aggregation relationships
        """
        relationships = []

        for attr in cls.attributes:
            # Skip attributes without type annotations
            if attr.type is None:
                continue

            # Get the base type name (strip Optional, List, etc.)
            type_name = self._get_base_type_name(attr.type)

            # Only create relationship if target is a class in package
            if type_name in class_names:
                # Determine if it's composition or aggregation
                # For now, use simple heuristic: if Optional or collection, it's aggregation
                is_collection = self._is_collection_type(attr.type)
                is_optional = attr.type.is_optional

                if is_collection or is_optional:
                    rel_type = RelationshipType.AGGREGATION
                    source_role = "has"
                else:
                    rel_type = RelationshipType.COMPOSITION
                    source_role = "owns"

                rel = Relationship(
                    type=rel_type,
                    source_id=cls.id,
                    target_id=class_map[type_name],
                    source_role=source_role,
                )
                relationships.append(rel)

        return relationships

    def _infer_dependencies(self, cls: Class, class_names: set, class_map: dict) -> list[Relationship]:
        """
        Infer dependency relationships from method parameters and return types.

        A dependency exists when a class uses another class in method signatures
        but doesn't store it as an attribute.

        Args:
            cls: Source class
            class_names: Set of all class names in package
            class_map: Map of class names to UUIDs

        Returns:
            List of dependency relationships
        """
        relationships = []

        # Collect types already in attributes (to avoid duplicates)
        attribute_types = {self._get_base_type_name(attr.type) for attr in cls.attributes if attr.type is not None}

        # Track unique dependencies
        dependencies = set()

        for method in cls.methods:
            # Check parameters
            for param in method.parameters:
                if param.name in ('self', 'cls'):
                    continue
                # Skip parameters without type annotations
                if param.type is None:
                    continue
                type_name = self._get_base_type_name(param.type)
                if type_name in class_names and type_name not in attribute_types:
                    dependencies.add(type_name)

            # Check return type
            if method.return_type:
                type_name = self._get_base_type_name(method.return_type)
                if type_name in class_names and type_name not in attribute_types:
                    dependencies.add(type_name)

        # Create relationships
        for target in dependencies:
            rel = Relationship(
                type=RelationshipType.DEPENDENCY,
                source_id=cls.id,
                target_id=class_map[target],
                source_role="uses",
            )
            relationships.append(rel)

        return relationships

    def _get_base_type_name(self, type_ref: TypeReference) -> str:
        """
        Extract base type name from TypeReference.

        Examples:
        - List[Engine] -> Engine
        - Optional[Department] -> Department
        - Engine -> Engine

        Args:
            type_ref: Type reference to extract from

        Returns:
            Base type name
        """
        # If it has type arguments, get the first one (for List, Set, etc.)
        if type_ref.type_arguments:
            return self._get_base_type_name(type_ref.type_arguments[0])

        return type_ref.name

    def _is_collection_type(self, type_ref: TypeReference) -> bool:
        """
        Check if type is a collection (List, Set, Dict, etc.).

        Args:
            type_ref: Type reference to check

        Returns:
            True if collection type
        """
        collection_types = {'List', 'list', 'Set', 'set', 'Dict', 'dict',
                           'Tuple', 'tuple', 'Sequence', 'Iterable'}
        return type_ref.name in collection_types


def parse_file_to_project(file_path: str, project_name: str | None = None) -> Project:
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


def parse_folder_to_project(folder_path: str, project_name: str | None = None) -> Project:
    """
    Parse all Python files in a folder to a Project with nested package structure.

    Creates one Package per directory, with nested directories represented using
    dot notation (e.g., "services.auth" for services/auth/).

    Args:
        folder_path: Path to folder containing Python files
        project_name: Optional project name (defaults to folder name)

    Returns:
        Project containing multiple packages based on directory structure

    Example:
        For folder structure:
            myproject/
                models.py
                services/
                    auth.py
                    user.py
                utils/
                    helpers.py

        Creates packages:
            - "" (root): classes from models.py
            - "services": classes from services/*.py
            - "utils": classes from utils/*.py
    """
    folder = Path(folder_path)

    if not folder.is_dir():
        raise ValueError(f"Not a directory: {folder_path}")

    # Directories to exclude from parsing
    EXCLUDED_DIRS = {
        '.venv', 'venv', '__pycache__', '.git',
        'node_modules', '.tox', 'build', 'dist',
        '.eggs', '*.egg-info', '.pytest_cache',
        '.mypy_cache', '.ruff_cache'
    }

    # Find all .py files recursively, excluding common directories
    all_py_files = folder.rglob("*.py")
    py_files = sorted([
        f for f in all_py_files
        if not any(excluded in f.parts for excluded in EXCLUDED_DIRS)
    ])

    if not py_files:
        raise ValueError(f"No Python files found in: {folder_path}")

    # Group files by their parent directory
    from collections import defaultdict
    files_by_package = defaultdict(list)

    for py_file in py_files:
        # Get relative path from folder root
        relative_path = py_file.relative_to(folder)

        # Determine package name from directory structure
        if relative_path.parent == Path('.'):
            # File in root directory
            package_name = ""
        else:
            # File in subdirectory - use dot notation
            package_name = str(relative_path.parent).replace('/', '.').replace('\\', '.')

        files_by_package[package_name].append(py_file)

    # Parse each package's files
    packages = []
    parser = PythonParser()

    for package_name, files in sorted(files_by_package.items()):
        package_classes = []
        package_relationships = []

        for py_file in files:
            try:
                file_package = parser.parse_file(str(py_file))

                # Add source file metadata to each class
                relative_path = py_file.relative_to(folder)
                for cls in file_package.classes:
                    cls.metadata["source_file"] = str(relative_path)
                    cls.metadata["source_file_absolute"] = str(py_file)

                package_classes.extend(file_package.classes)
                package_relationships.extend(file_package.relationships)
            except Exception as e:
                # Skip files that fail to parse (e.g., syntax errors)
                print(f"Warning: Skipping {py_file}: {e}", file=sys.stderr)
                continue

        # Only create package if it has classes
        if package_classes:
            # Use root package name or directory-based name
            display_name = package_name if package_name else Path(folder_path).name

            package = Package(
                name=package_name if package_name else display_name,
                classes=package_classes,
                relationships=package_relationships,
                docstring=f"Package from {len(files)} Python file(s)"
            )
            packages.append(package)

    if not packages:
        raise ValueError(f"No classes found in Python files in: {folder_path}")

    # Create project
    if project_name is None:
        project_name = folder.name

    project = Project(
        name=project_name,
        packages=packages,
    )

    return project
