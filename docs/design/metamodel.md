# Core Metamodel Design

## Overview

The DRAIT metamodel defines the abstract representation of class diagrams and their mapping to Python code. It serves as the foundation for bidirectional transformation between visual diagrams and source code.

## Design Principles

1. **UML 2.5 Alignment**: Follow UML class diagram semantics
2. **Python-Centric**: Optimized for Python language features (type hints, properties, decorators)
3. **Immutable Core**: Use immutability where possible for thread safety
4. **Validation**: Built-in constraint checking
5. **Serialization**: JSON-based persistence for Git compatibility

## Metamodel Hierarchy

```
Project
  └─ Package*
       ├─ Class*
       │    ├─ Attribute*
       │    ├─ Method*
       │    │    └─ Parameter*
       │    └─ Decorator*
       └─ Relationship*
```

## Core Entities

### 1. Project

Represents a complete software project with multiple packages and diagrams.

**Attributes:**
- `id`: UUID - Unique identifier
- `name`: String - Project name
- `version`: String - Project version (semantic versioning)
- `packages`: List[Package] - Contained packages
- `metadata`: Dict - Additional metadata (author, created_at, modified_at, etc.)

**Responsibilities:**
- Top-level container for all model elements
- Manages global settings and configuration
- Tracks version history

### 2. Package

Represents a Python package/module containing classes.

**Attributes:**
- `id`: UUID - Unique identifier
- `name`: String - Package name (Python module path, e.g., "models.user")
- `classes`: List[Class] - Contained classes
- `relationships`: List[Relationship] - Relationships between classes
- `imports`: List[Import] - External dependencies
- `docstring`: Optional[String] - Package documentation

**Responsibilities:**
- Groups related classes
- Maps to Python module/package structure
- Manages class relationships within scope

### 3. Class

Represents a Python class with attributes, methods, and metadata.

**Attributes:**
- `id`: UUID - Unique identifier
- `name`: String - Class name (PascalCase)
- `attributes`: List[Attribute] - Class attributes/fields
- `methods`: List[Method] - Class methods
- `decorators`: List[Decorator] - Class decorators (@dataclass, @abstractmethod, etc.)
- `stereotypes`: List[String] - UML stereotypes («interface», «abstract», «entity», etc.)
- `base_classes`: List[String] - Parent classes (inheritance)
- `is_abstract`: Boolean - Whether class is abstract
- `docstring`: Optional[String] - Class documentation
- `position`: Optional[Position] - UI position in diagram
- `metadata`: Dict - Additional metadata

**Responsibilities:**
- Core modeling element
- Maps directly to Python class definition
- Contains all class-level information

**Constraints:**
- Name must be valid Python identifier (PascalCase)
- Cannot inherit from self
- Abstract class must have at least one abstract method (validation)

### 4. Attribute

Represents a class attribute/field.

**Attributes:**
- `id`: UUID - Unique identifier
- `name`: String - Attribute name (snake_case)
- `type`: TypeReference - Data type (built-in, class, generic, etc.)
- `visibility`: Visibility - PUBLIC, PROTECTED, PRIVATE
- `default_value`: Optional[String] - Default value expression
- `is_static`: Boolean - Class variable vs instance variable
- `is_readonly`: Boolean - Property without setter
- `decorators`: List[Decorator] - Field decorators (@property, etc.)
- `docstring`: Optional[String] - Attribute documentation

**Responsibilities:**
- Represents class state
- Maps to Python instance/class variables or properties
- Defines type information for code generation

**Constraints:**
- Name must be valid Python identifier (snake_case)
- Type must be resolvable

### 5. Method

Represents a class method/function.

**Attributes:**
- `id`: UUID - Unique identifier
- `name`: String - Method name (snake_case)
- `parameters`: List[Parameter] - Method parameters (excluding self/cls)
- `return_type`: Optional[TypeReference] - Return type annotation
- `visibility`: Visibility - PUBLIC, PROTECTED, PRIVATE
- `is_static`: Boolean - @staticmethod
- `is_class_method`: Boolean - @classmethod
- `is_abstract`: Boolean - @abstractmethod
- `decorators`: List[Decorator] - Method decorators
- `docstring`: Optional[String] - Method documentation (with params, returns)
- `body`: Optional[String] - Method implementation (preserved manual code)

