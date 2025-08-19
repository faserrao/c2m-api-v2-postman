# Unused Scripts Analysis and Recommendations

## Overview

This document provides a detailed analysis of the 43 unused scripts found in the `/scripts` directory, with specific recommendations for each script.

## Summary Statistics

- **Total Scripts**: 60
- **Used Scripts**: 17 (28%)
- **Unused Scripts**: 43 (72%)
- **Shell Scripts Unused**: 18/18 (100%)
- **Python Scripts Unused**: 7/10 (70%)
- **JavaScript Scripts Unused**: 1/4 (25%)
- **JQ Scripts Unused**: 17/28 (61%)

## Categorized Recommendations

### 1. KEEP AND INTEGRATE - High Value Scripts (8 scripts)

These scripts provide valuable functionality that should be integrated into the Makefile:

#### Shell Scripts
- **`deploy-docs.sh`** - Automates documentation deployment
  - **Action**: Integrate into `make docs-deploy` target
  - **Benefit**: Streamlines production documentation updates

- **`generate-sdk.sh`** - SDK generation automation
  - **Action**: Create `make generate-sdks` target
  - **Benefit**: Automates client library generation

- **`git-pull-rebase.sh`** - Git workflow automation
  - **Action**: Create `make git-sync` target
  - **Benefit**: Standardizes team git workflow

- **`init-directory-structure.sh`** - Project initialization
  - **Action**: Create `make init-project` target
  - **Benefit**: Helps new developers set up quickly

#### Python Scripts
- **`generate_test_data.py`** - Standalone test data generator
  - **Action**: Integrate as fallback for test data generation
  - **Benefit**: More robust test data generation

- **`verify_urls.py`** - Python-based URL verification
  - **Action**: Use as alternative to jq-based verification
  - **Benefit**: More sophisticated URL validation

#### JavaScript Scripts
- **`merge-postman.js`** - Collection merger
  - **Action**: Integrate for complex collection merging
  - **Benefit**: Better than jq for complex merges

### 2. KEEP FOR MANUAL USE - Utility Scripts (7 scripts)

These scripts are useful for manual operations and debugging:

#### Shell Scripts
- **`git-push.sh`** - Git push automation
  - **Action**: Document in developer guide
  - **Reason**: Useful for CI/CD pipelines

- **`prism_test.sh`** - Additional Prism testing
  - **Action**: Keep for advanced testing scenarios
  - **Reason**: Useful for debugging Prism issues

#### Makefile Maintenance Scripts
- **`makefile-scripts/backup-makefile.sh`**
  - **Action**: Keep for Makefile version control
  - **Reason**: Critical for rollback scenarios

- **`makefile-scripts/check_and_create_makefile_files.sh`**
  - **Action**: Keep for Makefile validation
  - **Reason**: Ensures Makefile integrity

### 3. ARCHIVE - Legacy/Replaced Scripts (15 scripts)

These scripts have been replaced by newer versions or better implementations:

#### Python Scripts
- **`ebnf_to_openapi_grammer_based.py`** - Replaced by class-based version
- **`fix_collection_urls.py`** - Replaced by v2
- **`test_data_generator_for_openapi_specs/add_examples_to_spec copy.py`** - Obvious backup

#### JQ Scripts (replaced by integrated versions)
- **`add_testing_info_block.jq`**
- **`add_tests.jq`** (replaced by add_tests.js)
- **`auto_fix_collection.jq`**
- **`create_env_payload.jq`**
- **`create_mock_payload.jq`**
- **`full_publish_payload.jq`**
- **`link_env_to_mock_payload.jq`**
- **`link_payload.jq`**
- **`postman_import_payload.jq`**
- **`update_mock_env_payload.jq`**
- **`update_mock_payload.jq`**
- **`update_payload.jq`**

**Action**: Move to `scripts/archived/` directory with README explaining their historical purpose

### 4. REMOVE - No Clear Value (13 scripts)

These scripts appear to be experimental or have unclear purposes:

#### Shell Scripts
- **`makefile-scripts/fix-orchestrator.sh`**
- **`makefile-scripts/fix-orchestrator-v2.sh`**
- **`makefile-scripts/fix-orchestrator_v2.sh`** (duplicate naming)
- **`makefile-scripts/make-force-rebuild-change.sh`**
- **`makefile-scripts/mod-force-rebuild.sh`**
- **`makefile-scripts/add-force-rebuild.sh`**
- **`makefile-scripts/undo-make-force-rebuild-change.sh`**
- **`makefile-scripts/normalize.sh`**

