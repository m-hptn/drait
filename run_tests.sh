#!/bin/bash
# Simple test runner for DRAIT

# Run tests using Python's unittest discovery as fallback if pytest not available
if command -v pytest &> /dev/null; then
    echo "Running tests with pytest..."
    pytest
elif python3 -m pytest --version &> /dev/null 2>&1; then
    echo "Running tests with python3 -m pytest..."
    python3 -m pytest
else
    echo "pytest not found. Installing pytest..."
    echo "Please install pytest manually:"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "Or run: python3 -m pip install --user pytest pytest-cov"
    exit 1
fi
