# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the C2M API V2 project that implements a unique pipeline: EBNF Data Dictionary → OpenAPI Specification → Postman Collection → Mock Server → API Documentation.

## Restoration Status (2025-09-08)

✅ **RESTORATION COMPLETE** - The c2m-api-v2-postman repository (formerly c2m-api-v2-postman) has been successfully restored to its pre-auth state:
- JWT authentication code moved to separate security repository
- Makefile cleaned up (removed redundant targets, simplified publish workflow)
- Documentation reorganized into user-guides directory with symlinks
- OpenAPI spec creation in Postman fixed (was double-encoding issue)
- All 24 tests passing (including auth endpoint with 403 status allowed)
- Successfully merged to main branch

## Key Commands

### Initial Setup
```bash
make install                    # Install all dependencies (npm, Python)
python3 -m venv scripts/python_env/e2o.venv  # Create Python venv if needed
```

### Primary Development Workflow
```bash
make postman-collection-build-and-test  # Run complete pipeline (most common command)
```

### Individual Pipeline Steps
```bash
make generate-openapi-spec-from-dd      # Convert EBNF to OpenAPI
make lint                               # Validate OpenAPI spec
make prism-start                        # Start local mock server (port 4010)
make postman-mock                       # Run tests against mock
make docs-serve                         # Serve docs locally (port 8080)
```

### Cleanup
```bash
make postman-cleanup-all                # Delete all Postman resources
make prism-stop                         # Stop local mock server
```

### CI/CD Commands (GitHub Actions)
```bash
# These aliases are used by GitHub Actions workflow
make openapi-build                      # Build OpenAPI from EBNF + lint
make postman-collection-build           # Generate and flatten collection
make docs                               # Build API documentation
make lint                               # Lint OpenAPI spec
make diff                               # Diff spec vs origin/main
make postman-publish                    # Push to Postman (reads .postman-target)
make postman-publish-personal           # Explicitly publish to personal workspace
make postman-publish-corporate          # Explicitly publish to corporate workspace

# GitHub Actions specific behavior
# The workflow reads .postman-target file to determine which workspace to use
# Creates this file with: echo "personal" > .postman-target
```

### Smart Rebuild System (NEW!)
```bash
# Intelligent rebuild that only regenerates what has changed
make smart-rebuild                      # Check for changes and rebuild only what's needed
make smart-rebuild-dry-run             # Show what would be rebuilt without doing it
make smart-rebuild-status              # Show current build state and hashes
make smart-rebuild-clean               # Clear hash cache (forces full rebuild)
```

The smart rebuild system cascades through the pipeline:
1. Checks if data dictionary (EBNF) changed → regenerates OpenAPI if needed
2. Checks if OpenAPI spec changed → rebuilds Postman collections if needed
3. Checks if collections changed → regenerates SDK if needed
4. All changes trigger documentation rebuild
5. Shows diffs of what changed at each step

### Advanced Testing
```bash
# Test specific endpoints with Prism mock server
make prism-test-endpoint PRISM_TEST_ENDPOINT=/jobs/single-doc
make prism-test-list PRISM_TEST_ENDPOINT=/jobs/single-doc
make prism-test-select PRISM_TEST_ENDPOINT=/jobs/single-doc PRISM_TEST_INDEX=2
```

### Utility Commands
```bash
# SDK Generation
make generate-sdk                       # Generate SDK from OpenAPI spec

# Documentation Deployment
make deploy-docs                        # Deploy docs to hosting service

# Maintenance
make cleanup-scripts                    # Clean obsolete scripts
make cleanup-openapi                    # Clean old OpenAPI files
make cleanup-docs                       # Clean temp documentation files
make cleanup-all                        # Clean all directories

# Git Workflow
make git-pull-rebase                    # Pull with rebase
make git-save MSG="your commit message" # Quick add, commit, push
```

## Architecture

The project follows a data-driven approach where the EBNF data dictionary is the single source of truth:

1. **Data Dictionary** (`data_dictionary/`) - EBNF definitions converted to OpenAPI
2. **OpenAPI Spec** (`openapi/`) - Generated YAML specifications
3. **Postman Collections** (`postman/generated/`) - Test collections with examples
4. **Mock Servers** - Both local (Prism) and cloud (Postman) mocks
5. **Documentation** (`docs/`) - Auto-generated API documentation

## Key Directories