**Responsibilities:**
- Represents class behavior
- Maps to Python method definitions
- Stores both signature and implementation

**Constraints:**
- Name must be valid Python identifier (snake_case)
- Static methods cannot have self/cls parameter
- Abstract methods should not have body (or have pass/NotImplementedError)

### 6. Parameter

Represents a method parameter.

**Attributes:**
- `name`: String - Parameter name
- `type`: Optional[TypeReference] - Type annotation
- `default_value`: Optional[String] - Default value expression
- `kind`: ParameterKind - POSITIONAL, KEYWORD, VAR_POSITIONAL (*args), VAR_KEYWORD (**kwargs)

**Responsibilities:**
- Defines method signature
- Maps to Python function parameters

**Constraints:**
- Name must be valid Python identifier
- Positional parameters must come before keyword parameters

### 7. Relationship

Represents relationships between classes (inheritance, association, etc.).

**Attributes:**
- `id`: UUID - Unique identifier
- `type`: RelationshipType - INHERITANCE, ASSOCIATION, AGGREGATION, COMPOSITION, DEPENDENCY
- `source_id`: UUID - Source class ID
- `target_id`: UUID - Target class ID
- `source_role`: Optional[String] - Role name at source end
- `target_role`: Optional[String] - Role name at target end
- `source_multiplicity`: Optional[Multiplicity] - Cardinality (0..1, 1, *, 1..*, etc.)
- `target_multiplicity`: Optional[Multiplicity] - Cardinality
- `is_navigable_from_source`: Boolean - Can navigate from source to target
- `is_navigable_from_target`: Boolean - Can navigate from target to source

**Responsibilities:**
- Connects classes
- Represents UML relationships
- Maps to Python inheritance or attribute types

**Mapping to Python:**
- **Inheritance**: Python class inheritance (`class Child(Parent)`)
- **Association/Aggregation**: Attribute with type reference
- **Composition**: Attribute with type reference (stronger ownership semantics)
- **Dependency**: Import statement or parameter type

### 8. TypeReference

Represents type information with support for generics and unions.

**Attributes:**
- `name`: String - Type name (str, int, List, Optional, etc.)
- `module`: Optional[String] - Module path for imports (typing, collections, etc.)
- `type_arguments`: List[TypeReference] - Generic type arguments (List[str], Dict[str, int])
- `is_optional`: Boolean - Shorthand for Optional[T]

**Examples:**
- `str` → `TypeReference(name="str")`
- `List[str]` → `TypeReference(name="List", module="typing", type_arguments=[TypeReference(name="str")])`
- `Optional[int]` → `TypeReference(name="int", is_optional=True)`
- `Dict[str, User]` → `TypeReference(name="Dict", module="typing", type_arguments=[TypeReference(name="str"), TypeReference(name="User")])`

### 9. Decorator

Represents Python decorators applied to classes, methods, or attributes.

**Attributes:**
- `name`: String - Decorator name (@property, @staticmethod, @dataclass, etc.)
- `module`: Optional[String] - Module for import
- `arguments`: Dict[String, String] - Decorator arguments

**Examples:**
- `@property` → `Decorator(name="property")`
- `@dataclass` → `Decorator(name="dataclass", module="dataclasses")`
- `@validator("name")` → `Decorator(name="validator", arguments={"field": "name"})`

## Enumerations

### Visibility
```python
PUBLIC = "public"      # No underscore
PROTECTED = "protected" # Single underscore _
PRIVATE = "private"    # Double underscore __
```

### RelationshipType
```python
INHERITANCE = "inheritance"
ASSOCIATION = "association"
AGGREGATION = "aggregation"
COMPOSITION = "composition"
DEPENDENCY = "dependency"
REALIZATION = "realization"  # Interface implementation
```

