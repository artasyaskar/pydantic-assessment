#!/usr/bin/env python3
"""Parser for test results."""

import json
import sys
from pathlib import Path


def parse_test_results(output_path: str = None) -> dict:
    """Parse test results and return structured data."""
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": [],
        "fail_to_pass": [],
        "pass_to_pass": []
    }
    
    # Read pytest output if available
    if output_path and Path(output_path).exists():
        with open(output_path) as f:
            content = f.read()
            
        # Parse pytest output
        for line in content.split('\n'):
            if 'passed' in line and 'failed' in line:
                parts = line.split(',')
                for part in parts:
                    part = part.strip()
                    if 'passed' in part:
                        try:
                            results['passed'] = int(part.split()[0])
                        except (ValueError, IndexError):
                            pass
                    elif 'failed' in part:
                        try:
                            results['failed'] = int(part.split()[0])
                        except (ValueError, IndexError):
                            pass
    
    results['total'] = results['passed'] + results['failed']
    
    return results


def main():
    """Main entry point."""
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    results = parse_test_results(output_file)
    print(json.dumps(results, indent=2))
    
    # Exit with error code if tests failed
    if results['failed'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
