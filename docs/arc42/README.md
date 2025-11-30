# Architecture Documentation - Model-Driven Development Tool

This directory contains the arc42 architecture documentation for the Model-Driven Development Tool.

## Structure

```
docs/arc42/
├── src/
│   └── docs/
│       ├── arc42.adoc                    # Main documentation file
│       ├── chapters/                     # Individual arc42 chapters
│       │   ├── 01_introduction_and_goals.adoc
│       │   ├── 02_architecture_constraints.adoc
│       │   ├── 03_system_scope_and_context.adoc
│       │   ├── 04_solution_strategy.adoc
│       │   ├── 05_building_block_view.adoc
│       │   ├── 06_runtime_view.adoc
│       │   ├── 07_deployment_view.adoc
│       │   ├── 08_concepts.adoc
│       │   ├── 09_architecture_decisions.adoc
│       │   ├── 10_quality_requirements.adoc
│       │   ├── 11_risks_and_technical_debt.adoc
│       │   └── 12_glossary.adoc
│       └── images/                       # Diagrams and images
├── Config.groovy                         # docToolchain configuration
├── docToolchainConfig.groovy            # Alternative config format
└── README.md                            # This file
```

## About arc42

arc42 is a template for architecture communication and documentation. It provides a standardized structure for documenting software architectures.

Learn more at: https://arc42.org/

## About docToolchain

docToolchain is a collection of tools for documentation, especially for software architecture documentation. It uses AsciiDoc format and can generate HTML, PDF, and other output formats.

Learn more at: https://doctoolchain.github.io/docToolchain/

## Prerequisites

To render this documentation, you'll need:

- Java 11 or higher (for docToolchain)
- Git (for cloning docToolchain)

## Rendering Documentation

### Option 1: Using AsciiDoctor directly (simplest)

If you just want to generate HTML without all docToolchain features:

1. Install AsciiDoctor:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install asciidoctor

   # On macOS
   brew install asciidoctor

   # Or using Ruby gem
   gem install asciidoctor
   ```

2. Generate HTML:
   ```bash
   cd docs/arc42/src/docs
   asciidoctor arc42.adoc -o ../../build/arc42.html
   ```

3. Open the generated file:
   ```bash
   xdg-open ../../build/arc42.html
   ```

Note: This won't render PlantUML diagrams. For full diagram support, use Option 2 or 3 below.

### Option 2: Using docToolchain wrapper (full features)

1. Download the docToolchain wrapper (run from the docs/arc42 directory):
   ```bash
   cd docs/arc42
   curl -Lo dtcw https://raw.githubusercontent.com/docToolchain/docToolchain/ng/dtcw
   chmod +x dtcw
   ```

2. Generate HTML documentation:
   ```bash
   ./dtcw generateHTML
   ```

3. Generate PDF documentation:
   ```bash
   ./dtcw generatePDF
   ```

4. Output will be in the `build/html5/` directory

5. View the generated documentation:
   ```bash
   # Open in default browser
   xdg-open build/html5/arc42.html

   # Or navigate to: docs/arc42/build/html5/arc42.html
   ```

**Note:** If you downloaded dtcw in a different directory, either move it to `docs/arc42/` or use the full path like `/path/to/dtcw generateHTML` when running from the `docs/arc42/` directory.

### Option 3: Using Docker

```bash
docker run --rm -v ${PWD}:/project -w /project/docs/arc42 \
  doctoolchain/doctoolchain:latest generateHTML
```

### Option 4: Install docToolchain locally

1. Install docToolchain following instructions at https://doctoolchain.github.io/docToolchain/

2. Navigate to this directory and run:
   ```bash
   doctoolchain . generateHTML
   ```

## Viewing the Documentation

After generation, the documentation will be at:
- **docToolchain**: `docs/arc42/build/html5/arc42.html`
- **AsciiDoctor**: `docs/arc42/build/arc42.html` (or wherever you specified with -o)

Open the file in your web browser:
```bash
xdg-open docs/arc42/build/html5/arc42.html
```

## Editing Documentation

The documentation is written in AsciiDoc format. You can edit the `.adoc` files with any text editor.

For better AsciiDoc editing experience, consider:
- VS Code with AsciiDoc extension
- IntelliJ IDEA with AsciiDoc plugin
- Atom with AsciiDoc preview

## Documentation Sections

1. **Introduction and Goals** - Overview, requirements, quality goals, stakeholders
2. **Architecture Constraints** - Technical, organizational, and convention constraints
3. **System Scope and Context** - Business and technical context
4. **Solution Strategy** - Key technology decisions and architectural patterns
5. **Building Block View** - Static decomposition of the system
6. **Runtime View** - Behavior and interaction scenarios
7. **Deployment View** - Infrastructure and deployment
8. **Cross-cutting Concepts** - Domain model, UX, persistence, security concepts
9. **Architecture Decisions** - Important decisions and their rationale (ADRs)
10. **Quality Requirements** - Quality scenarios and requirements
11. **Risks and Technical Debt** - Known risks and accepted technical debt
12. **Glossary** - Important terms and acronyms

## Contributing

When updating documentation:

1. Follow the arc42 template structure
2. Use AsciiDoc syntax
3. Place images in `src/docs/images/`
4. Use PlantUML for diagrams (inline in `.adoc` files)
5. Update this README if adding new sections or changing structure

## License

[Add your license information here]
