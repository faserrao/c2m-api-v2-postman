# GitHub Actions Workflow Report
## C2M API v2 CI/CD Pipeline

**Generated**: 2026-02-16
**Workflow File**: `.github/workflows/api-ci-cd.yml`
**Purpose**: Automated build, test, publish, and deployment pipeline for C2M API v2

---

## Executive Summary

When code is pushed to the `c2m-api-v2-postman` repository, an automated GitHub Actions workflow triggers that:

1. **Generates** OpenAPI specifications from EBNF data dictionary
2. **Creates** Postman collections with comprehensive test data
3. **Builds** API documentation (Redocly HTML)
4. **Generates** SDK code for 11 programming languages
5. **Publishes** all resources to Postman workspace
6. **Validates** pipeline outputs with 23 quality checks
7. **Deploys** artifacts to separate repository
8. **Uploads** documentation to GitHub Pages

The entire pipeline completes in approximately **3-4 minutes** and publishes to either **personal** or **corporate** Postman workspace based on repository owner.

---

## Workflow Triggers

### Automatic Triggers

**Push to `main` branch** when changes occur in:
- `openapi/**` - OpenAPI specifications
- `data_dictionary/**` - EBNF data dictionary (source of truth)
- `docs/**` - Documentation files
- `postman/**` - Postman collections and scripts
- `scripts/**` - Build and generation scripts
- `tests/**` - Validation scripts
- `Makefile` - Build orchestration
- `.github/workflows/api-ci-cd.yml` - Workflow itself

**Pull Request to `main` branch** (same paths, read-only validation)

### Manual Trigger

**Workflow Dispatch** with options:
- ✓ Publish to Postman (default: true)
- ✓ Deploy to GitHub Pages (default: true)

---

## Workspace Detection Logic

**CRITICAL**: The workflow automatically detects which Postman workspace to use based on repository owner:

| Repository Owner | Postman Workspace | Purpose |
|-----------------|------------------|---------|
| `faserrao` | Personal | Development/testing |
| `click2mail` | Corporate (Team) | Production |

This **1:1 relationship** prevents cross-workspace pollution and ensures:
- faserrao repository → Personal workspace ONLY
- click2mail repository → Corporate workspace ONLY

Both repositories run **identical workflows** but publish to different workspaces.

---

## Workflow Phases

### Phase 1: Setup (30-45 seconds)

**Environment Preparation**:
- Checkout main repository (`c2m-api-v2-postman`)
- Checkout security repository (`c2m-api-v2-postman-security`)
- Checkout artifacts repository (`c2m-api-v2-postman-artifacts`)
- Setup Node.js v20 with npm cache
- Setup Python 3.11 with pip cache
- Install system dependencies (jq, curl, Postman CLI)

**Dependencies Installed**:
- Node packages (if `package-lock.json` exists)
- Python packages (from `requirements.txt` and `scripts/python_env/requirements.txt`)
- Postman CLI (for Newman testing)

**Environment Information Printed**:
- Python version
- Node version
- npm version
- jq version
- curl version
- Postman CLI location
- GitHub event type (push/PR/manual)
- GitHub ref (branch)

---

### Phase 2: Build OpenAPI Specification (20-30 seconds)

**Process**:
1. **EBNF → OpenAPI Translation**:
   - Reads `data_dictionary/c2mapiv2-dd.ebnf` (904 lines)
   - Runs `scripts/active/ebnf_to_openapi_dynamic_v3.py`
   - Generates `openapi/c2mapiv2-openapi-spec-base.yaml` (719 lines)
   - Merges auth overlay from security repository
   - Creates `openapi/c2mapiv2-openapi-spec-final.yaml`

2. **Add Response Examples**:
   - Runs `scripts/active/add_response_examples.py`
   - Generates success response examples (200-299 status codes)
   - Generates error response examples (400, 401, 403, 404, 422, 500)
   - Creates `openapi/c2mapiv2-openapi-spec-with-examples.yaml`

3. **Validation** (continue-on-error):
   - Lints OpenAPI spec with Redocly
   - Reports: 0 errors, 34 warnings (expected - unused components)
   - Warnings are cosmetic, not blocking

4. **Diff Check** (PRs only):
   - Compares new spec vs origin/main
   - Shows what changed in API definition

