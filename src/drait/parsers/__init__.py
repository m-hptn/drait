"""
Parsers for DRAIT - extract metamodel from source code.

This package contains parsers that convert source code to DRAIT metamodel.
"""

from .python_parser import PythonParser

__all__ = ["PythonParser"]
