# Project TODO List

This file tracks longer-term improvements, technical debt, and future enhancements.

## Validation System Improvements

### Build Manifest System for Timestamp Validation
**Priority**: Medium
**Complexity**: Medium
**Status**: Planned

**Problem**:
- Validation script checks if files exist on disk but cannot distinguish between:
  - Newly generated files from current build
  - Stale files from previous builds
- This works fine in CI/CD (fresh checkout each time)
- But locally, if a build fails halfway, validation might pass by checking old files
- With incremental builds, validation doesn't know which files SHOULD have been regenerated

**Current Workaround**:
- CI/CD always does fresh checkout (no stale files)
- Local developers manually clean when needed

**Proposed Solution - Build Manifest System**:

Each build target writes a manifest declaring what it produces:
```bash
# .build-state/manifest
BUILD_TARGET=postman-instance-build-without-tests
BUILD_START_TIME=1699123456
BUILD_EXPECTED_OUTPUTS=postman/generated/*.json,docs/index.html,openapi/bundled.yaml
```

Validation reads manifest and checks:
1. Files in EXPECTED_OUTPUTS exist
2. Files in EXPECTED_OUTPUTS are newer than BUILD_START_TIME
3. Files NOT in EXPECTED_OUTPUTS can be any age (from previous incremental builds)

**Benefits**:
- Works correctly for full builds, incremental builds, and partial builds
- Each target explicitly declares what it produces
- Validation is precise - only checks what should be new
- Foundation for smarter rebuild system

**Implementation Notes**:
- Add `.build-state/` to `.gitignore`
- Create Makefile helper function: `write_build_manifest(target, outputs)`
- Update validation script to read and check manifest
- Handle CI/CD (fresh checkout, no manifest needed) gracefully

**Related Files**:
- `tests/validate-pipeline-outputs.sh` - Validation script
- `Makefile` - Build targets (postman-instance-build-with-tests, postman-instance-build-without-tests)
- `.github/workflows/api-ci-cd.yml` - CI/CD workflow

**Discussion Date**: 2025-11-04
**Raised By**: User during validation system review

---

## Other Future Improvements

(Add additional items as they come up)