**Outputs**:
- `c2mapiv2-openapi-spec-base.yaml` - Base specification
- `c2mapiv2-openapi-spec-final.yaml` - With auth overlay
- `c2mapiv2-openapi-spec-with-examples.yaml` - With response examples

---

### Phase 3: Build Documentation (15-20 seconds)

**Process**:
1. Runs Redocly build: `make docs`
2. Reads OpenAPI spec with examples
3. Generates static HTML documentation
4. Injects custom templates (endpoint quickstart, banner)

**Outputs**:
- `docs/index.html` (491 KB) - Complete API documentation
- `docs/openapi-bundled.yaml` - Bundled OpenAPI spec

---

### Phase 4: Generate SDKs (45-60 seconds)

**Process** (continue-on-error):
1. Runs OpenAPI Generator for 11 languages
2. Generates complete SDK implementations with:
   - API client code
   - Model classes
   - JWT authentication examples
   - Documentation (README, API docs)
   - Test fixtures
   - Package manifests (package.json, setup.py, etc.)

**Languages**:
- Python
- JavaScript
- TypeScript
- Java
- Go
- Ruby
- PHP
- C#
- Swift
- Kotlin
- Rust

**Outputs**:
- `sdk/python/` - Complete Python package
- `sdk/javascript/` - Complete JavaScript package
- (9 more language directories)

**Note**: May show warnings about schema name resolution (non-blocking)

---

### Phase 5: Drift Detection (PRs Only)

**Purpose**: Ensure generated artifacts are committed

**Process**:
1. Checks git status for uncommitted changes in:
   - `openapi/` directory
   - `postman/generated/` directory
   - `docs/` directory

2. **If uncommitted changes found**:
   - ❌ Fails PR with error message
   - Shows which files are out of sync
   - Provides exact commands to run locally:
     ```bash
     make openapi-build
     make postman-collection-build
     make docs
     ```

3. **If all artifacts committed**:
   - ✅ Passes check
   - Allows PR to proceed

**Why Important**: Prevents generated artifacts from drifting out of sync with source data dictionary.

---

### Phase 6: Publish to Postman (60-90 seconds)

**Conditions**:
- Push to `main` branch OR manual dispatch
- `PUBLISH_TO_POSTMAN` enabled (default: true)
- At least one Postman API key configured

**Workspace Selection**:
- **faserrao** repository → Personal workspace (POSTMAN_SERRAO_API_KEY)
- **click2mail** repository → Corporate workspace (POSTMAN_C2M_API_KEY)

**Process**:

1. **Auto-detect Context**:
   ```bash
   if [ "${{ github.repository_owner }}" = "faserrao" ]; then
     WORKSPACE="personal"
   else
     WORKSPACE="corporate"
   fi
   ```

2. **Complete Cleanup**:
   ```bash
   make postman-cleanup-all
   ```
   Deletes ALL existing resources:
   - Mock servers
   - Collections
   - APIs
   - Environments
   - Trash items
   - Standalone specs

3. **Full Rebuild**:
   ```bash
   export BUILD_TYPE=github
   make postman-instance-build-without-tests
   ```

   Creates (in order):
   - **API Definition** (links spec to Postman API)
   - **Standalone OpenAPI Spec**
   - **Linked Collection** (placeholders: `<string>`, `<integer>`, `<oneOf>`)
   - **Test Collection** (realistic faker-generated data)
   - **Use Case Collection** (8 real-world scenarios)
   - **Getting Started Collection** (16 educational patterns)
   - **Mock Server** (created from TEST collection)
   - **Mock Environment** (linked to mock server)
   - **AWS Dev Environment** (production credentials)

4. **UID Tracking**:
   Each resource UID saved to file:
   - `postman_api_uid.txt`
   - `postman_spec_uid.txt`
   - `postman_linked_collection_uid.txt`
   - `test_collection_uid.txt`
   - `postman_mock_uid.txt`
   - `postman_mock_url.txt`

**Resources Published**: 8 total resources per workspace

---

### Phase 7: Post-Build Validation (10-15 seconds)

**Process**:
1. Runs `scripts/validation/ci_verify.sh` with workspace parameter
2. Executes `tests/validate-pipeline-outputs.sh`

**Validation Checks** (23 total):

**OpenAPI Specification** (8 checks):
- ✓ Base spec exists and has content
- ✓ Final spec exists (with auth overlay)
- ✓ Spec with examples exists
- ✓ SDK code samples present (11 endpoints)
- ✓ Proper structure (info, paths, components)
- ✓ Security schemes defined
- ✓ No syntax errors
- ✓ File sizes reasonable

