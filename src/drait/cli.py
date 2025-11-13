"""
Command-line interface for DRAIT.

Provides easy-to-use commands for parsing Python code and exporting diagrams.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from drait.parsers.python_parser import parse_file_to_project
from drait.exporters.plantuml import PlantUMLExporter


def parse_command():
    """
    Parse Python file and generate PlantUML diagram.

    Usage:
        drait-parse myfile.py
        drait-parse myfile.py -o diagram.puml
        drait-parse myfile.py --output diagram.puml --name MyProject
    """
    parser = argparse.ArgumentParser(
        description="Parse Python code and generate UML class diagram",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse file and output to console
  drait-parse mycode.py

  # Parse and save to file
  drait-parse mycode.py -o diagram.puml

  # Parse with custom project name
  drait-parse mycode.py --name "My Project" -o diagram.puml

  # Parse and show statistics
  drait-parse mycode.py --stats
        """
    )

    parser.add_argument(
        "input_file",
        type=str,
        help="Python source file to parse"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file for PlantUML diagram (default: print to stdout)"
    )

    parser.add_argument(
        "-n", "--name",
        type=str,
        help="Project name for diagram title (default: filename)"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics about parsed code"
    )

    parser.add_argument(
        "--no-relationships",
        action="store_true",
        help="Exclude relationships from diagram"
    )

    args = parser.parse_args()

    # Check if input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    if not input_path.is_file():
        print(f"Error: Not a file: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    # Parse the file
    try:
        project = parse_file_to_project(str(input_path), args.name)
    except Exception as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        sys.exit(1)

    # Show statistics if requested
    if args.stats:
        package = project.packages[0]
        print(f"Project: {project.name}")
        print(f"Package: {package.name}")
        print(f"Classes: {len(package.classes)}")
        print(f"Relationships: {len(package.relationships)}")
        print()

        # Count features
        abstract_classes = sum(1 for cls in package.classes if cls.is_abstract)
        dataclasses = sum(1 for cls in package.classes
                         if any(d.name == "dataclass" for d in cls.decorators))
        total_methods = sum(len(cls.methods) for cls in package.classes)
        abstract_methods = sum(1 for cls in package.classes
                              for m in cls.methods if m.is_abstract)

        print("Features:")
        print(f"  Abstract classes: {abstract_classes}")
        print(f"  Dataclasses: {dataclasses}")
        print(f"  Total methods: {total_methods}")
        print(f"  Abstract methods: {abstract_methods}")
        print()

    # Export to PlantUML
    exporter = PlantUMLExporter()
    plantuml_code = exporter.export_project(project)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(plantuml_code)
        print(f"PlantUML diagram written to: {args.output}")
    else:
        print(plantuml_code)


def export_command():
    """
    Export existing DRAIT JSON model to PlantUML.

    Usage:
        drait-export model.json
        drait-export model.json -o diagram.puml
    """
    parser = argparse.ArgumentParser(
        description="Export DRAIT model to PlantUML diagram"
    )

    parser.add_argument(
        "model_file",
        type=str,
        help="DRAIT JSON model file"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file for PlantUML diagram (default: print to stdout)"
    )

    args = parser.parse_args()

    # This would load from JSON and export
    # For now, just show a message
    print("Note: JSON import/export not yet implemented")
    print("Use drait-parse to parse Python files directly")
    sys.exit(1)


def main():
    """
    Main entry point for drait command.

    Usage:
        drait parse <file.py>
        drait export <model.json>
        drait --help
    """
    parser = argparse.ArgumentParser(
        description="DRAIT - Model-Driven Development Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  parse      Parse Python code and generate UML diagram
  export     Export DRAIT model to PlantUML

For command-specific help:
  drait parse --help
  drait export --help

Quick start:
  drait parse mycode.py -o diagram.puml

Or use the direct commands:
  drait-parse mycode.py -o diagram.puml
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version="DRAIT 0.1.0"
    )

    parser.add_argument(
        "command",
        nargs="?",
        choices=["parse", "export"],
        help="Command to execute"
    )

    # Parse just the command
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args, remaining = parser.parse_known_args()

    if args.command == "parse":
        # Reconstruct argv for parse_command
        sys.argv = ["drait-parse"] + remaining
        parse_command()
    elif args.command == "export":
        sys.argv = ["drait-export"] + remaining
        export_command()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