#### JQ Scripts
- **`url_hardfix.jq`**
- **`url_hardfix_with_paths.jq`**
- **`verify_mock.jq`**

#### Other
- **`scripts/temp`** - Temporary file
- **`env_template (Unicode Encoding Conflict).jq`** - Corrupted file

**Action**: Delete after confirming with team

### 5. SPECIAL CASES - Need Investigation (2 scripts)

#### Python Scripts
- **`repair_urls.py`** - Unclear if this provides unique functionality
  - **Action**: Review code and compare with fix_collection_urls_v2.py

- **`test_data_generator_for_openapi_specs/test_example.py`**
  - **Action**: Determine if this is a unit test or utility

## Recommended Directory Structure

```
scripts/
├── active/              # Currently used scripts (move here)
├── utilities/           # Manual-use scripts
├── archived/            # Legacy scripts for reference
├── test_data_generator_for_collections/
├── test_data_generator_for_openapi_specs/
├── jq/                  # Active JQ filters only
└── README.md           # Script documentation
```

## Implementation Plan

### Phase 1: Immediate Actions (1 day)
1. Create new directory structure
2. Move active scripts to `active/`
3. Delete obvious temporary/corrupted files
4. Create `scripts/README.md` documenting each directory

### Phase 2: Integration (1 week)
1. Add Makefile targets for high-value scripts:
   ```makefile
   .PHONY: docs-deploy
   docs-deploy: docs-build
   	@./scripts/utilities/deploy-docs.sh
   
   .PHONY: generate-sdks
   generate-sdks:
   	@./scripts/utilities/generate-sdk.sh
   
   .PHONY: git-sync
   git-sync:
   	@./scripts/utilities/git-pull-rebase.sh
   ```

2. Test integrated scripts
3. Update main README with new targets

### Phase 3: Archive and Clean (2 weeks)
1. Move legacy scripts to `archived/` with documentation
2. Create `archived/README.md` explaining each script's history
3. Remove confirmed unnecessary scripts
4. Update `.gitignore` if needed

## Script Documentation Template

For each script in `utilities/` or `active/`, add a header:

```bash
#!/bin/bash
# Script: script-name.sh
# Purpose: Brief description
# Usage: ./script-name.sh [arguments]
# Dependencies: List any required tools
# Author: Original author
# Date: Creation date
# Status: Active|Utility|Deprecated
# Notes: Any special considerations
```

## Benefits of Cleanup

1. **Reduced Confusion**: Developers won't waste time on obsolete scripts
2. **Easier Maintenance**: Clear separation of active vs. legacy code
3. **Better Documentation**: Each script's purpose becomes clear
4. **Improved Onboarding**: New developers understand available tools
5. **Git History Preserved**: Archived scripts maintain history

## Metrics for Success

- Reduce script directory from 60 to ~25 active files
- 100% of active scripts documented
- All high-value scripts integrated into Makefile
- Zero duplicate functionality scripts
- Clear README for each subdirectory

## Next Steps

1. **Review with Team**: Confirm script categorizations
2. **Create Backup**: Before any deletions
3. **Implement Phase 1**: Start with directory restructure
4. **Document Changes**: Update main README
5. **Team Training**: Ensure everyone knows new structure

## Notes on Specific Scripts

### Makefile Scripts Directory
The `makefile-scripts/` directory appears to be from a major Makefile refactoring effort. The presence of:
- Multiple orchestrator fix versions
- Force rebuild scripts
- Backup utilities

Suggests these were used during a complex Makefile restructuring. They should be archived with documentation about the refactoring they supported.

### Duplicate JQ Scripts
Several JQ scripts exist in both the root `scripts/` directory and `scripts/jq/`:
- `fix_urls.jq`
- `sanitize_collection.jq`
- `verify_urls.jq`

The Makefile references the versions in `scripts/jq/`, so the root-level duplicates should be removed.

### Test Data Generators
Both test data generator directories are partially used:
- `test_data_generator_for_collections/` - `addRandomDataToRaw.js` is used
- `test_data_generator_for_openapi_specs/` - `add_examples_to_spec.py` is used

Keep these directories but clean out backup and test files.

## Conclusion

The scripts directory has accumulated technical debt over time, with 72% of scripts being unused. By implementing this cleanup plan, the project will be more maintainable and easier for new developers to understand. The key is preserving valuable utilities while removing confusion-causing duplicates and obsolete scripts.