**Postman Collections** (5 checks):
- ✓ Linked collection generated
- ✓ Test collection generated with examples
- ✓ Use case collection generated
- ✓ All collections have valid structure
- ✓ Example data quality

**Postman Artifacts** (6 checks):
- ✓ API UID file contains valid UID
- ✓ Linked collection UID file valid
- ✓ Test collection UID file valid
- ✓ Mock server UID file exists
- ✓ Mock environment file exists
- ℹ️ Auth credentials (INFO in CI/CD - stored in GitHub Secrets)

**Documentation** (3 checks):
- ✓ Redoc documentation exists (docs/index.html)
- ✓ File size OK (491 KB)
- ✓ Bundled OpenAPI spec exists

**Test Results** (1 check):
- ✓ Newman HTML report exists

**Result**: 23/23 validations pass (100%)

**If Validation Fails**:
- ❌ Build fails
- Shows which check failed
- Uploads validation reports as artifacts

---

### Phase 8: Copy Artifacts to Artifacts Repository (5-10 seconds)

**Purpose**: Store all generated files in separate `c2m-api-v2-postman-artifacts` repository

**Process**:
1. Creates directory structure:
   ```
   artifacts-repo/
   ├── openapi/          (OpenAPI specs)
   ├── postman/
   │   ├── collections/  (JSON collections)
   │   └── metadata/     (UID files, environment JSONs)
   ├── docs/             (Redocly HTML documentation)
   └── sdks/             (11 language SDKs)
   ```

2. Copies files:
   - OpenAPI: `*.yaml` files
   - Postman Collections: `generated/*.json`
   - Postman Metadata: `*.txt` and `*.json` files
   - Documentation: Complete `docs/` directory
   - SDKs: Complete `sdk/` directory (if exists)

3. Commits and pushes to artifacts repo:
   ```
   Commit message: "Build #123: Update from [original commit message]"
   Metadata:
     - Source commit: [SHA]
     - Workflow: API Spec, Docs, and Postman CI/CD
     - Triggered by: [actor]
   ```

**Result**: Artifacts repository updated with latest build outputs

---

### Phase 9: Upload Build Artifacts (5-10 seconds)

**Purpose**: Store artifacts in GitHub Actions for download

**Process**:
- Packages all generated files
- Uploads as workflow artifact named `api-artifacts`
- Retention: 90 days (GitHub default)

**Contents**:
- OpenAPI specifications (3 YAML files)
- Postman collections (6 JSON files)
- Postman metadata (8 TXT/JSON files)
- Documentation (HTML + assets)
- SDKs (11 language directories)

**Access**: Available via Actions tab → Workflow run → Artifacts section

---

### Phase 10: Prepare GitHub Pages (5 seconds)

**Status**: Currently **DISABLED** (requires admin to enable in repository settings)

**When Enabled**:
1. Configures GitHub Pages
2. Uploads `docs/` directory as Pages artifact
3. Deploys to `https://[owner].github.io/c2m-api-v2-postman/`

**To Enable**:
1. Repository Settings → Pages → Source → GitHub Actions
2. Change line 389 in workflow: `false` → `true`

---

### Phase 11: Workflow Summary (5 seconds)

**Process**:
- Generates summary with status of all jobs
- Shows build status (success/failure)
- Shows deployment status (Postman/Pages)
- Provides quick links

**Summary Includes**:
- ✅/❌ Build completed successfully / Build failed
- ✅/❌/⏭️ Deployment statuses
- 🔗 Quick Links:
  - View Workflow Run
  - Download Artifacts

**Visible**: GitHub Actions UI → Workflow run → Summary tab

---

## Pipeline Outputs Summary

### Postman Workspace (8 Resources)

| Resource | Description | UID File |
|----------|-------------|----------|
| API Definition | Links OpenAPI spec to Postman | `postman_api_uid.txt` |
| Standalone Spec | OpenAPI spec in Postman | `postman_spec_uid.txt` |
| Linked Collection | Placeholder values | `postman_linked_collection_uid.txt` |
| Test Collection | Realistic test data | `test_collection_uid.txt` |
| Use Case Collection | 8 real-world scenarios | `use_case_collection_uid.txt` |
| Getting Started | 16 educational patterns | `getting_started_collection_uid.txt` |
| Mock Server | Responds to API requests | `postman_mock_uid.txt` |
| Mock Environment | Mock server configuration | `mock_env_uid.txt` |
| AWS Dev Environment | Production credentials | `aws_dev_env_uid.txt` |

