# Scripts retired 2026-10-17

Moved here during the scripts-directory cleanup. None of them was used by the build,
by CI, or by another active script. Kept for reference only; nothing here is maintained.

| File | Why retired |
|---|---|
| `add_tests_jwt.js` | Only reachable through `make postman-add-jwt-tests`, which tested an undefined variable and never ran. `add_tests.js` adds the Newman tests. Removed with the targets `postman-add-jwt-tests` and `jwt-test` (the latter used an undefined `PROJECT_ROOT`). |
| `fix_openapi_oneOf_schemas.py` | No-op: loaded the base spec and wrote it back unchanged. Removed from `generate-openapi-spec-from-ebnf-dd`; the spec is byte-identical without it. |
| `jq/fix_paths.jq`, `jq/merge.jq` | Defined as Makefile variables, never used. |
| `jq/sanitize_collection.jq` | Only used by `postman-test-collection-fix-examples`, which no build called (target removed). |
| `makefile-scripts/*` | One-off Makefile editing helpers (Aug 2025), referenced nowhere. |
| `utilities/cleanup-{scripts,openapi,docs}-directory.sh` | One-time "possible-trash" reorganisation scripts; targets `cleanup-*` removed. |
| `utilities/archive_legacy_scripts.sh`, `utilities/fix-all-symlinks.sh`, `utilities/fix-symlinks-simple.sh`, `replace-symlinks-for-github.sh` | One-time migration and symlink fixes. |
| `utilities/deploy-docs.sh` | Obsolete: docs are published by CI to the artifacts repository's GitHub Pages; target `deploy-docs` removed. |
| `utilities/fix_document_source_identifier.py` | One-time collection fix. |
| `utilities/verify_mocks.py` | Could not work against this all-POST API (empty bodies are rejected before schema checks). |
| `test_data_generator_for_collections/package*.json` | Dead: no nested `node_modules` exists, so `addRandomDataToRaw.js` loads Faker 9.9.0 from the repo root, not the 8.4.1 pinned here. |
