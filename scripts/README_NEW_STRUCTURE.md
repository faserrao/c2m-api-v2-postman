# Scripts Directory Reorganization Plan

## Current Status: Planning Phase
**DO NOT MOVE FILES YET** - This is the planned structure for reorganization.

## Proposed Directory Structure

```
scripts/
├── active/              # Scripts currently used by Makefile
├── utilities/           # Useful scripts for manual operations
├── archived/            # Legacy/replaced scripts (historical reference)
├── jq/                  # (existing) Active JQ filters
├── test_data_generator_for_collections/    # (existing)
├── test_data_generator_for_openapi_specs/  # (existing)
├── python_env/          # (existing) Python virtual environment
└── makefile-scripts/    # (existing - to be reviewed)
```

## Migration Plan

### Phase 1: Preparation (CURRENT PHASE)
1. YES Create directory structure
2. Document all file movements needed
3. Identify all Makefile references that need updating
4. Create migration script to automate the process

### Phase 2: Migration (NOT STARTED)
1. Run migration script in test mode
2. Update all Makefile paths
3. Test entire pipeline
4. Commit changes

### Phase 3: Cleanup (FUTURE)
1. Remove empty directories
2. Update documentation
3. Remove deprecated scripts

## Files to Move to `active/`
These scripts are currently referenced in the Makefile:

1. `ebnf_to_openapi_dynamic_v3.py` → active/
2. `add_tests.js` → active/
3. `fix_collection_urls_v2.py` → active/
4. `validate_collection.js` → active/
5. `fix_request_urls.py` → active/
6. `add_tests_jwt.js` → active/
7. `add_collection_variables.js` → active/
8. `fix-template-banner.sh` → active/

## Files to Move to `utilities/`
Useful scripts for manual operations:

1. `prism_test.sh` → utilities/
2. `generate-sdk.sh` → utilities/
3. `deploy-docs.sh` → utilities/
4. `git-pull-rebase.sh` → utilities/
5. `git-push.sh` → utilities/
6. `cleanup-scripts-directory.sh` → utilities/
7. `cleanup-openapi-directory.sh` → utilities/
8. `cleanup-docs-directory.sh` → utilities/
9. `generate_test_data.py` → utilities/
10. `verify_urls.py` → utilities/

## Files to Move to `archived/`
Legacy or replaced scripts:

1. `ebnf_to_openapi_grammer_based.py` → archived/
2. `fix_collection_urls.py` → archived/ (replaced by v2)
3. All unused JQ scripts → archived/jq/
4. `generate_openapi_from_swagger.py` → archived/
5. `merge_yaml_files.py` → archived/

## Makefile Variables That Need Updating

When we migrate, these variables need path updates:

```makefile
EBNF_TO_OPENAPI_SCRIPT := scripts/active/ebnf_to_openapi_dynamic_v3.py
ADD_TESTS_SCRIPT := scripts/active/add_tests.js
FIX_COLLECTION_URLS := scripts/active/fix_collection_urls_v2.py
POSTMAN_VALIDATOR := scripts/active/validate_collection.js
# ... etc
```

## DO NOT PROCEED WITHOUT:
1. Full backup of scripts directory
2. Testing migration script
3. Confirming all pipeline tests pass
4. Team approval

---
**Last Updated**: August 30, 2025
**Status**: PLANNING - DO NOT EXECUTE YET