# Data Dictionary Directory

This directory contains the EBNF (Extended Backus-Naur Form) data dictionary that serves as the single source of truth for the C2M API specification.

## Directory Contents

### Files

#### `c2mapiv2-dd.ebnf`
The main EBNF data dictionary file that defines all data structures, types, and relationships for the C2M API v2.
- **Purpose**: Primary source for API data models
- **Format**: EBNF notation
- **Usage**: Converted to OpenAPI specification via `make generate-openapi-spec-from-ebnf-dd`

#### `Awesome—here's a clean, implementation-r.yml`
YAML configuration file for implementation details.
- **Purpose**: Additional implementation metadata
- **Format**: YAML

#### `GitHub Actions deployment.pdf`
Documentation for GitHub Actions deployment process.
- **Purpose**: Reference guide for CI/CD deployment
- **Format**: PDF document

## EBNF to OpenAPI Workflow

1. **Edit EBNF**: Modify `c2mapiv2-dd.ebnf` to update data models
2. **Convert**: Run `make generate-openapi-spec-from-ebnf-dd`
3. **Result**: Generates OpenAPI spec in `openapi/` directory

## EBNF Format Guide

The EBNF format follows standard notation:
- `::=` - Definition
- `|` - Alternative
- `[]` - Optional
- `{}` - Repetition (0 or more)
- `()` - Grouping
- `""` - Literal strings

### Example EBNF Definition
```ebnf
RecipientAddress ::= {
    "line1" : String,
    ["line2" : String],
    "city" : String,
    "state" : StateCode,
    "zip" : ZipCode
}
```

## Making Changes

1. Always edit the EBNF file first - it's the source of truth
2. Run conversion to update OpenAPI spec
3. Test changes with mock server
4. Commit both EBNF and generated files

## Related Documentation

- [OpenAPI Directory](../openapi/README.md) - Generated specifications
- [Scripts Directory](../scripts/README.md) - Conversion scripts
- [Root README](../README.md) - Project overview