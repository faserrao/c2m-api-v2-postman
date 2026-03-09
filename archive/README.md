# Archive Directory

**Created:** 2026-03-09
**Purpose:** Store superseded, backup, and test files that are no longer actively used

---

## Directory Structure

```
archive/
├── scripts/
│   ├── backups/        - Backup files (.backup, .reverted)
│   ├── v1/             - Version 1 scripts (superseded)
│   ├── v2/             - Version 2 scripts (superseded)
│   └── superseded/     - Other superseded scripts
├── openapi/
│   └── test-specs/     - Test and intermediate OpenAPI specs
└── compressed/         - Compressed archive files
```

---

## Archived Files

### Backup Files (5 items)

**Location:** `archive/scripts/backups/`

1. `ebnf_to_openapi_dynamic_v3.py.backup-2026-02-13` (51KB)
2. `ebnf_to_openapi_dynamic_v3.py.backup-2026-02-16` (51KB)
3. `ebnf_to_openapi_dynamic_v3.py.reverted` (51KB)
4. `generate_curated_collections_v4.py.backup-2026-03-05` (30KB)
5. `generate_use_case_collection_v2.py.backup` (15KB)

**Reason:** Backup copies of active scripts; current versions are in scripts/active/

---

### Version 1 Scripts (3 items)

**Location:** `archive/scripts/v1/`

1. `generate_getting_started_collection.py`
2. `generate_getting_started_with_examples.py`
3. `generate_use_case_collection.py`

**Reason:** Superseded by template-based system (scripts/utilities/generate_getting_started_collections.py)

**Superseded:** 2026-03-08 (template system implemented)

---

### Version 2 Scripts (3 items)

**Location:** `archive/scripts/v2/`

1. `generate_getting_started_collection_v2.py`
2. `generate_getting_started_from_linked_v2.py`
3. `generate_use_case_collection_v2.py`

**Reason:** Superseded by template-based system and v3 versions

**Superseded:** 2026-03-08 (template system) and earlier v3 migrations

---

### Other Superseded Scripts (2 items)

**Location:** `archive/scripts/superseded/`

1. `generate_getting_started_from_linked_v3.py`
   - **Reason:** Superseded by template system
   - **Superseded:** 2026-03-08

2. `add_tests.js`
   - **Reason:** Superseded by JWT-aware version (add_tests_jwt.js)
   - **Superseded:** Earlier (JWT authentication added)

---

### Test OpenAPI Specs (3 items)

**Location:** `archive/openapi/test-specs/`

1. `test-fixed-oneOf-spec.yaml` (30KB)
   - **Purpose:** Test version for oneOf schema fixes
   - **Date:** 2025-10-25

2. `test-with-examples.yaml` (53KB)
   - **Purpose:** Test version with examples
   - **Date:** 2026-02-16

3. `bundled.yaml` (74KB)
   - **Purpose:** Bundled OpenAPI spec (merged overlays)
   - **Date:** 2026-03-06
   - **Note:** Intermediate file, regenerated during build

**Reason:** Test and intermediate files not needed for production builds

---

### Compressed Archives (1 item)

**Location:** `archive/compressed/`

1. `c2mapiv2-openapi-spec-final-with-examples.yaml.zip` (8.7KB)
   - **Date:** 2026-03-07
   - **Reason:** Compressed archive; can be regenerated from source

---

## Active Scripts Inventory

These scripts remain in `scripts/active/` and ARE actively used:

### Core Generation
- `ebnf_to_openapi_dynamic_v3.py` - EBNF to OpenAPI translator (MAIN)
- `merge_openapi_overlays.py` - Merge auth overlay into spec
- `generate_curated_collections_v4.py` - Use case collections (v4 current)

### Collection Processing
- `add_auth_examples.js` - Add auth endpoint examples
- `add_error_responses_to_collection.js` - Add error response examples
- `add_pre_request_script.js` - Inject JWT pre-request script
- `add_response_examples.py` - Add response examples
- `add_tests_jwt.js` - Add tests with JWT awareness (CURRENT)
- `inject_documentation_link.js` - Add Redoc documentation links

### Getting Started (Template System)
- `scripts/utilities/generate_getting_started_collections.py` - NEW template-based generator

### OneOf Processing
- `extract_all_oneof_examples.py` - Extract oneOf examples
- `fix_oneOf_placeholders.js` - Fix placeholder values in oneOf

### Other Active
- `fix_collection_urls_v2.py` - Fix collection URLs with {{baseUrl}}
- `validate_collection.js` - Collection validation
- `addRandomDataToRaw_oneOf.js` - Random data for oneOf fields
- `fix_document_source_identifier.py` - Fix document source identifiers
- `fix_openapi_oneOf_schemas.py` - OneOf schema fixes
- `generate_getting_started_from_linked.py` - Generate from linked (no version = current)
- `generate_getting_started_with_examples_from_test.py` - Generate from test collection
- `generate_use_case_collection_v3.py` - Use case collections (v3 current)
- `add_auth_to_test_collection.js` - Add auth to test collections

---

## Python Cache

**Removed:** `scripts/active/__pycache__/`
- Auto-generated Python bytecode
- Can be regenerated automatically

---

## Restoration Instructions

If you need to restore any archived file:

```bash
# Restore a backup
cp archive/scripts/backups/<filename> scripts/active/

# Restore a v1 script
cp archive/scripts/v1/<filename> scripts/active/

# Restore a test spec
cp archive/openapi/test-specs/<filename> openapi/

# Restore compressed archive
cp archive/compressed/<filename> openapi/
```

---

## Archive Statistics

**Total Files Archived:** 17 files
**Total Size:** ~508KB
**Space Saved:** Minimal (primary benefit is organization)

**Breakdown:**
- Backup files: 5 (198KB)
- v1 scripts: 3 (~30KB)
- v2 scripts: 3 (~30KB)
- Superseded scripts: 2 (~16KB)
- Test specs: 3 (157KB)
- Compressed: 1 (9KB)
- Cache removed: 1 directory (~68KB)

---

## Verification

To verify no active scripts were archived:

```bash
# Check Makefile references
grep -r "generate_getting_started_collection.py" Makefile  # Should be empty
grep -r "add_tests.js" Makefile                             # Should be empty

# Verify active scripts still exist
ls scripts/active/ebnf_to_openapi_dynamic_v3.py            # Should exist
ls scripts/active/add_tests_jwt.js                          # Should exist
ls scripts/utilities/generate_getting_started_collections.py # Should exist
```

---

## Maintenance

- **Review Frequency:** Every 3-6 months
- **Criteria for Permanent Deletion:** Files archived > 1 year with no restoration requests
- **Backup:** Archive directory included in git repository

---

## History

- **2026-03-09:** Initial archive created
  - Archived 17 files (backups, superseded scripts, test specs)
  - Removed __pycache__ directory
  - Organized into categorized subdirectories