- **`scripts/`**: Conversion and utility scripts (Python, Node.js, Shell)
  - `active/` - Primary pipeline scripts
    - `ebnf_to_openapi_class_based.py` - Core EBNF to OpenAPI converter
    - `add_tests.js` - Adds automated tests to collections
    - `fix_collection_urls_v2.py` - Fixes URLs in collections
  - `utilities/` - Support and maintenance scripts
  - `archived/` - Legacy and deprecated scripts

- **`postman/`**: Postman-related files
  - `custom/` - User customizations and overrides
  - `generated/` - Auto-generated collections
  - Various UID/URL tracking files

- **`openapi/`**: OpenAPI specifications
  - Final spec: `c2mapiv2-openapi-spec-final.yaml`

## Environment Configuration

Create a `.env` file with:
```
POSTMAN_SERRAO_API_KEY=your-api-key
POSTMAN_C2M_API_KEY=alternate-api-key
```

## Common Development Tasks

### Running Tests
```bash
# Test against local mock
make prism-mock-test

# Test against Postman cloud mock  
make postman-mock

# Run specific endpoint test
PRISM_TEST_ENDPOINT=/your/endpoint make prism-test-select
```

### Debugging
```bash
make print-openapi-vars         # Debug OpenAPI variables
make verify-urls               # Check collection URLs
make postman-workspace-debug   # Debug Postman workspace
```

### Working with Mock Servers
```bash
# Local development (Prism)
make prism-start              # Start on port 4010
make prism-status            # Check if running
make prism-stop              # Stop server

# Postman cloud mock
make postman-mock-create     # Create new mock
make update-mock-env         # Update mock environment
```

## Important Notes

1. **Makefile $$ Escaping**: Shell variables in Makefile require `$$` not `$`
2. **Python Environment**: Uses venv at `scripts/python_env/e2o.venv`
3. **Workspace ID**: Default is Serrao workspace (`d8a1f479-a2aa-4471-869e-b12feea0a98c`)
4. **Mock URLs**: Automatically saved to tracking files in `postman/`
5. **Collection Fixes**: URLs are automatically fixed to use `{{baseUrl}}` placeholder
6. **GitHub Actions**: Uses portable jq syntax (no line continuations) for compatibility
7. **API Deletion**: Fixed to properly delete all APIs in workspace during cleanup

## Troubleshooting

- **PyYAML Issues**: Run `make fix-yaml`
- **Port Conflicts**: Prism uses 4010, docs use 8080
- **API Key Issues**: Check `.env` file and `POSTMAN_API_KEY` selection in Makefile
- **Collection Validation**: Run `make postman-test-collection-validate`
- **GitHub Actions jq errors**: Fixed - uses portable syntax without line continuations
- **Wrong workspace published**: Check `.postman-target` file content
- **Only 1 API deleted**: Fixed - now properly deletes all APIs during cleanup

## Pipeline Flow

1. Edit EBNF data dictionary
2. Run `make postman-collection-build-and-test`
3. System automatically:
   - Converts EBNF to OpenAPI
   - Generates Postman collection
   - Adds test data and tests
   - Creates mock server
   - Runs tests
   - Generates documentation

## GitHub Actions CI/CD

The project includes automated CI/CD pipelines:

### Main Workflow (`api-ci-cd.yml`)
- **Triggers**: Push to main, PRs, manual dispatch
- **Actions**: 
  - Builds OpenAPI spec from EBNF
  - Generates Postman collections
  - Builds documentation
  - Auto-commits generated files (main branch only)
  - Cleans up existing Postman resources before publishing
  - Publishes to Postman workspace based on `.postman-target` file
  - Deploys docs to GitHub Pages

### PR Drift Check (`pr-drift-check.yml`)
- **Purpose**: Ensures generated files are committed
- **Fails PR if**: Generated artifacts differ from committed versions
- **Auto-comments**: Instructions to regenerate files

### Required Secrets
Configure in GitHub Settings → Secrets:
- `POSTMAN_API_KEY`: Your Postman API key
- `POSTMAN_WORKSPACE_ID`: Target workspace UUID

### Workspace Publishing
The workflow determines which workspace to publish to:
1. Reads `.postman-target` file (contains "personal" or "corporate")
2. Runs corresponding make target: `make postman-publish-{target}`
3. Default is "personal" if file doesn't exist

To set target: `echo "personal" > .postman-target`

## Script Integration Status

### Recently Integrated Scripts
✅ `prism_test.sh` - Advanced endpoint testing with Prism (targets: prism-test-*)
✅ `generate-sdk.sh` - SDK generation placeholder (target: generate-sdk)
✅ `deploy-docs.sh` - Documentation deployment placeholder (target: deploy-docs)
✅ `cleanup-*.sh` - Directory cleanup utilities (targets: cleanup-*)
✅ `git-pull-rebase.sh` - Git workflow helper (target: git-pull-rebase)
✅ `git-push.sh` - Quick commit helper (target: git-save)

