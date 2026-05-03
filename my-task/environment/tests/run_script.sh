#!/bin/bash
set -e

echo "Running test script..."

cd /workspace/pydantic

# Run pytest on the test file
python -m pytest tests/test_validate_default_factory.py -v --tb=short
