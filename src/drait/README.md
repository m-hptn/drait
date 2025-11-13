# DRAIT Metamodel

The core metamodel for the DRAIT Model-Driven Development Tool.

## Overview

The metamodel defines how class diagrams are represented internally in DRAIT. It provides a structured way to model UML class diagrams with full support for Python-specific features like type hints, decorators, and visibility modifiers.

## Key Features

- **UML 2.5 Compliant**: Follows UML class diagram semantics
- **Python-Optimized**: Full support for Python type hints, decorators, and conventions
- **JSON Serialization**: Git-friendly persistence format
- **Type-Safe**: Leverages Python dataclasses and type hints
- **Extensible**: Designed for future language support

## Quick Start

```python
from drait.metamodel import Class, Attribute, TypeReference, Visibility

# Create a simple class
person = Class(
    name="Person",
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
    ],
)

# Serialize to JSON
json_data = person.to_dict()

# Deserialize from JSON
loaded_person = Class.from_dict(json_data)
```

## Core Entities

### Project
Top-level container for all model elements. Contains packages and global metadata.

### Package
Represents a Python module/package. Groups related classes and their relationships.

### Class
Represents a Python class with attributes, methods, decorators, and inheritance.

### Attribute
Class attribute/field with type information, visibility, and default values.

### Method
Class method with parameters, return type, decorators, and optional body.

### Relationship
Connection between classes (inheritance, association, composition, etc.).

### TypeReference
Type information with support for generics (`List[str]`, `Dict[str, int]`, etc.).

## Examples

See the [examples directory](../../examples/) for complete examples:

- `simple_example.py` - Basic class diagram creation
- `simple_class_diagram.json` - Serialized example

## Documentation

For detailed metamodel design documentation, see:
- [docs/design/metamodel.md](../../docs/design/metamodel.md)

## Architecture

The metamodel is the foundation for:

1. **Diagram Editor**: Visual representation of classes
2. **Code Generator**: Transforms metamodel to Python code
3. **Code Parser**: Extracts metamodel from Python AST
4. **Synchronization Engine**: Maintains bidirectional consistency

## Future Extensions

- Support for additional diagram types (sequence, component)
- Multi-language support (Java, TypeScript, C#)
- Custom stereotypes and constraints
- Design pattern recognition
