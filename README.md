# DRAIT - Model-Driven Development Tool

**D**iagram **R**eal-time **A**rchitecture **I**nteraction **T**ool

A Model-Driven Development (MDD) tool that enables software developers and architects to seamlessly work with visual class diagrams and auto-generated code with real-time bidirectional synchronization.

## Features

- **Visual Class Diagram Editor**: Interactive drawing interface for creating and editing UML class diagrams
- **Code Generation**: Automatic Python code generation from class diagrams
- **Reverse Engineering**: Automatic class diagram generation from existing Python code
- **Real-time Synchronization**: Bidirectional live updates between diagrams and code
- **Developer Workflow Integration**: Seamless integration into software development processes

## Status

🚧 **Active Development** - Core metamodel and Python parser are complete. Working on code generation next.

### Completed Features

✅ **Core Metamodel** ([src/drait/metamodel.py](src/drait/metamodel.py))
- Complete UML class diagram representation
- Support for classes, attributes, methods, parameters, relationships
- Advanced type references with generics support
- JSON serialization for git-friendly storage

✅ **Python AST Parser** ([src/drait/parsers/python_parser.py](src/drait/parsers/python_parser.py))
- **Phase 1**: Extract classes, attributes, methods with visibility detection
- **Phase 2**: Advanced type annotations (List[T], Dict[K,V], Optional, Union, nested generics)
- **Phase 3**: Automatic relationship inference
  - Inheritance from base classes
  - Composition for owned objects
  - Aggregation for shared/optional references
  - Dependencies from method signatures
- **Phase 4**: Advanced Python features
  - Abstract classes (ABC) and abstract methods
  - Decorators (@dataclass, @property, @staticmethod, custom decorators)
  - Properties with getter/setter/deleter
  - Dataclasses with arguments and field metadata
  - Protocol classes (typing.Protocol)

✅ **PlantUML Exporter** ([src/drait/exporters/plantuml.py](src/drait/exporters/plantuml.py))
- Export metamodel to PlantUML diagrams
- Full support for all relationship types
- Preserves type information including generics

## Installation

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver:

```bash
# Install from local directory
cd drait
uv pip install -e .

# Or install from git repository
uv pip install git+https://github.com/m-hptn/drait.git
```

### Using pip

```bash
# Install from local directory
pip install -e .

# Or install from git repository
pip install git+https://github.com/m-hptn/drait.git
```

### Development Installation

For development with testing tools:

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

## Quick Start

### Command-Line Usage

After installation, you can use the `drait-parse` command to parse Python files and generate UML diagrams:

```bash
# With uv (recommended)
uv run drait-parse mycode.py

# Or if installed in active virtual environment
drait-parse mycode.py

# Save diagram to file
uv run drait-parse mycode.py -o diagram.puml

# Parse with custom project name
uv run drait-parse mycode.py --name "My Project" -o diagram.puml

# Show statistics about the parsed code
uv run drait-parse mycode.py --stats
```

**Note**: If using `uv`, prefix commands with `uv run`. If you've installed in a virtual environment (`python -m venv` or `uv venv`), activate it first and run commands directly.

### Python API Usage

You can also use DRAIT as a Python library:

```python
from drait import parse_file_to_project, PlantUMLExporter

# Parse Python file
project = parse_file_to_project("mycode.py", "MyProject")

# Export to PlantUML
exporter = PlantUMLExporter()
plantuml_code = exporter.export_project(project)

# Save or print
print(plantuml_code)
```

### Example: Parse Your Own Code

```bash
# Parse the DRAIT parser itself!
uv run drait-parse src/drait/parsers/python_parser.py -o parser_diagram.puml --stats

# Output:
# Project: python_parser
# Package: python_parser
# Classes: 1
# Relationships: 0
# Total methods: 25+
# PlantUML diagram written to: parser_diagram.puml
```

### Real-World Example

Parse your own Python code from anywhere:

```bash
# Navigate to your project
cd /path/to/your/project

# Parse a single file
uv run --with drait drait-parse src/mymodule.py -o diagram.puml --stats

# Or install drait first, then use it multiple times
uv pip install drait
uv run drait-parse src/file1.py -o diagram1.puml
uv run drait-parse src/file2.py -o diagram2.puml
```

## Documentation

Comprehensive architecture documentation is available in the [docs/arc42](docs/arc42/) directory, following the arc42 template:

- [Architecture Documentation Source](docs/arc42/src/docs/arc42.adoc) - AsciiDoc source files
- [Local Build Instructions](docs/arc42/README.md) - How to render documentation locally

### Local Documentation Build

To generate HTML documentation locally:

```bash
cd docs/arc42
curl -Lo dtcw https://raw.githubusercontent.com/docToolchain/docToolchain/ng/dtcw
chmod +x dtcw
./dtcw generateHTML
xdg-open build/html5/arc42.html
```

> **Note**: A GitHub Actions workflow is configured in [.github/workflows/docs.yml](.github/workflows/docs.yml) that will automatically build and deploy documentation to GitHub Pages when the repository becomes public.

## Project Structure

```
drait/
├── docs/
│   └── arc42/              # Architecture documentation (arc42 template)
│       ├── src/docs/       # AsciiDoc source files
│       └── README.md       # Documentation build instructions
├── src/                    # Source code (coming soon)
├── tests/                  # Test suite (coming soon)
└── README.md              # This file
```

## Technology Stack (Planned)

- **Backend**: Python 3.8+ for code generation and parsing
- **Frontend**: Electron + React + TypeScript for cross-platform UI
- **Code Parsing**: Python AST module
- **Code Generation**: Template-based with Jinja2
- **Diagram Storage**: JSON format (Git-friendly)
- **Target Platform**: Desktop application (Windows, macOS, Linux)

## Key Design Principles

1. **Real-time Performance**: Changes reflected in < 500ms
2. **Accuracy**: Semantic correctness in bidirectional transformations
3. **Usability**: Intuitive for both architects and developers
4. **Extensibility**: Plugin architecture for future language support
5. **Reliability**: No data loss during synchronization

## Roadmap

- [x] Architecture documentation (arc42)
- [x] Core metamodel design
- [x] PlantUML diagram export
- [x] Python AST parser implementation (Phase 1-4 complete)
  - [x] Phase 1: Class, attribute, and method extraction
  - [x] Phase 2: Advanced type annotations (generics, Optional, Union)
  - [x] Phase 3: Relationship inference (inheritance, composition, aggregation, dependency)
  - [x] Phase 4: Advanced features (ABC, decorators, properties, dataclasses)
- [ ] Code generator with templates
- [ ] Interactive diagram viewer (web-based)
- [ ] Diagram editor UI (React + Canvas/SVG)
- [ ] Synchronization engine
- [ ] Conflict resolution mechanism
- [ ] Desktop application (Electron)
- [ ] User documentation
- [ ] Beta release

## Contributing

This project is in early stages. Contribution guidelines will be added as the project matures.

## License

[To be determined]

## Architecture Highlights

The system is built on three key architectural patterns:

- **MVVM (Model-View-ViewModel)**: Separating diagram/code models from presentation
- **Event-Driven Architecture**: Real-time synchronization through file watchers and UI events
- **Bidirectional Transformation**: Forward (diagram → code) and backward (code → diagram) transformations

For detailed architecture information, see the [architecture documentation](docs/arc42/README.md).

## Contact

Project maintained by the DRAIT development team.

---

*Generated with care for software architects and developers who believe in the power of visual modeling and clean code.*
