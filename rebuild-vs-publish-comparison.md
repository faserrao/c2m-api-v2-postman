# Rebuild Orchestrators vs Publish Targets - Redundancy Analysis

## 1. Targets Called by Rebuild Orchestrators

### `rebuild-all-with-delete`
```makefile
1. postman-cleanup-all
2. rebuild-all-no-delete
   └── install
   └── generate-and-validate-openapi-spec
   └── postman-instance-build-and-test
```

### `rebuild-all-no-delete`
```makefile
1. install
2. generate-and-validate-openapi-spec
3. postman-instance-build-and-test
   ├── postman-login
   ├── postman-import-openapi-spec
   │   └── postman-import-openapi-as-api
   ├── postman-spec-create-standalone
   ├── postman-create-linked-collection
   │   ├── postman-api-linked-collection-generate
   │   ├── postman-linked-collection-flatten
   │   ├── postman-linked-collection-upload
   │   └── postman-linked-collection-link
   ├── postman-create-test-collection
   ├── postman-create-mock-and-env
   ├── prism-start
   ├── postman-mock
   └── postman-docs-build-and-serve-up
```

## 2. Targets Called by Publish Targets

### `postman-publish-personal` and `postman-publish-team`
Both targets call the exact same sequence (only difference is workspace/API key):

```makefile
1. Save target to .postman-target (if not SKIP_TARGET_SAVE)
2. workspace-info
3. postman-cleanup-all
4. postman-import-openapi-as-api
5. postman-spec-create-standalone
6. postman-linked-collection-upload
7. postman-linked-collection-link
8. postman-create-test-collection
9. postman-create-mock-and-env
10. postman-import-openapi-spec
```

## 3. Comparison Analysis

### What's the Same

Both workflows include these core Postman operations:
- `postman-cleanup-all` (in rebuild-all-with-delete)
- `postman-import-openapi-spec` / `postman-import-openapi-as-api`
- `postman-spec-create-standalone`
- `postman-linked-collection-upload`
- `postman-linked-collection-link`
- `postman-create-test-collection`
- `postman-create-mock-and-env`

### What's Different

**Rebuild Orchestrators Include:**
- `install` - Install dependencies
- `generate-and-validate-openapi-spec` - Build OpenAPI from EBNF
- `postman-login` - Authenticate
- `postman-api-linked-collection-generate` - Generate collection
- `postman-linked-collection-flatten` - Flatten collection
- `prism-start` - Start local mock server
- `postman-mock` - Run tests
- `postman-docs-build-and-serve-up` - Generate and serve docs

**Publish Targets Include:**
- `.postman-target` file management
- `workspace-info` - Display workspace details
- Direct workspace/API key overrides

### Key Observations of Redundancy

1. **Major Duplication**: The publish targets essentially duplicate the Postman upload portion of `postman-instance-build-and-test`, but:
   - They skip the build steps (OpenAPI generation, collection generation)
   - They skip the testing steps (prism, postman-mock)
   - They skip documentation generation

2. **Workflow Differences**:
   - **Rebuild**: Complete pipeline from source → OpenAPI → Postman → Test → Docs
   - **Publish**: Only uploads pre-built artifacts to Postman

3. **Missing in Publish**:
   - No validation that OpenAPI spec is up-to-date
   - No collection generation (assumes already built)
   - No testing before publishing
   - No documentation generation

4. **Redundant Operations**:
   - Both do `postman-cleanup-all`
   - Both upload the same artifacts in the same order
   - The publish targets manually list what `postman-instance-build-and-test` already orchestrates

## 4. Why There's Duplication

The duplication exists because:

1. **Different Use Cases**:
   - Rebuild: Developer workflow (build, test, validate)
   - Publish: Deployment workflow (upload pre-validated artifacts)

2. **Workspace Targeting**:
   - Rebuild uses current workspace settings
   - Publish explicitly targets personal/team workspaces

3. **CI/CD Integration**:
   - Publish targets are designed for GitHub Actions
   - They manage `.postman-target` for workflow persistence

## 5. Recommendation

To reduce redundancy, consider:

1. **Extract Common Sequence**: Create a `postman-upload-sequence` target that both workflows can use
2. **Parameterize Workspace**: Make `postman-instance-build-and-test` accept workspace overrides
3. **Split Concerns**: Separate building from publishing more clearly
4. **Add Publish Mode**: Add a "publish-only" mode to `postman-instance-build-and-test` that skips local testing

Example refactoring:
```makefile
# Common upload sequence
postman-upload-artifacts:
	$(MAKE) postman-import-openapi-as-api
	$(MAKE) postman-spec-create-standalone
	$(MAKE) postman-linked-collection-upload
	$(MAKE) postman-linked-collection-link
	$(MAKE) postman-create-test-collection
	$(MAKE) postman-create-mock-and-env
	$(MAKE) postman-import-openapi-spec

# Simplified publish targets
postman-publish-personal:
	@echo "personal" > .postman-target
	POSTMAN_WORKSPACE_OVERRIDE=$(SERRAO_WS) POSTMAN_API_KEY_OVERRIDE="$${POSTMAN_SERRAO_API_KEY}" \
		$(MAKE) postman-cleanup-all postman-upload-artifacts
```