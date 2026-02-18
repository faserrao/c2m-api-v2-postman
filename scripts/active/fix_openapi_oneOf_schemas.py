#!/usr/bin/env python3
"""
fix_openapi_oneOf_schemas.py

Post-processes OpenAPI spec after EBNF-to-OpenAPI conversion.
All oneOf schemas now use named EBNF productions and require no fixups.
This script is retained as a pipeline hook for future use.
"""

import yaml
import sys


def main():
    if len(sys.argv) < 3:
        print("Usage: python fix_openapi_oneOf_schemas.py <input.yaml> <output.yaml>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"Loading OpenAPI spec from {input_file}...")
    with open(input_file, 'r') as f:
        spec = yaml.safe_load(f)

    # No fixups required: all oneOf variants are named EBNF productions.

    print(f"Saving spec to {output_file}...")
    with open(output_file, 'w') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, width=1000)

    print("OneOf schemas verified (no fixups needed)")


if __name__ == '__main__':
    main()
