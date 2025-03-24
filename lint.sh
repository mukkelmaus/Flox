#!/bin/bash
# Linting script for OneTask API
# This script checks the code for common issues and errors

echo "Running linting checks for OneTask API..."

# Run flake8 if installed
if command -v flake8 &> /dev/null
then
    echo "Running flake8..."
    flake8 app tests
else
    echo "flake8 not installed, skipping"
fi

# Check for Pydantic V2 warnings
echo "Checking for Pydantic V2 compatibility issues..."
grep -r "orm_mode" app/schemas/

# Check for unhandled exceptions
echo "Checking for try blocks without except..."
grep -r -A 2 "try:" app/ | grep -v "except"

# Check for environment variables
echo "Checking for hardcoded environment variables that should be configurable..."
grep -r "os.environ\[" app/

echo "Linting completed!"