### Remaining Integration Opportunities
- `generate_openapi_from_swagger.py` - Swagger to OpenAPI conversion
- `merge_yaml_files.py` - Merge multiple YAML specs
- `api_client_generator.py` - Generate Python client from OpenAPI

## Logging Protocol
**Update logs after each major feature completion OR every 30 minutes, whichever comes first**

## Session History - 2025-11-04

### Makefile Target Renaming for Clarity

**Summary**: Renamed Makefile targets to eliminate confusion about build behavior (with/without tests).

#### Background
- Original naming caused confusion:
  - `postman-instance-build-and-test` (local development with tests)
  - `postman-instance-build-only` (CI/CD without tests)
- The word "only" was ambiguous - unclear what was being excluded
- Need for symmetric, parallel naming convention

#### Changes Made
**Old Names → New Names:**
- `postman-instance-build-and-test` → `postman-instance-build-with-tests`
- `postman-instance-build-only` → `postman-instance-build-without-tests`

**Files Updated:**
1. **Makefile** - Target definitions and all references (6 changes)
2. **.github/workflows/api-ci-cd.yml** - CI/CD pipeline (1 change)
3. **CLAUDE.md** - Session history and key commands (2 changes)
4. **CI_CD_OPERATIONS_GUIDE.md** - All workflow examples (9 changes)
5. **VALIDATION_CI_CD_INTEGRATION.md** - Troubleshooting section (1 change)

#### Benefits
- ✅ **Crystal clear intent**: Both names explicitly state test inclusion/exclusion
- ✅ **Symmetric naming**: Both follow pattern `postman-instance-build-<modifier>`
- ✅ **No ambiguity**: "with-tests" vs "without-tests" is unambiguous
- ✅ **Better developer experience**: Immediately obvious which target to use

#### Usage Clarification
**Local Development:**
```bash
make postman-instance-build-with-tests
# Includes: Prism mock server, local testing, documentation serving
```

**CI/CD Pipeline:**
```bash
make postman-instance-build-without-tests
# Skips: Local testing, prism-start, docs-serve
# Includes: All Postman publishing, collections, mock servers, environments
```

