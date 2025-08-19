# Claude Code Task Specification

## Goal
Generate a program that:
1. Takes an OpenAPI specification file (JSON or YAML) as input.
2. Automatically adds minimal placeholder `examples` for each response schema where examples are missing.
3. Outputs a new OpenAPI spec file with the same name as the input file, but with `-with-examples` appended before the extension.

**Example:**
- Input: `c2m_openapi_spec_final.yaml`
- Output: `c2m_openapi_spec_final-with-examples.yaml`

## Requirements
- Detect if the input file is `.yaml` or `.json`.
- Add examples such as:
  - `"example": "string-example"` for `type: string`
  - `"example": 123` for `type: integer`
  - `"example": 1.23` for `type: number`
  - `"example": true` for `type: boolean`
- Preserve the structure of the original OpenAPI document.
- Maintain compatibility with OpenAPI 3.0 or 3.1 specifications.
- Use a CLI interface:
  ```bash
  python add_examples.py input_spec.yaml