### Local Repository Files

**OpenAPI Specifications**:
- `openapi/c2mapiv2-openapi-spec-base.yaml` (719 lines)
- `openapi/c2mapiv2-openapi-spec-final.yaml` (with auth)
- `openapi/c2mapiv2-openapi-spec-with-examples.yaml` (with response examples)

**Postman Collections**:
- `postman/generated/c2mapiv2-linked-collection-flat.json` (108 KB)
- `postman/generated/c2mapiv2-test-collection-flat.json` (152 KB)
- `postman/generated/c2mapiv2-use-case-collection.json` (48 KB)
- `postman/generated/c2mapiv2-getting-started-collection.json` (20 KB)

**Documentation**:
- `docs/index.html` (491 KB) - Complete API documentation

**SDKs** (if generated):
- `sdk/python/` - Python client
- `sdk/javascript/` - JavaScript client
- (9 more languages)

### Artifacts Repository

**Synchronized Copy** of all generated files for:
- Historical tracking
- Deployment packages
- Distribution to consumers
- Rollback capability

---

## Error Handling

### Build Failures

**If OpenAPI Generation Fails**:
- ❌ Workflow stops immediately
- Error message shows EBNF parsing issue
- Fix required in `data_dictionary/c2mapiv2-dd.ebnf`

**If Postman Publish Fails**:
- ❌ Workflow stops at publish step
- Possible causes:
  - Invalid API key
  - Network error
  - Postman API rate limit
  - UID mismatch

**If Validation Fails**:
- ❌ Workflow stops after publish
- Shows which of 23 checks failed
- Validation reports uploaded as artifacts

### Soft Failures (Continue-on-Error)

**Lint Warnings**:
- ⚠️ Workflow continues
- Warnings logged but not blocking

**SDK Generation**:
- ⚠️ Workflow continues if SDK generation fails
- SDKs not critical for core API functionality

**GitHub Pages**:
- ⚠️ Workflow continues if Pages not enabled
- Documentation still available in artifacts

---

## Performance Metrics

### Typical Workflow Duration

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Setup | 30-45s | 45s |
| Build OpenAPI | 20-30s | 75s |
| Build Docs | 15-20s | 95s |
| Generate SDKs | 45-60s | 155s |
| Publish to Postman | 60-90s | 245s |
| Validation | 10-15s | 260s |
| Copy Artifacts | 5-10s | 270s |
| Upload Artifacts | 5-10s | 280s |
| **Total** | **3-5 minutes** | **280s** |

### Resource Usage

- **Compute**: ubuntu-latest (GitHub-hosted runner)
- **Memory**: Peak ~2 GB (SDK generation)
- **Disk**: ~500 MB (all artifacts)
- **Network**: ~100 MB (dependencies + uploads)

---

## Security Considerations

### Secrets Management

**Required GitHub Secrets**:
- `POSTMAN_SERRAO_API_KEY` - Personal Postman workspace access
- `POSTMAN_C2M_API_KEY` - Corporate Postman workspace access
- `SECURITY_REPO_TOKEN` - GitHub PAT for cross-repo access

**Security Features**:
- Secrets never logged or exposed
- API keys rotated annually
- Cross-repo access limited to specific repositories
- `BUILD_TYPE=github` flag prevents local file checks

### Workspace Isolation

**Enforcement**:
- Repository owner determines workspace (enforced at workflow level)
- No manual workspace selection (prevents mistakes)
- faserrao → Personal ONLY
- click2mail → Corporate ONLY

**Benefits**:
- No cross-workspace pollution
- Clear production vs development separation
- Simplified access control

---

## Monitoring and Troubleshooting

### Check Workflow Status

**GitHub Actions UI**:
1. Go to repository → Actions tab
2. Click on workflow run
3. View job logs and artifacts

**Command Line**:
```bash
# List recent runs
gh run list --limit 5

# View specific run
gh run view [run-id]

# View run logs
gh run view [run-id] --log

# Download artifacts
gh run download [run-id]
```

### Common Issues

