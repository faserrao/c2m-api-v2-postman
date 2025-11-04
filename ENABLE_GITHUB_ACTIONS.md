# Enable GitHub Actions - Quick Guide

## Current Status

GitHub Actions is currently **DISABLED** on this repository. This is preventing the post-build validation workflow from running automatically after the merge to main.

## Why is Actions Disabled?

GitHub disables Actions by default on newly created repositories or when there are security concerns. This is a safety measure.

## How to Enable (60 seconds)

### Step 1: Navigate to Settings

Click on the repository link:
```
https://github.com/faserrao/c2m-api-v2-postman/settings/actions
```

**OR** manually navigate:
1. Go to https://github.com/faserrao/c2m-api-v2-postman
2. Click **Settings** tab (top right)
3. Click **Actions** → **General** (left sidebar)

### Step 2: Enable Actions

On the Actions settings page, you'll see:

```
Workflows aren't being run on this repository

GitHub Actions is not currently enabled on this repository.
```

**Click the green button**: `Enable Actions on this repository`

### Step 3: Verify Enabled

After clicking enable, you should see:

- **Actions permissions** section (radio buttons)
- **Workflow permissions** section
- No more warning about Actions being disabled

## What Happens Next?

### Automatic Workflow Trigger

The validation workflow should trigger automatically because:
1. The merge to main happened **after** Actions was disabled
2. GitHub queues push events when Actions is disabled
3. Enabling Actions will process the queued event

**If the workflow doesn't trigger automatically**, you can trigger it manually:

```bash
# Using gh CLI
gh workflow run api-ci-cd.yml --ref main

# Or via GitHub UI
# https://github.com/faserrao/c2m-api-v2-postman/actions/workflows/api-ci-cd.yml
# Click "Run workflow" button
```

### Expected Workflow Execution

The "API Spec, Docs, and Postman CI/CD" workflow will:

1. **Build** - Generate OpenAPI spec, Postman collections, docs (3-4 min)
2. **Publish** - Publish to Postman workspace (1 min)
3. **Validate** - Run post-build validation (2-3 min)
4. **Upload** - Save validation reports as artifacts (30s)

**Total Duration**: 5-8 minutes

## Monitoring the Workflow

### Option 1: GitHub CLI
```bash
cd /Users/frankserrao/Dropbox/Customers/c2m/projects/c2m-api/C2M_API_v2/c2m-api-v2-postman

# List recent runs
gh run list --workflow=api-ci-cd.yml --limit 5

# Watch a specific run (replace RUN_ID)
gh run watch RUN_ID

# View logs
gh run view RUN_ID --log
```

### Option 2: GitHub Web UI
```
https://github.com/faserrao/c2m-api-v2-postman/actions
```

Look for the workflow run with:
- **Workflow**: API Spec, Docs, and Postman CI/CD
- **Trigger**: push
- **Branch**: main
- **Event**: The merge commit from feature/post-build-validation

## Validation Reports

After the workflow completes successfully, download the validation reports:

### Via GitHub CLI
```bash
# List artifacts from latest run
gh run list --workflow=api-ci-cd.yml --limit 1 --json databaseId --jq '.[0].databaseId' | \
  xargs -I {} gh run download {} --name validation-reports --dir reports/

# This downloads to reports/ directory
```

### Via GitHub Web UI
1. Navigate to: https://github.com/faserrao/c2m-api-v2-postman/actions
2. Click on the most recent workflow run
3. Scroll down to **Artifacts** section
4. Click **validation-reports** to download (ZIP file)
5. Extract to see:
   - `validation-YYYYMMDD-HHMMSS.md` - Human-readable report
   - `validation-YYYYMMDD-HHMMSS.json` - Machine-readable data
   - `newman-*.html` - Newman test report (if tests ran)

## Expected Validation Results

Based on local testing, expect:

- **Secrets Validation**: ✅ PASS (2/2 checks)
- **Pipeline Validation**: ⚠️ PARTIAL (15/20 checks, 5 expected failures)
- **Mock Server Detection**: ✅ PASS (1/1 check)
- **Newman Tests**: ⏸️ SKIPPED (requires published mock server)
- **Report Generation**: ✅ PASS

**Overall Status**: Should show "PASSED" (all critical validations passing)

## Success Criteria

The post-build validation system is working correctly when:

1. ✅ GitHub Actions enabled
2. ✅ Workflow triggered automatically or manually
3. ✅ "Run Post-Build Validation" step completes successfully
4. ✅ Validation reports uploaded as artifacts
5. ✅ Report shows reasonable pass rate (>75%)

## Troubleshooting

### Workflow Still Not Triggering

If the workflow doesn't trigger after enabling Actions:

```bash
# Manual trigger
gh workflow run api-ci-cd.yml --ref main
```

### Validation Step Fails

Check the workflow logs:
```bash
gh run list --workflow=api-ci-cd.yml --limit 1
# Note the RUN_ID, then:
gh run view RUN_ID --log-failed
```

Common issues:
- **Python packages not installed**: CI script creates venv automatically
- **Postman API key missing**: Check repository secrets
- **Mock server not found**: Expected if not published yet

### Need Help

Review these documents:
- `VALIDATION_CI_CD_INTEGRATION.md` - Complete CI/CD guide
- `VALIDATION_TESTING_GUIDE.md` - 10-test suite with troubleshooting
- `scripts/validation/README.md` - Script documentation

## Quick Reference

| Action | Command |
|--------|---------|
| Enable Actions | Click button at https://github.com/faserrao/c2m-api-v2-postman/settings/actions |
| Trigger workflow | `gh workflow run api-ci-cd.yml --ref main` |
| Watch workflow | `gh run watch <RUN_ID>` |
| View logs | `gh run view <RUN_ID> --log` |
| Download reports | `gh run download <RUN_ID> --name validation-reports` |
| Check status | https://github.com/faserrao/c2m-api-v2-postman/actions |

---

**Next Step**: Click the "Enable Actions on this repository" button and wait for the workflow to complete (5-8 minutes).