#### Rationale
- Tests require local infrastructure (Prism server, docs server)
- CI/CD publishes to Postman cloud (doesn't need local testing)
- CI/CD uses separate validation step after publish
- Local developers want immediate test feedback
- Both targets generate same Postman artifacts

#### Key Learning
- Target names should be self-documenting
- Parallel structures reduce cognitive load
- "with/without" pattern clearer than "only" suffix

---

## Session History - 2025-10-12

### Authentication Consolidation - Comparative Analysis of Two Approaches

**Summary**: Created comprehensive comparison of two different authentication consolidation strategies discovered across separate planning sessions.

#### Background
- Two separate sessions proposed different solutions to same problem (dual auth systems)
- Session 1 (Oct 11): AUTHENTICATION_CONSOLIDATION_PLAN.md - Dual-mechanism approach
- Session 2 (Oct 10-11): SINGLE_USER_POOL_MIGRATION_PLAN.md - Single User Pool approach
- This session reconciles both approaches with side-by-side comparison

#### Document Created
- **AUTHENTICATION_CONSOLIDATION_PLAN_V2.md** (Parent directory: C2M_API_v2/)
  - ~700 lines comprehensive comparison
  - Architecture diagrams for both approaches
  - Implementation complexity analysis
  - Security analysis
  - Cost comparison (+40% vs -40%)
  - User experience comparison
  - Decision framework with decision tree

#### Approach A: Dual-Mechanism Unified Service (Recommended)
**Architecture**:
- Extend c2m-api-v2-postman-security with NEW Cognito User Pool for human users
- KEEP existing M2M Lambda authorizer unchanged (backwards compatible)
- Add UserCredentials DynamoDB table (maps userId → unique clientId/secret)
- Add endpoints: POST /auth/user/login, GET /auth/user/credentials
- Users login → auto-fetch their unique credentials → use in generated code

**Key Metrics**:
- Timeline: 5 weeks
- Effort: 80-100 hours
- Cost: +$2/month (+40% increase)
- Risk: Low (no breaking changes)
- Backwards Compatibility: 100%

**Benefits**:
- ✅ Fast implementation (5 weeks vs 6-8 weeks)
- ✅ No breaking changes for Postman collections or existing M2M
- ✅ Per-user credential isolation (unique clientId per user)
- ✅ Auto-fetch credentials (no manual entry)
- ✅ Easy rollback if issues arise

**Trade-offs**:
- ⚠️ Two auth mechanisms to maintain (Lambda + Cognito)
- ⚠️ Higher operational cost (+$2/month)
- ⚠️ API logs show clientId not username
- ⚠️ More complex architecture long-term

#### Approach B: Single User Pool (Alternative)
**Architecture**:
- Replace EVERYTHING with ONE Cognito User Pool
- M2M becomes service accounts in User Pool (e.g., postman-ci user)
- OAuth2 scopes for authorization (api:read, api:write, api:execute, api:admin)
- API Gateway Cognito Authorizer (replace custom Lambda authorizer)
- Users login → use their JWT directly (no clientId/secret)

**Key Metrics**:
- Timeline: 6-8 weeks
- Effort: 150-200 hours
- Cost: -$3/month (40% reduction)
- Risk: High (breaking changes for Postman)
- Backwards Compatibility: 0% (breaking change)

**Benefits**:
- ✅ Simpler long-term architecture (one auth system)
- ✅ Cost savings (-$3/month)
- ✅ User-level tracking in ALL API logs
- ✅ Native Cognito features (MFA, password policy, etc.)
- ✅ OAuth2 scopes for fine-grained authorization

**Trade-offs**:
- ⚠️ Slower implementation (6-8 weeks)
- ⚠️ Breaking change for all Postman collections
- ⚠️ Higher migration risk (production impact)
- ⚠️ Extensive testing required (all auth flows change)
- ⚠️ Service accounts in User Pool (unconventional)

#### Recommendation: Approach A with Future Migration Path

**Rationale**:
1. **Lower Risk**: No breaking changes, easy rollback, incremental deployment
2. **Faster Delivery**: 5 weeks vs 6-8 weeks to production
3. **Immediate Value**: Solves main problem (per-user credentials, auto-fetch)
4. **Future Option**: Can migrate to Approach B later if needed (after 3-6 months)
5. **Proven Pattern**: Similar to industry-standard "API key per user" model

**Migration Path A → B**:
- Approach A provides stable foundation
- Users already have unique credentials (easier migration)
- Can evaluate OAuth2 model after Approach A is proven
- Migration from A to B estimated at 2-3 weeks (vs 6-8 weeks fresh)

#### Impact on c2m-api-v2-postman
- **No changes to existing functionality** (either approach)
- Postman collections:
  - Approach A: No changes required (JWT pre-request script unchanged)
  - Approach B: Breaking changes (all collections must update pre-request scripts)
- Mock server detection: Unchanged
- Real World Use Cases collection: Unchanged

#### Decision Framework

**Choose Approach A if**:
- ✅ Need deployment within 5-6 weeks
- ✅ Breaking changes not acceptable
- ✅ Lower risk is priority
- ✅ Want to validate model before full commitment

**Choose Approach B if**:
- ✅ Have 6-8 weeks for implementation
- ✅ Can coordinate breaking changes with all stakeholders
- ✅ Long-term cost reduction critical
- ✅ User-level tracking in ALL logs required immediately
- ✅ Want to avoid technical debt (two auth systems)

#### Next Steps
1. ✅ Review AUTHENTICATION_CONSOLIDATION_PLAN_V2.md
2. ⏳ Stakeholder decision (Approach A vs B) within 1 week
3. ⏳ If Approach A: Start Phase 1 (Infrastructure setup in c2m-api-v2-postman-security)
4. ⏳ If Approach B: Review SINGLE_USER_POOL_MIGRATION_PLAN.md, create Postman migration plan

#### Key Learning
- Authentication consolidation has multiple valid approaches
- Dual-mechanism (Approach A) respects different use cases (M2M vs User)
- Single pool (Approach B) provides architectural simplicity
- Incremental approach (A first, then optionally B) reduces risk while preserving options

## Session History - 2025-10-11

### Authentication Consolidation Decision & Planning

**Summary**: Decided to consolidate all authentication (M2M + User) into c2m-api-v2-postman-security as THE unified authentication service for the entire C2M API V2 ecosystem.

#### Background
- Analyzed current authentication infrastructure across the project
- Discovered two completely independent systems with no integration:
  1. **c2m-api-v2-postman-security**: M2M client credentials (used by Postman collections)
  2. **c2m-api-v2-click2endpoint-developers**: User username/password (used by wizard app)
- Identified problems: Duplicate infrastructure, hardcoded credentials, no per-user isolation, manual credential entry

#### Decision
- **Make c2m-api-v2-postman-security the single authentication service** for everything
- Extend it to support both M2M (existing) and User authentication (new)
- Remove duplicate Cognito infrastructure from c2m-api-v2-click2endpoint-developers
- Auto-fetch user credentials after login (no more hardcoded test-client-123)

#### Key Changes Planned
1. **Extend c2m-api-v2-postman-security** (Phase 1-2):
   - Add Cognito User Pool for human users (username/password)
   - Create UserCredentials DynamoDB table (maps users to their clientId/clientSecret)
   - Add Lambda functions: user-login, get-credentials, rotate-credentials
   - Add API endpoints: POST /auth/user/login, GET /auth/user/credentials, GET /auth/user/me
   - Keep existing M2M endpoints unchanged

2. **Update c2m-api-v2-click2endpoint-developers** (Phase 3):
   - Remove local Cognito User Pool
   - Replace AWS Amplify with fetch() calls to security repo API
   - Auto-fetch credentials after user login
   - Display credentials in Settings (read-only, with rotation button)
   - Remove hardcoded DEFAULT_CLIENT_ID/SECRET from codeGenerators.ts

3. **Migrate Users** (Phase 2):
   - Export users from click2endpoint Cognito
   - Create in security repo Cognito
   - Generate unique clientId/clientSecret for each user
   - Store mapping in UserCredentials table

#### Documents Created
- **AUTHENTICATION_CONSOLIDATION_PLAN.md**: Complete 5-week implementation plan
- **CURRENT_AUTHENTICATION_FLOW_DIAGRAM.md**: AS-IS flow with detailed ASCII diagrams
- **AUTHENTICATION_INFRASTRUCTURE_COMPARISON.md**: Side-by-side comparison of both systems

#### Benefits
- ✅ Single source of truth for all authentication
- ✅ Per-user credential isolation (each user gets unique clientId/secret)
- ✅ Better UX (auto-fetch credentials, no manual entry)
- ✅ Production-ready (same system for dev and prod)
- ✅ Scalable (easy to add click2endpoint-nlp, future apps)
- ✅ Maintainable (one codebase to secure and update)
- ✅ Cost-effective (+$2/month = $7-12/month total)

#### Impact on c2m-api-v2-postman
- **No changes to existing functionality**: Postman collections continue to work as-is
- JWT pre-request script unchanged (still calls /auth/tokens/long and /auth/tokens/short)
- Mock server detection logic unchanged
- All existing M2M endpoints preserved

#### Timeline
- Phase 1: Infrastructure Setup (Week 1)
- Phase 2: User Migration (Week 2)
- Phase 3: click2endpoint Integration (Week 3)
- Phase 4: Testing & Documentation (Week 4)
- Phase 5: Production Deployment (Week 5)
- **Total**: 5 weeks from implementation start

#### Next Steps
1. Get approval from stakeholders
2. Start Phase 1: Add Cognito User Pool to security repo
3. Implement user login Lambda function
4. Test new endpoints with Postman

#### Key Learning
- Consolidating authentication early prevents technical debt
- Provider-agnostic design (already in security repo) makes this easier
- Single authentication service simplifies the entire ecosystem

## Session History - 2025-10-09

### Complete Session: JWT Mock Detection, CI/CD Environment Creation Fix

**Summary**: Fixed JWT mock detection, resolved mock server collection bug, fixed GitHub Actions environment creation, updated Click2Endpoint URLs, and documented credentials.

#### Part 1: JWT Mock Detection Fix & Mock Server Collection Bug
1. **JWT Pre-request Script - URL Resolution Fix**
   - **Problem**: Authorization headers were being added to mock server requests despite console showing "Mock server detected - skipping"
   - **Root Cause**: `pm.request.url.toString()` returns unresolved template `{{baseUrl}}/path` not the actual URL
   - **Solution**: Check both `pm.request.url.host` (resolved by Postman) AND `baseUrl` variable
   - **Files Modified**:
     - `postman/scripts/jwt-pre-request.js` (Test Collection - two-token flow)
     - `postman/scripts/simple-jwt-pre-request.js` (Real World Collection - single token)
     - `scripts/active/generate_use_case_collection.py` (hardcoded JavaScript in Python)
   - **Enhanced Logging**: Added debug output showing URL resolution, host detection, baseUrl variable, and mock detection result

2. **Mock Server Creation Collection Bug**
   - **Problem**: `/jobs/single-doc` and `/jobs/multi-doc-merge` returned mockRequestNotFoundError
   - **Root Cause**: Mock server created from Real World Use Cases collection (only 3 endpoints) instead of Test Collection (all 9 endpoints)
   - **Solution**: Updated Makefile to create mock from Test Collection UID file
   - **Key Insight**: Test Collection defines all endpoints (blueprint), Real World Collection sends example requests

3. **Click2Endpoint URL Updates**
   - Updated 3 files with new mock server URL after rebuild:
     - `c2m-api-v2-click2endpoint-developers/frontend/.env.local`
     - `c2m-api-v2-click2endpoint-developers/frontend/src/utils/codeGenerators.ts`
     - `c2m-api-v2-click2endpoint-developers/frontend/.env.example`
   - New mock URL: `https://46116679-9a50-434a-a26a-49781942a926.mock.pstmn.io`

4. **Credentials Documentation**
   - Added comprehensive Click2Endpoint section (~110 lines) to both:
     - `~/.c2msecure/C2M_API_V2_CREDENTIALS_REFERENCE.md` (with actual credentials)
     - `SystemWideDocuments/C2M_API_V2_CREDENTIALS_REFERENCE.md` (sanitized)
   - Documented storage locations, credential types, settings flow, auth flow, and security notes

5. **Branch Merged to Main**
   - Branch: `experiment/fix-jwt-mock-detection`
   - Commits: 8 files modified, +153/-43 lines
   - Merged successfully and pushed to GitHub

#### Part 2: GitHub Actions CI/CD Environment Creation Fix

6. **Environment Creation Bug in CI/CD**
   - **Problem**: GitHub Actions workflow not creating environments in Postman
   - **Root Cause**: UID file mismatch (same issue as local build)
     - `postman-test-collection-upload` saves UID to `postman/test_collection_uid.txt`
     - `postman-mock-create` was reading from `postman/native-flat-collection-uid.txt` (different file!)
   - **Solution**: Updated 3 Makefile targets to use `$(POSTMAN_TEST_COLLECTION_UID_FILE)`:
     - `postman-mock-create` (line 1520)
     - `postman-link-env-to-mock-server` (lines 1688, 1691)
     - `update-mock-env` (line 1554)
   - **Testing**:
     - ✅ Local test: Deleted stale file, ran `make postman-instance-build-without-tests` successfully
     - ✅ CI/CD test: Triggered workflow #18389887601, completed successfully in 2m 43s

7. **CI/CD Test Results** (Workflow #18389887601)
   - ✅ **2 Environments Created**:
     - C2M API - Mock Server (`46321051-83ef2298-0979-4696-8215-268903ae188c`)
     - C2M API - AWS Dev (`46321051-73ed8284-064d-488b-9973-37dcc0488d8e`)
   - ✅ **3 Collections Created**:
     - C2M API v2 – Real World Use Cases
     - C2mApiCollectionLinked
     - C2mApiV2TestCollection
   - ✅ **Mock Server Created and Linked**:
     - URL: `https://908705d8-5891-4b43-88f3-ab4633156419.mock.pstmn.io`
     - Collection: Test Collection (all 12 endpoints)
     - Environment: Linked to C2M API - Mock Server environment
   - ✅ **Mock Server Tested**: POST request returned valid response (status: processing, jobId: CSlkTg1owN)

8. **End-to-End Verification**
   - User tested Real World Use Cases collection in Postman
   - JWT auth flow working: Token obtained, mock detected, auth header skipped
   - Mock server responded: 200 OK, 338ms, jobId saved
   - **All components working perfectly**: CI/CD → Environments → Mock Server → Collections → JWT Auth

#### Technical Details
- **Postman URL Resolution**:
  - `pm.request.url.toString()` → `{{baseUrl}}/path` (template)
  - `pm.request.url.host` → `['908705d8-5891-4b43-88f3-ab4633156419', 'mock', 'pstmn', 'io']` (resolved)
  - Fallback: Check `baseUrl` variable when host is unresolved
- **Mock Detection Logic**: Dual check (host + baseUrl variable)
- **Collection Structure**: Test Collection (9 endpoints), Real World (3 template endpoints)
- **UID File Consolidation**: Single source of truth (`test_collection_uid.txt`)

#### Key Learnings
- Postman URL resolution varies by context - always check both resolved host AND variables
- Mock server creation requires collection with endpoint definitions (Test), not just examples (Use Cases)
- UID file synchronization critical for CI/CD - one target writes, all targets must read same file
- Hardcoded JavaScript in Python strings is pragmatic but should be refactored to template files
- Dual verification (local + CI/CD) catches environment-specific issues

#### Commits
- `f8abfc9` - Merge branch 'experiment/fix-jwt-mock-detection'
- `9de9aaf` - fix: update Test Collection UID after rebuild
- `070d280` - fix: use correct UID file for mock server creation

## Session History - 2025-09-29

### Critical Fixes Applied Today
1. **JWT Pre-request Script - Mock Server Detection**
   - Fixed issue where Authorization header was being sent to mock servers causing HTML errors
   - Solution: Detect mock server URLs and skip Authorization header
   - Files modified:
     - `postman/scripts/jwt-pre-request.js`
     - `scripts/active/generate_use_case_collection.py`
   - Both Real World and Test collections share the same mock server

2. **OpenAPI Validation Errors**
   - Fixed "application~1json" errors by removing duplicate 'example' fields
   - Modified `scripts/active/add_response_examples.py` to only use 'examples' not 'example'
   - Added descriptions and tags to all job endpoints

3. **GitHub Actions Workflow**
   - Fixed dependency order - docs build must come after Postman collection build
   - Added use case collection generation to CI flow (required for mock server)
   - Fixed shell syntax error in artifacts commit step
   - Added rule to generate `with-examples.yaml` file as dependency

4. **Real World Use Cases Collection Overhaul**
   - **Fixed Template Endpoints**: Removed `jobOptions` from Legal Firm, Real Estate Agent, and Monthly Newsletters
     - Replaced with appropriate `jobTemplate` references (e.g., "legal_certified_mail")
   - **Removed GET Requests**: Each use case now only contains Submit Job request
   - **Updated Collection Description**:
     - Removed authentication setup section
     - Added detailed step-by-step navigation instructions (8 steps)
     - Fixed missing navigation level (POST request expansion)
     - Added full use case descriptions exactly as provided (not summarized)
     - Removed reference to 'C2M Production' environment
   - **Eliminated Duplicates**: Complete cleanup/rebuild to ensure only one collection
   - **Fixed Mock Server**: Recreated using test collection instead of use case collection
   - **File Consolidation**: Only generate `c2mapiv2-use-case-collection.json` via Makefile

5. **Critical Mock Server Architecture Discovery**
   - **Root Cause of Failures**: Mock server was being created with wrong collection
     - Makefile bug: Lines 1521-1523 use `USE_CASE_COLLECTION_UID` for mock creation
     - Real World Use Cases collection only has example requests, not endpoint definitions
     - This caused 404 errors and generic "example" responses
   - **Correct Architecture**:
     - Mock server MUST be built from TEST collection (contains all endpoint definitions)
     - Real World Use Cases collection sends requests TO the mock server
     - TEST collection = blueprint/instruction manual for mock server
     - Real World Use Cases = pre-filled example requests
   - **Flow**: TEST Collection → Defines Mock Server → Accepts requests from ANY collection
   - **Fix**: Complete rebuild properly created mock with test collection

6. **Use Case Collection Permutation System** (2025-09-30)
   - **Problem**: Original script generated similar examples (consecutive permutations too alike)
   - **Solution**: Created `generate_use_case_collection_v2.py` that reads from existing permutation files
   - **Architecture**:
     - Reads from `data_dictionary/generate-endpoint-permutations/permutations/`
     - Each file contains all permutations for an endpoint (270-810 permutations each)
     - Script randomly selects 5 diverse examples per use case
   - **Selection Strategy**:
     - Divides permutation list into 5 sections
     - Randomly picks one from each section
     - Ensures variety across document sources, payment types, and address types
   - **Integration**:
     - Updated Makefile to use new script
     - Original script preserved as fallback (`generate_use_case_collection.py`)
     - Easy revert: just change script name in Makefile
   - **Benefits**:
     - More diverse examples (not consecutive similar ones)
     - Leverages existing permutation generation infrastructure
     - Repeatable in pipeline - different examples each run

## Known Issues to Fix Later

1. **Postman Response Examples Show Request Bodies**
   - Issue: Response examples in Postman collections show request body format instead of actual response format
   - Expected: `{status, message, jobId}`
   - Actual: Shows request body with `{jobTemplate, documentSourceIdentifier, etc.}`
   - Likely cause: openapi-to-postmanv2 converter issue
   - Priority: Low - not blocking functionality

## Learning Memories

- `learn`: Placeholder for learning memories related to the project
- Added a placeholder for `memorize`
- First memory added: Learning how to effectively manage and update project documentation
- Discovered the importance of dynamic pipeline generation based on source document changes
- Fixed API deletion issue where only 1 of N APIs was being deleted
- Implemented workspace-based publishing system using `.postman-target` file
- Created comprehensive build guide for non-technical users
- Fixed OpenAPI spec double-encoding bug (was using `jq -Rs .` instead of `cat`)
- Simplified publish targets to use orchestrator pattern (eliminated ~1000 lines)
- Restored repo from broken state with auth integration mixed in
- **2025-09-08**: Fixed CI/CD workflow issues:
  - Postman CLI needs explicit installation in GitHub Actions
  - Added CI-specific targets that skip local testing (prism-start, docs-serve)
  - npm version of openapi-diff behaves differently than brew version
- **2025-09-08**: Consolidated documentation from security repo:
  - Created POSTMAN_COMPLETE_GUIDE.md merging all Postman docs
  - Created AUTHENTICATION_GUIDE.md consolidating auth documentation
  - Created CUSTOMER_ONBOARDING_GUIDE.md for new customers
  - Established migration plan for remaining docs
- **2025-09-27**: Fixed oneOf handling in the entire pipeline:
  - openapi-to-postmanv2 simplifies anonymous oneOf schemas to just the first type
  - Created fix_openapi_oneOf_schemas.py to convert anonymous to named schemas
- **2025-10-09**: JWT mock detection and mock server collection bug:
  - `pm.request.url.toString()` returns unresolved template `{{baseUrl}}/path` during pre-request
  - `pm.request.url.host` is resolved by Postman (array format) - use this for mock detection
  - Must check BOTH resolved host AND baseUrl variable for complete coverage
  - Mock server MUST be created from Test Collection (9 endpoints) not Real World Use Cases (3 endpoints)
  - Test Collection = blueprint for mock server, Real World = example requests
  - Both collections can use same mock once created from correct collection
  - Enhanced logging crucial for debugging Postman pre-request script issues
  - Modified EBNF to OpenAPI converter to generate named schemas for oneOf variants
  - Integrated fixes into Makefile pipeline (not one-time changes)
  - Fixed test data generator to handle `<oneOf>` placeholders
  - Result: Linked collections show `<oneOf>`, test collections rotate through examples
- **2024-02-28**: Added first memory about generating API documentation programmatically and maintaining a single source of truth with EBNF

## Project Memory & Key Patterns

### Critical Files to Remember
- **PROJECT_MEMORY.md** - Comprehensive project knowledge base
- **Makefile** - Main orchestrator (now clean and simplified)
- **data_dictionary/c2mapiv2-dd.ebnf** - Source of truth for API
- **openapi/c2mapiv2-openapi-spec-final.yaml** - Generated API spec
- **postman/scripts/jwt-pre-request.js** - JWT auth integration point

### Key Commands to Remember
```bash
# Most common development command
make postman-instance-build-with-tests

# When things go wrong
make postman-cleanup-all
make prism-mock-test

# Check what's in Postman
make postman-workspace-debug
```

### Common Gotchas
1. **Double encoding bug**: Always use `cat` not `jq -Rs .` for spec content
2. **Workspace switching**: Use orchestrator pattern, not duplicate targets
3. **Auth integration**: Keep in security repo, minimal hooks only
4. **Test failures**: Check allowed status codes (now includes 403)
5. **CI/CD issues**: 
   - Postman CLI must be installed explicitly in GitHub Actions
   - Use CI-specific targets that skip local servers
   - openapi-diff npm version hangs (use npx, temporarily disabled)
6. **OneOf handling**: 
   - openapi-to-postmanv2 simplifies anonymous oneOf schemas to first type only
   - Fix requires converting anonymous schemas to named schemas in OpenAPI
   - Pipeline now includes fix_openapi_oneOf_schemas.py after EBNF conversion
   - Test data generator must recognize `<oneOf>` as a placeholder
7. **Mock Server Architecture** (CRITICAL):
   - Mock server MUST be created from TEST collection, NOT Real World Use Cases
   - TEST collection defines endpoints; Real World collection just sends requests
   - Wrong collection = 404 errors or generic "example" responses
   - Makefile bug at lines 1521-1523 can create mock with wrong collection

### Repository Relationships
- **Main repo**: c2m-api-v2-postman (core API functionality)
- **Security repo**: c2m-api-v2-postman-security (JWT auth implementation)
- **Integration**: Minimal hooks, not full integration