### ParameterKind
```python
POSITIONAL = "positional"
KEYWORD = "keyword"
VAR_POSITIONAL = "var_positional"  # *args
VAR_KEYWORD = "var_keyword"        # **kwargs
```

### Multiplicity
```python
ZERO_TO_ONE = "0..1"
ONE = "1"
ZERO_TO_MANY = "0..*"
ONE_TO_MANY = "1..*"
MANY = "*"
CUSTOM = "n..m"  # Custom range
```

## Supporting Types

### Position
For diagram layout information.

**Attributes:**
- `x`: Float - X coordinate
- `y`: Float - Y coordinate
- `width`: Optional[Float] - Element width
- `height`: Optional[Float] - Element height

### Import
External dependencies.

**Attributes:**
- `module`: String - Module path
- `symbols`: List[String] - Imported symbols (empty for `import module`)
- `alias`: Optional[String] - Import alias

**Examples:**
- `from typing import List, Dict` → `Import(module="typing", symbols=["List", "Dict"])`
- `import numpy as np` → `Import(module="numpy", alias="np")`

## Validation Rules

The metamodel includes built-in validation:

1. **Naming Conventions**:
   - Class names: PascalCase
   - Attribute/method names: snake_case
   - Constants: UPPER_SNAKE_CASE

2. **Type Safety**:
   - All type references must be resolvable
   - Circular dependencies detection
   - Generic type arguments validation

3. **UML Constraints**:
   - No self-inheritance
   - Abstract classes have abstract methods
   - Multiplicity consistency

4. **Python Constraints**:
   - Valid Python identifiers
   - Reserved keywords not used
   - Parameter ordering (positional before keyword)

## JSON Serialization Format

Example serialized class:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "User",
  "stereotypes": ["entity"],
  "is_abstract": false,
  "base_classes": [],
  "attributes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "username",
      "type": {
        "name": "str",
        "is_optional": false
      },
      "visibility": "public",
      "default_value": null,
      "is_static": false,
      "docstring": "Unique username for the user"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "name": "email",
      "type": {
        "name": "str",
        "is_optional": false
      },
      "visibility": "public",
      "default_value": null,
      "is_static": false
    }
  ],
  "methods": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "name": "authenticate",
      "parameters": [
        {
          "name": "password",
          "type": {
            "name": "str"
          },
          "default_value": null,
          "kind": "positional"
        }
      ],
      "return_type": {
        "name": "bool"
      },
      "visibility": "public",
      "is_static": false,
      "is_class_method": false,
      "is_abstract": false,
      "docstring": "Authenticate user with password.\n\nArgs:\n    password: Password to verify\n\nReturns:\n    True if authentication successful"
    }
  ],
  "decorators": [
    {
      "name": "dataclass",
      "module": "dataclasses",
      "arguments": {}
    }
  ],
  "docstring": "User entity representing a system user.",
  "position": {
    "x": 100.0,
    "y": 150.0,
    "width": 200.0,
    "height": 150.0
  }
}
```

## Mapping to Python Code

### Class Example

**Metamodel:**
```json
{
  "name": "User",
  "attributes": [{"name": "username", "type": {"name": "str"}}],
  "methods": [{"name": "greet", "return_type": {"name": "str"}}]
}
```

**Generated Python:**
```python
class User:
    """User class."""

    def __init__(self):
        self.username: str = ""

    def greet(self) -> str:
        """Greet method."""
        pass
```

## Extension Points

The metamodel is designed for future extensibility:

1. **Custom Stereotypes**: User-defined stereotypes for domain-specific modeling
2. **Constraints**: OCL-like constraint language for validation
3. **Annotations**: Python 3.9+ type annotations (TypedDict, Protocol, etc.)
4. **Pattern Recognition**: Detect and apply design patterns
5. **Multi-language**: Support for Java, TypeScript, C# in future

## Next Steps

1. Implement metamodel classes in Python
2. Add JSON schema validation
3. Create sample models
4. Build transformation to/from Python AST
5. Implement validation rules
