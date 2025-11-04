# CI/CD Operations Guide - Dual Repository Architecture

**Date**: 2025-11-04
**Status**: Production Ready
**Repositories**: faserrao/c2m-api-v2-postman + click2mail/c2m-api-v2-postman

---

## Table of Contents

1. [Overview](#overview)
2. [Dual Repository Architecture](#dual-repository-architecture)
3. [Workspace Auto-Detection](#workspace-auto-detection)
4. [CI/CD Flow Diagram](#cicd-flow-diagram)
5. [Local/Manual Flow Diagram](#localmanual-flow-diagram)
6. [Validation System](#validation-system)
7. [Common Operations](#common-operations)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The C2M API V2 project uses a **dual-repository architecture** with **workspace auto-detection** to ensure safe, isolated CI/CD pipelines for development and production environments.

### Key Principles

1. **Repository determines Postman workspace** (CI/CD only)
2. **Validation runs everywhere** (both repos, local + CI/CD)
3. **Identical workflows** (no code divergence between repos)
4. **Local flexibility preserved** (developer controls which workspace to update)

### Repository Mapping

| Repository | Owner | CI/CD Updates | Purpose |
|------------|-------|---------------|---------|
| **faserrao/c2m-api-v2-postman** | faserrao | Personal Postman workspace | Development/Testing |
| **click2mail/c2m-api-v2-postman** | click2mail | Corporate Postman workspace | Production/Team |

---

## Dual Repository Architecture

### Why Two Repositories?

**Mutually Exclusive Pipelines:**
- faserrao CI/CD **cannot** touch Corporate workspace
- click2mail CI/CD **cannot** touch Personal workspace
- Prevents accidental production updates from development work
- Clear separation of development and production environments

**Benefits:**
- ✅ Safety: No cross-contamination possible
- ✅ Clarity: Repository name tells you the environment
- ✅ Flexibility: Independent development and production workflows
- ✅ Simplicity: Identical workflow files (no divergence)

### Repository Synchronization

Both repositories contain **identical code** and are kept in sync:

```bash
# Local repository has two remotes
git remote -v
# origin      https://github.com/faserrao/c2m-api-v2-postman.git
# click2mail  https://github.com/click2mail/c2m-api-v2-postman.git

# Push to both repositories
git push origin main        # Updates faserrao repo
git push click2mail main    # Updates click2mail repo

# Or use git alias to push to both
git ctx-push-both main
```

---

## Workspace Auto-Detection

### How It Works (CI/CD Only)

The GitHub Actions workflow automatically detects which Postman workspace to update based on the **repository owner**:

```yaml
# Identical code in BOTH repositories
if [ "${{ github.repository_owner }}" = "faserrao" ]; then
  POSTMAN_TARGET="personal"
  echo "🎯 Auto-detected workspace: personal (faserrao)"
else
  POSTMAN_TARGET="corporate"
  echo "🎯 Auto-detected workspace: corporate (${{ github.repository_owner }})"
fi
```

### Detection Logic

| Repository Owner | Detected Workspace | API Key Used | Postman Workspace |
|-----------------|-------------------|--------------|-------------------|
| `faserrao` | personal | `POSTMAN_SERRAO_API_KEY` | Personal workspace |
| `click2mail` | corporate | `POSTMAN_C2M_API_KEY` | Corporate/Team workspace |

### Why This Approach?

1. **Immutable**: Repository owner cannot be changed
2. **Self-documenting**: Owner name logically determines workspace
3. **Zero configuration**: No files or variables to configure
4. **Identical workflows**: Same code works in both repos
5. **Safe**: Impossible to misconfigure

---

## CI/CD Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS CI/CD FLOW                     │
└─────────────────────────────────────────────────────────────────┘

Developer pushes code:
  ├── git push origin main         (faserrao repo)
  └── git push click2mail main     (click2mail repo)
                │
                │
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
┌─────────────────┐   ┌─────────────────┐
│  faserrao Repo  │   │ click2mail Repo │
│  GitHub Actions │   │  GitHub Actions │
└─────────────────┘   └─────────────────┘
    │                       │
    │ 1. DETECT WORKSPACE   │
    ├─────────────────────┐ │
    │ Owner: faserrao     │ │ Owner: click2mail
    │ → personal          │ │ → corporate
    └─────────────────────┘ │
    │                       │
    │ 2. BUILD              │
    ├─────────────────────┐ │
    │ • EBNF → OpenAPI    │ │ • EBNF → OpenAPI
    │ • Generate          │ │ • Generate
    │   Collections       │ │   Collections
    │ • Build Docs        │ │ • Build Docs
    └─────────────────────┘ │
    │                       │
    │ 3. PUBLISH            │
    ├─────────────────────┐ │
    │ • Cleanup existing  │ │ • Cleanup existing
    │ • Create API def    │ │ • Create API def
    │ • Upload spec       │ │ • Upload spec
    │ • Create collections│ │ • Create collections
    │ • Create mock       │ │ • Create mock
    │ • Create envs       │ │ • Create envs
    └─────────────────────┘ │
    │                       │
    │ 4. VALIDATE           │
    ├─────────────────────┐ │
    │ • Secret validation │ │ • Secret validation
    │ • Pipeline outputs  │ │ • Pipeline outputs
    │ • Mock verification │ │ • Mock verification
    │ • Generate reports  │ │ • Generate reports
    └─────────────────────┘ │
    │                       │
    │ 5. UPLOAD ARTIFACTS   │
    ├─────────────────────┐ │
    │ • Validation reports│ │ • Validation reports
    │ • OpenAPI specs     │ │ • OpenAPI specs
    │ • Collections       │ │ • Collections
    │ • Documentation     │ │ • Documentation
    └─────────────────────┘ │
    │                       │
    ▼                       ▼
┌──────────────────┐   ┌──────────────────┐
│   PERSONAL       │   │   CORPORATE      │
│   Postman        │   │   Postman        │
│   Workspace      │   │   Workspace      │
│                  │   │                  │
│ • Collections    │   │ • Collections    │
│ • Mock Server    │   │ • Mock Server    │
│ • Environments   │   │ • Environments   │
│ • API Definition │   │ • API Definition │
└──────────────────┘   └──────────────────┘
      ▲                       ▲
      │                       │
      └───────────────────────┘

   MUTUALLY EXCLUSIVE UPDATES
   (No conflicts possible)

Duration: 5-8 minutes per repository
Parallel execution: Both workflows run simultaneously
```

### CI/CD Workflow Steps Detail

**Step 1: Workspace Detection (Auto)**
- Reads `github.repository_owner` context variable
- Sets `POSTMAN_TARGET` to "personal" or "corporate"
- Logs detection for transparency

**Step 2: Build (3-4 minutes)**
- Generate OpenAPI spec from EBNF data dictionary
- Generate Postman collections (Test, Linked, Use Cases)
- Build API documentation (Redocly)
- Generate SDKs (optional)

**Step 3: Publish (1 minute)**
- Cleanup existing resources in detected workspace
- Create API definition in Postman
- Upload OpenAPI spec as standalone
- Create/update collections
- Create mock server from Test collection
- Create environments (Mock + AWS Dev)

**Step 4: Validate (2-3 minutes)**
- Validate secret configuration (.env files)
- Validate pipeline outputs (files exist, structure valid)
- Verify mock server responds correctly
- Run Newman tests (optional)
- Generate consolidated validation report

**Step 5: Upload Artifacts (30 seconds)**
- Upload validation reports (30-day retention)
- Upload OpenAPI specs
- Upload Postman collections
- Upload documentation
- Copy artifacts to artifacts repository

---

## Local/Manual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   LOCAL/MANUAL DEVELOPMENT FLOW                  │
└─────────────────────────────────────────────────────────────────┘

Developer's Local Machine:
  ├── c2m-api-v2-postman/
  │   ├── data_dictionary/
  │   ├── openapi/
  │   ├── postman/
  │   └── .postman-target (local config file - NOT tracked in git)
  │
  └── Working on feature/bugfix

    │
    │ OPTION 1: Use .postman-target file
    │
    ├──> echo "personal" > .postman-target
    │    make postman-publish
    │    └──> Publishes to Personal workspace
    │
    ├──> echo "corporate" > .postman-target
    │    make postman-publish
    │    └──> Publishes to Corporate workspace
    │
    │ OPTION 2: Use explicit targets
    │
    ├──> make postman-publish-personal
    │    └──> Always publishes to Personal workspace
    │
    ├──> make postman-publish-corporate
    │    └──> Always publishes to Corporate workspace
    │
    │ OPTION 3: Publish to BOTH
    │
    └──> make postman-publish-personal && \
         make postman-publish-corporate
         └──> Updates BOTH workspaces

    │
    │ VALIDATION (Local)
    │
    ├──> make validate-local
    │    ├──> Reads .postman-target file
    │    └──> Validates detected workspace
    │
    ├──> make validate-local-personal
    │    └──> Validates Personal workspace
    │
    └──> make validate-local-corporate
         └──> Validates Corporate workspace

    │
    ▼
┌─────────────────────────────────────────┐
│     LOCAL VALIDATION REPORT             │
├─────────────────────────────────────────┤
│ • Secret configuration: ✅              │
│ • Pipeline outputs: ⚠️ 15/20           │
│ • Mock server detection: ✅            │
│ • Newman tests: ⏸️ SKIPPED             │
│ • Report: reports/validation-*.md      │
└─────────────────────────────────────────┘

    │
    │ COMMIT & PUSH
    │
    ├──> git add .
    ├──> git commit -m "feat: add new endpoint"
    │
    │ Push to faserrao (personal development)
    ├──> git push origin main
    │    └──> Triggers faserrao CI/CD → Personal workspace
    │
    │ Push to click2mail (production deployment)
    └──> git push click2mail main
         └──> Triggers click2mail CI/CD → Corporate workspace

KEY POINTS:
• .postman-target file is LOCAL ONLY (ignored by CI/CD)
• Developer chooses workspace when running locally
• CI/CD auto-detects workspace from repository owner
• Validation runs both locally AND in CI/CD
• Full flexibility: update one, both, or neither workspace locally
```

### Local Development Workflow Detail

**Step 1: Edit Source Files**
```bash
# Edit EBNF data dictionary
vim data_dictionary/c2mapiv2-dd.ebnf

# Or edit OpenAPI spec directly
vim openapi/c2mapiv2-openapi-spec-final.yaml
```

**Step 2: Build Locally**
```bash
# Full build pipeline
make postman-instance-build-and-test

# Or individual steps
make generate-openapi-spec-from-ebnf-dd
make postman-collection-build
make docs
```

**Step 3: Choose Workspace (Local Only)**
```bash
# Option A: Set .postman-target file
echo "personal" > .postman-target
make postman-publish

# Option B: Use explicit target
make postman-publish-personal

# Option C: Publish to both
make postman-publish-personal
make postman-publish-corporate
```

**Step 4: Validate Locally**
```bash
# Auto-detect from .postman-target
make validate-local

# Or explicit workspace
make validate-local-personal
make validate-local-corporate

# View reports
cat reports/validation-*.md
```

**Step 5: Commit & Push**
```bash
# Commit changes
git add .
git commit -m "feat: add new endpoint"

# Push to faserrao (dev)
git push origin main

# Push to click2mail (prod)
git push click2mail main

# Or push to both
git push origin main && git push click2mail main
```

---

## Validation System

### Overview

The post-build validation system runs **everywhere**:
- ✅ **Locally**: `make validate-local`
- ✅ **CI/CD (faserrao)**: After publishing to Personal workspace
- ✅ **CI/CD (click2mail)**: After publishing to Corporate workspace

### Validation Components

**1. Secret Configuration Validation**
- Checks `.env` files exist and are valid
- Verifies required API keys are present
- Validates file permissions
- Location: `tests/validate-secrets.sh`

**2. Pipeline Output Validation**
- Validates OpenAPI specs exist and are valid YAML
- Checks Postman collections structure
- Verifies documentation was generated
- Validates mock servers were created
- Location: `tests/validate-pipeline-outputs.sh`

**3. Mock Server Verification**
- Tests Prism local mock (port 4010)
- Tests Postman cloud mock
- Validates responses against OpenAPI schemas
- Location: `scripts/validation/verify_mocks.py`

**4. Newman API Tests**
- Runs test collection against mock server
- Validates all endpoints return 2xx status
- Checks response schemas
- Location: `scripts/validation/run_newman.sh`

**5. Consolidated Report Generation**
- Aggregates results from all components
- Generates markdown report
- Generates JSON data for automation
- Location: `scripts/validation/generate_report.py`

### Validation Execution

**Local Execution:**
```bash
# Full validation suite
make validate-local                    # Auto-detect workspace
make validate-local-personal          # Validate personal
make validate-local-corporate         # Validate corporate

# Individual components
make validate-secrets                 # Secret validation only
make validate-pipeline                # Pipeline outputs only
make validate-mocks                   # Mock servers only
```

**CI/CD Execution:**
```bash
# Runs automatically in GitHub Actions
./scripts/validation/ci_verify.sh personal     # faserrao repo
./scripts/validation/ci_verify.sh corporate    # click2mail repo
```

### Validation Reports

**Location:**
- Local: `reports/validation-YYYYMMDD-HHMMSS.md`
- CI/CD: Uploaded as GitHub Actions artifacts (30-day retention)

**Report Contents:**
```markdown
# C2M API V2 - Validation Report

**Date**: 2025-11-04 21:30:00
**Workspace**: Personal
**Build Type**: Local

## Summary
- **Status**: ✅ PASSED
- **Total Tests**: 20
- **Passed**: 15
- **Failed**: 5
- **Success Rate**: 75.0%

## Component Results

### Secrets ✅
- **Status**: PASSED
- **Tests**: 2/2 passed

### Pipeline ⚠️
- **Status**: PASSED
- **Tests**: 15/20 passed (5 expected failures)

### Mocks ✅
- **Status**: PASSED
- **Tests**: 1/1 passed
```

### Success Criteria

**Passing validation requires:**
- ✅ Secret validation: All checks pass (2/2)
- ✅ Pipeline validation: Core checks pass (≥75%)
- ✅ Mock server detection: Mock server accessible
- ⏸️ Newman tests: Optional (requires published mock)

**Known acceptable failures:**
- Missing examples in OpenAPI spec (expected)
- No pre-request script in linked collection (optional)
- Request naming format variations (minor)
- Newman tests skipped (requires mock server)

---

## Common Operations

### 1. Local Development Workflow

**Scenario**: Working on a new feature, testing in Personal workspace

```bash
# 1. Edit EBNF data dictionary
vim data_dictionary/c2mapiv2-dd.ebnf

# 2. Build locally
make postman-instance-build-and-test

# 3. Publish to Personal workspace
echo "personal" > .postman-target
make postman-publish

# 4. Validate
make validate-local

# 5. Commit
git add .
git commit -m "feat: add customer lookup endpoint"
git push origin main
```

### 2. Production Deployment Workflow

**Scenario**: Deploying tested changes to Corporate workspace

```bash
# 1. Verify local build passes
make postman-instance-build-and-test

# 2. Test in Personal workspace first
make postman-publish-personal
make validate-local-personal

# 3. If validation passes, deploy to production
git push click2mail main

# 4. Monitor CI/CD workflow
gh run watch --repo click2mail/c2m-api-v2-postman

# 5. Download and review validation report
gh run download <RUN_ID> --repo click2mail/c2m-api-v2-postman \
  --name validation-reports
```

### 3. Synchronizing Both Repositories

**Scenario**: Pushing the same code to both repos

```bash
# Option 1: Manual push to both
git push origin main
git push click2mail main

# Option 2: Use git alias
git ctx-push-both main

# Result: BOTH workflows trigger
# - faserrao CI/CD → Personal workspace
# - click2mail CI/CD → Corporate workspace
```

### 4. Testing Changes Locally Without Publishing

**Scenario**: Validate changes before publishing to Postman

```bash
# 1. Build everything locally
make postman-instance-build-and-test

# 2. Start local Prism mock
make prism-start

# 3. Run tests against local mock
make prism-mock-test

# 4. Validate pipeline outputs
make validate-pipeline

# 5. Stop mock server
make prism-stop

# No Postman publish = no changes to any workspace
```

### 5. Publishing to Both Workspaces Locally

**Scenario**: Update both Personal and Corporate workspaces from local build

```bash
# Build once
make postman-instance-build-only

# Publish to Personal
make postman-publish-personal

# Validate Personal
make validate-local-personal

# Publish to Corporate
make postman-publish-corporate

# Validate Corporate
make validate-local-corporate

# Review both validation reports
ls -lt reports/validation-*.md | head -2
```

### 6. Monitoring CI/CD Workflows

**Scenario**: Check status of running workflows

```bash
# List recent runs (both repos)
gh run list --repo faserrao/c2m-api-v2-postman --limit 3
gh run list --repo click2mail/c2m-api-v2-postman --limit 3

# Watch a specific workflow (live updates)
gh run watch <RUN_ID> --repo faserrao/c2m-api-v2-postman

# View workflow logs
gh run view <RUN_ID> --repo faserrao/c2m-api-v2-postman --log

# View only failed steps
gh run view <RUN_ID> --repo faserrao/c2m-api-v2-postman --log-failed

# Download validation reports
gh run download <RUN_ID> --repo faserrao/c2m-api-v2-postman \
  --name validation-reports --dir reports/
```

### 7. Emergency Rollback

**Scenario**: Production deployment broke something, need to rollback

```bash
# 1. Find last good commit
git log --oneline click2mail/main

# 2. Reset to last good commit
git reset --hard <COMMIT_SHA>

# 3. Force push to click2mail (triggers CI/CD)
git push --force click2mail main

# 4. Monitor rollback
gh run watch --repo click2mail/c2m-api-v2-postman

# 5. Verify Corporate workspace restored
make validate-local-corporate
```

---

## Troubleshooting

### Issue: Wrong Workspace Updated in CI/CD

**Symptoms:**
- faserrao workflow published to Corporate workspace
- click2mail workflow published to Personal workspace

**Root Cause:**
- Auto-detection logic broken

**Diagnosis:**
```bash
# Check repository owner
gh api repos/faserrao/c2m-api-v2-postman --jq .owner.login
# Should output: faserrao

gh api repos/click2mail/c2m-api-v2-postman --jq .owner.login
# Should output: click2mail
```

**Solution:**
- Verify workflow file contains correct auto-detection logic
- Check workflow logs for "Auto-detected workspace" message
- Repository owner is immutable - cannot be wrong

---

### Issue: Validation Fails in CI/CD But Passes Locally

**Symptoms:**
- Local validation: ✅ PASS
- CI/CD validation: ❌ FAIL

**Common Causes:**

**1. Different Postman workspaces**
```bash
# Local might be validating Personal workspace
# CI/CD validating Corporate workspace

# Solution: Validate same workspace locally
make validate-local-corporate
```

**2. Timing differences**
```bash
# CI/CD runs immediately after publish
# Local validation runs on old published resources

# Solution: Publish locally before validating
make postman-publish-personal
make validate-local-personal
```

**3. Environment differences**
```bash
# Local: macOS, CI/CD: Ubuntu
# Some dependencies behave differently

# Solution: Check CI logs for specific error
gh run view <RUN_ID> --log-failed
```

---

### Issue: Workflow Not Triggered After Push

**Symptoms:**
- `git push origin main` completes successfully
- No workflow appears in Actions tab

**Diagnosis:**
```bash
# Check if Actions is enabled
gh api repos/faserrao/c2m-api-v2-postman --jq .has_workflows
# Should output: true

# Check workflow file exists
ls -la .github/workflows/api-ci-cd.yml

# Check recent workflow runs
gh run list --repo faserrao/c2m-api-v2-postman --limit 5
```

**Solutions:**

**1. Actions disabled**
- Go to: https://github.com/faserrao/c2m-api-v2-postman/settings/actions
- Enable "Allow all actions and reusable workflows"

**2. Push didn't include workflow file**
```bash
# Ensure workflow file is in repository
git ls-files .github/workflows/api-ci-cd.yml

# If missing, add and push
git add .github/workflows/api-ci-cd.yml
git commit -m "fix: add workflow file"
git push origin main
```

**3. Manual trigger**
```bash
# Trigger workflow manually
gh workflow run api-ci-cd.yml --repo faserrao/c2m-api-v2-postman --ref main
```

---

### Issue: Validation Reports Not Uploaded

**Symptoms:**
- Workflow completes successfully
- No "validation-reports" artifact available

**Diagnosis:**
```bash
# Check workflow run artifacts
gh run view <RUN_ID> --repo faserrao/c2m-api-v2-postman --json artifacts

# Check if validation step ran
gh run view <RUN_ID> --log | grep "Post-Build Validation"
```

**Common Causes:**

**1. Validation step skipped**
- Only runs after Postman publish
- Check if publish step ran

**2. Validation step failed before report generation**
```bash
# Check validation step logs
gh run view <RUN_ID> --log | grep -A 50 "Post-Build Validation"
```

**3. Artifact upload failed**
```bash
# Check artifact upload step
gh run view <RUN_ID> --log | grep -A 10 "Upload Validation Reports"
```

**Solution:**
- Validation always runs if publish completed
- Reports generated even if validation fails
- Check workflow conditions in .github/workflows/api-ci-cd.yml

---

### Issue: Both Repositories Out of Sync

**Symptoms:**
- `git log origin/main..HEAD` shows commits
- `git log click2mail/main..HEAD` shows commits
- Repositories have diverged

**Diagnosis:**
```bash
# Check commit hashes
git log origin/main -1 --oneline
git log click2mail/main -1 --oneline

# Check diff
git log click2mail/main..origin/main --oneline
```

**Solution:**
```bash
# Sync click2mail to faserrao
git push click2mail main

# Or force sync if necessary
git push --force-with-lease click2mail main

# Verify sync
git log origin/main..HEAD        # Should be empty
git log click2mail/main..HEAD    # Should be empty
```

---

### Issue: Postman API Rate Limit Exceeded

**Symptoms:**
- CI/CD fails with "429 Too Many Requests"
- Validation fails to verify mock server

**Root Cause:**
- Both workflows running simultaneously hit rate limit
- Too many API calls in short time

**Solution:**

**1. Stagger workflow runs**
```bash
# Push to repos with delay
git push origin main
sleep 60
git push click2mail main
```

**2. Increase Postman plan**
- Free tier: 1,000 API calls/month
- Basic tier: 10,000 API calls/month
- Professional tier: 100,000 API calls/month

**3. Reduce API calls**
- Skip validation in one repository
- Use `make postman-instance-build-only` (no validation)

---

### Issue: Local .postman-target File Ignored

**Symptoms:**
- Set `.postman-target` to "corporate"
- `make postman-publish` still publishes to personal

**Diagnosis:**
```bash
# Check file exists
cat .postman-target
# Should output: corporate

# Check Makefile reads file
make -n postman-publish | grep POSTMAN_TARGET
```

**Common Causes:**

**1. File in wrong directory**
```bash
# Must be in project root
ls -la .postman-target

# Not in subdirectory
```

**2. Using explicit target**
```bash
# These ignore .postman-target file
make postman-publish-personal     # Always personal
make postman-publish-corporate    # Always corporate

# This reads .postman-target file
make postman-publish
```

**3. File has whitespace**
```bash
# Check for trailing whitespace/newlines
cat -A .postman-target

# Should output: personal$ or corporate$
# Not: personal␣$

# Fix:
echo "corporate" > .postman-target
```

---

## Quick Reference

### CI/CD Commands

```bash
# Monitor workflows
gh run list --repo faserrao/c2m-api-v2-postman --limit 5
gh run list --repo click2mail/c2m-api-v2-postman --limit 5

# Watch workflow (live)
gh run watch <RUN_ID> --repo faserrao/c2m-api-v2-postman

# Download validation reports
gh run download <RUN_ID> --repo faserrao/c2m-api-v2-postman \
  --name validation-reports

# Manual trigger
gh workflow run api-ci-cd.yml --repo faserrao/c2m-api-v2-postman --ref main
```

### Local Build Commands

```bash
# Full build + test + publish + validate
make postman-instance-build-and-test

# Build only (no publish)
make postman-instance-build-only

# Publish only
make postman-publish-personal
make postman-publish-corporate

# Validate only
make validate-local-personal
make validate-local-corporate
```

### Git Operations

```bash
# Push to faserrao (dev)
git push origin main

# Push to click2mail (prod)
git push click2mail main

# Push to both
git push origin main && git push click2mail main

# Check sync status
git log origin/main..HEAD
git log click2mail/main..HEAD
```

### Workspace Configuration (Local Only)

```bash
# Set workspace via file
echo "personal" > .postman-target
echo "corporate" > .postman-target

# Check current setting
cat .postman-target

# Clear setting (use default: personal)
rm .postman-target
```

---

## Summary

### Key Concepts

1. **Dual Repository = Dual Workspace**
   - faserrao repo → Personal Postman workspace
   - click2mail repo → Corporate Postman workspace

2. **Auto-Detection (CI/CD Only)**
   - Repository owner determines workspace
   - No configuration files needed
   - Identical workflows in both repos

3. **Local Flexibility**
   - Developer controls workspace selection
   - Can publish to one, both, or neither
   - `.postman-target` file for convenience

4. **Validation Everywhere**
   - Runs locally: `make validate-local`
   - Runs in CI/CD: automatic after publish
   - Same tests, same reports, same criteria

5. **Mutually Exclusive Pipelines**
   - faserrao CI/CD cannot touch Corporate
   - click2mail CI/CD cannot touch Personal
   - Zero possibility of cross-contamination

### Workflow Summary Table

| Action | Postman Workspace Updated | Validation Runs | Report Location |
|--------|--------------------------|-----------------|-----------------|
| `git push origin main` | Personal (CI/CD) | Yes (CI/CD) | GitHub artifacts |
| `git push click2mail main` | Corporate (CI/CD) | Yes (CI/CD) | GitHub artifacts |
| `make postman-publish-personal` | Personal (local) | No | Run manually |
| `make postman-publish-corporate` | Corporate (local) | No | Run manually |
| `make validate-local-personal` | None | Yes (local) | reports/ directory |
| `make validate-local-corporate` | None | Yes (local) | reports/ directory |

---

**Document Version**: 1.0
**Last Updated**: 2025-11-04
**Maintained By**: Development Team