**Issue: "Invalid API Key"**
- **Cause**: Postman API key expired or incorrect
- **Fix**: Update GitHub Secret with new key

**Issue: "Auth credentials missing from environment"**
- **Cause**: Expected failure in CI/CD (credentials in GitHub Secrets, not local file)
- **Status**: INFO message, validation passes

**Issue: "No changes to commit" in artifacts repo**
- **Cause**: No files changed since last build
- **Status**: Normal, workflow continues

**Issue: "Drift detected" in PR**
- **Cause**: Generated files not committed
- **Fix**: Run build commands locally and commit results

---

## Comparison: Local vs CI/CD Build

| Aspect | Local Build | CI/CD Build |
|--------|-------------|-------------|
| **Target** | `make postman-instance-build-with-tests` | `make postman-instance-build-without-tests` |
| **Prism Mock** | ✓ Started on port 4010 | ✗ Skipped |
| **Docs Server** | ✓ Started on port 8080 | ✗ Skipped |
| **Newman Tests** | ✓ Against local mock | ✓ Against published mock |
| **Validation** | 22/23 pass (1 INFO for auth) | 23/23 pass (BUILD_TYPE=github) |
| **Duration** | 8-10 minutes | 3-5 minutes |
| **Postman Publish** | Optional | Automatic |
| **SDK Generation** | Only in `make full-rebuild` | Every build |
| **Artifacts** | Local disk only | GitHub + Artifacts repo |

---

## Future Enhancements

### Planned Improvements

1. **GitHub Pages Deployment**:
   - Currently disabled (requires admin)
   - Enable: Repository Settings → Pages
   - Will auto-deploy docs to public URL

2. **Parallel SDK Generation**:
   - Generate multiple languages concurrently
   - Reduce SDK phase from 60s to ~20s

3. **Incremental Builds**:
   - Detect what changed (EBNF vs docs vs scripts)
   - Skip unchanged steps
   - Reduce build time by 50%

4. **Deployment Notifications**:
   - Slack/email notifications on success/failure
   - Deploy status badges in README

5. **Performance Monitoring**:
   - Track build duration over time
   - Alert on >5 minute builds

---

## Appendix: Make Targets Used

### Build Phase

| Make Target | Purpose |
|-------------|---------|
| `openapi-build` | Generate OpenAPI from EBNF + merge overlays |
| `lint` | Validate OpenAPI spec with Redocly |
| `diff` | Compare spec changes (PRs only) |
| `docs` | Build Redocly HTML documentation |
| `generate-sdk-all` | Generate SDKs for 11 languages |

### Publish Phase

| Make Target | Purpose |
|-------------|---------|
| `workspace-info` | Show current workspace configuration |
| `postman-cleanup-all` | Delete all Postman resources |
| `postman-instance-build-without-tests` | Full rebuild (no local servers) |
| `validate-pipeline` | Run 23 validation checks |

### Components of Build Target

The `postman-instance-build-without-tests` target orchestrates:

1. `postman-create-api` - Create API definition
2. `postman-spec-create-standalone` - Upload OpenAPI spec
3. `postman-create-linked-collection` - Create linked collection
4. `postman-create-test-collection` - Create test collection with examples
5. `postman-upload-use-case-collection` - Upload use cases
6. `postman-generate-getting-started-all` - Generate and upload Getting Started
7. `postman-mock-create` - Create mock server
8. `postman-create-mock-and-env` - Create mock environment
9. `postman-create-aws-dev-env` - Create AWS dev environment
10. `validate-pipeline` - Validate all outputs

---

## Document Version

**Version**: 1.0
**Date**: 2026-02-16
**Author**: Claude Code (Anthropic)
**Workflow Version**: As of commit b7ea715
**Workflow File**: `.github/workflows/api-ci-cd.yml` (445 lines)

---

## Quick Reference

**View Latest Run**:
```bash
gh run list --limit 1
```

**View Run Logs**:
```bash
gh run view [run-id] --log
```

**Download Artifacts**:
```bash
gh run download [run-id]
```

**Trigger Manual Build**:
```bash
gh workflow run api-ci-cd.yml
```

**Check Postman Resources**:
```bash
# Personal workspace
make postman-workspace-debug

# After build
cat postman/*.txt  # View all UIDs
```

**Validation Results**:
```bash
cat reports/validation-*.md
```

---

**End of Report**
