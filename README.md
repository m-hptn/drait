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

🚧 **Early Development** - This project is currently in the architecture and planning phase.

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
- [ ] Python AST parser implementation
- [ ] Code generator with templates
- [ ] Diagram editor UI (React + Canvas/SVG)
- [ ] Synchronization engine
- [ ] Conflict resolution mechanism
- [ ] Desktop application (Electron)
- [ ] Testing suite
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
