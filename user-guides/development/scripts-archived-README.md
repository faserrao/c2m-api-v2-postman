# Archived Scripts

This directory contains legacy scripts that have been replaced or are no longer used in the current pipeline.

## Archived Scripts by Category

### JQ Scripts (Replaced or Integrated)
- **add_testing_info_block.jq** - Replaced by add_info.jq in jq/
- **add_tests.jq** - Replaced by add_tests.js (JavaScript version)
- **create_env_payload.jq** - Functionality integrated into Makefile
- **create_mock_payload.jq** - Functionality integrated into Makefile
- **full_publish_payload.jq** - Not used in current pipeline
- **link_env_to_mock_payload.jq** - Functionality integrated into Makefile
- **link_payload.jq** - Functionality integrated into Makefile
- **postman_import_payload.jq** - Functionality integrated into Makefile
- **update_mock_env_payload.jq** - Functionality integrated into Makefile
- **update_mock_payload.jq** - Functionality integrated into Makefile
- **update_payload.jq** - Not used
- **url_hardfix_with_paths.jq** - Experimental, not used
- **verify_mock.jq** - Not used

### Python Scripts (Legacy Versions)
- **ebnf_to_openapi_class_based.py** - Earlier version, replaced by ebnf_to_openapi_dynamic_v3.py
- **analyze_endpoint_elements_v2.py** - Analysis script for development
- **extract_endpoint_ebnf_ordered.py** - Analysis script for development

### Shell/JS Scripts (Replaced by Makefile)
- **generate-postman.sh** - Functionality now in Makefile targets
- **quick-validate.sh** - Replaced by Makefile validation targets
- **inject-banner-correctly.js** - Banner injection, unclear if still needed
- **merge-postman.js** - Collection merging, may be useful for complex merges

## Archive Date
August 30, 2025

## Note
These scripts are kept for historical reference and potential future use. They should not be used in the current pipeline without careful review and testing.
