# OpenAPI Directory Cleanup Summary

## Overview
Cleaned up the openapi directory by removing backup files and an unusual file.

## Space Saved: 64 KB

## Files Moved:

### 1. **Timestamped Backup Files** (2 files)
- `c2mapiv2-openapi-spec-final.yaml.082020252137` - Backup from Aug 20, 2025
  - Old title: "LOB-Style Document Submission API"
  - Smaller size: 20KB vs current 37KB
- `c2mapiv2-openapi-spec-final-with-examples.yaml.082020252211` - Backup from Aug 20, 2025

### 2. **Unusual Files** (1 file)
- `...` - An OpenAPI spec with unusual filename (21KB)
  - Title: "Click2Mail Document Submission API"
  - Appears to be an older/different version
  - No clear purpose for the unusual name

## Files Kept (Essential):

1. **`c2mapiv2-openapi-spec-final.yaml`** (37KB)
   - Main OpenAPI specification
   - Title: "C2M API v2 - Auth Overlay"
   - Referenced as `C2MAPIV2_OPENAPI_SPEC` in Makefile

2. **`c2mapiv2-openapi-spec-base.yaml`** (27KB)
   - Base specification (before overlay merge)
   - Title: "C2M Job Submission API"
   - Referenced as `C2MAPIV2_OPENAPI_SPEC_BASE` in Makefile

3. **`bundled.yaml`** (38KB)
   - Bundled/merged specification
   - Referenced as `OPENAPI_BUNDLED_FILE` in Makefile
   - Contains auth endpoints from overlay

4. **`c2mapiv2-openapi-spec-final-with-examples.yaml`** (21KB)
   - Specification with examples
   - Used by `PRISM_SPEC` for mock server
   - Can be regenerated with `make postman-openapi-spec-add-examples`

5. **`overlays/`** directory
   - Contains `auth.tokens.yaml` - JWT authentication overlay
   - Essential for auth endpoint definitions

## Directory Structure After Cleanup:
```
openapi/
├── bundled.yaml                              # Merged spec with auth
├── c2mapiv2-openapi-spec-base.yaml         # Base spec (no auth)
├── c2mapiv2-openapi-spec-final.yaml        # Final spec
├── c2mapiv2-openapi-spec-final-with-examples.yaml  # With examples for testing
└── overlays/
    └── auth.tokens.yaml                     # JWT auth overlay
```

## Result:
- Removed 3 unnecessary files
- OpenAPI directory is now clean with only essential specs
- All files have clear purposes and are referenced in the build process
- Backup files from August 20 development session have been archived