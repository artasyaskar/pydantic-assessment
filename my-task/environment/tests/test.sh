#!/bin/bash
set -e

echo "Running validate_default factory tests..."

cd /workspace/pydantic

# Run the specific test file
python -m pytest tests/test_validate_default_factory.py -v

echo "All tests passed!"
