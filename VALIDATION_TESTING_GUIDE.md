# Validation System Testing Guide

**Purpose**: Test Phases 1-3 of the post-build validation system before proceeding with CI/CD integration

**Date**: 2025-11-04

---

## Pre-Test Checklist

### ✅ Prerequisites

Ensure these are in place before testing:

```bash
# 1. On feature branch
git branch --show-current
# Should show: feature/post-build-validation

# 2. Python dependencies installed
pip list | grep -E "requests|pyyaml|jsonschema"
# Install if missing:
# pip install requests pyyaml jsonschema

# 3. Node.js and Newman available
npx newman --version
# Should show Newman version

# 4. Workspace configured
cat .postman-target
# Should show: personal or team

# 5. Environment file exists
ls -la .env
# Should exist with POSTMAN API keys
```

---

## Test Suite

### Test 1: Workspace Detection ✅

**What it tests**: Makefile correctly detects workspace from `.postman-target`

```bash
# Check current workspace
cat .postman-target

# Test workspace detection (dry run)
make validate-local --dry-run | head -5

# Expected output:
# echo "🔍 Detected workspace: personal"
# /Library/Developer/CommandLineTools/usr/bin/make validate-local-personal
```

**Pass Criteria**:
- ✅ Detects correct workspace (personal or team)
- ✅ Calls correct sub-target (`validate-local-personal` or `validate-local-team`)

---

### Test 2: Secret Validation ✅

**What it tests**: Environment configuration validation script

```bash
# Run secret validation directly
make validate-secrets

# Expected output:
# 🔐 Validating secrets and environment configuration...
# ✓ .env file exists
# ✓ POSTMAN_SERRAO_API_KEY is set (XX chars)
# ✓ Postman API key is valid
# ✓ Workspace accessible: d8a1f479-...
```

**Pass Criteria**:
- ✅ Detects `.env` file
- ✅ Validates API key format
- ✅ Tests Postman API connectivity
- ✅ Verifies workspace access
- ✅ Exit code 0 on success

**Check Exit Code**:
```bash
make validate-secrets
echo $?  # Should be 0
```

---

### Test 3: Pipeline Validation ✅

**What it tests**: OpenAPI spec, collections, artifacts, documentation validation

```bash
# Run pipeline validation directly
make validate-pipeline

# Expected output:
# 📊 Validating pipeline outputs...
# [CHECK] Validating OpenAPI specifications...
# [PASS] Base OpenAPI spec exists
# [PASS] Final OpenAPI spec exists
# [CHECK] Validating Postman collections...
# [PASS] Linked collection exists
# [PASS] Test collection exists
# ...
# Total validations: XX
# Passed: XX
# Failed: X
```

**Pass Criteria**:
- ✅ Validates OpenAPI specs exist
- ✅ Validates Postman collections exist
- ✅ Validates UID files exist
- ✅ Validates documentation exists
- ✅ Shows summary statistics
- ✅ Exit code 0 if all pass

**Check Exit Code**:
```bash
make validate-pipeline
echo $?  # Should be 0 or 1 depending on results
```

---

### Test 4: Mock Server Detection ✅

**What it tests**: Prism mock server detection and Newman test execution

**Prerequisites**:
```bash
# Start Prism mock server first
make prism-start

# Verify it's running
lsof -i :4010
```

**Run Test**:
```bash
# Run mock validation
make validate-mocks

# Expected output:
# 🧪 Validating mock servers...
#    - Prism mock: http://localhost:4010
#    ✅ Prism mock server is running
#    - Running Newman tests against mocks...
# 🔬 Running Newman tests against Prism mock...
# newman
# C2M API v2 Test Collection
# ...
```

**Pass Criteria**:
- ✅ Detects Prism server on port 4010
- ✅ Runs Newman tests
- ✅ Shows test results
- ✅ Generates HTML report

**Check Report**:
```bash
ls -lh postman/newman-report.html
open postman/newman-report.html  # macOS
```

---

### Test 5: Mock Verification Script ✅

**What it tests**: Mock server response validation against OpenAPI spec

**Prerequisites**:
```bash
# Ensure Prism is running
make prism-start

# Get Postman mock URL from environment
cat postman/mock-env.json | jq -r '.values[] | select(.key=="baseUrl") | .value'
```

**Run Test**:
```bash
# Test Prism mock only
python scripts/validation/verify_mocks.py --skip-postman -v

# Test Postman mock only (replace URL)
python scripts/validation/verify_mocks.py --skip-prism \
    --postman-url https://YOUR-MOCK-URL.mock.pstmn.io -v

# Test both mocks
python scripts/validation/verify_mocks.py \
    --postman-url https://YOUR-MOCK-URL.mock.pstmn.io \
    --output reports/mock-verification.json
```

**Expected Output**:
```
🔬 Mock Server Verification
   OpenAPI Spec: openapi/c2mapiv2-openapi-spec-final.yaml
   Endpoints: 9

📊 Testing Prism Mock: http://localhost:4010
   Testing POST /jobs/single-doc on prism...
   Testing POST /jobs/multi-doc-merge on prism...
   ...
   ✅ Passed: 8/9
   ❌ Failed: 1/9

✅ Validation successful: All endpoints passed
```

**Pass Criteria**:
- ✅ Loads OpenAPI spec correctly
- ✅ Tests all endpoints
- ✅ Validates response status codes
- ✅ Generates JSON output
- ✅ Exit code 0 if all pass

**Check Output**:
```bash
cat reports/mock-verification.json | jq '.summary'
```

---

### Test 6: Newman Wrapper Script ✅

**What it tests**: Newman test execution wrapper with timestamped reports

```bash
# Run Newman wrapper
./scripts/validation/run_newman.sh \
    -c postman/generated/c2mapiv2-test-collection-fixed.json \
    -e postman/mock-env.json \
    -v

# Expected output:
# 🔬 Newman Test Execution
#    Collection: postman/generated/c2mapiv2-test-collection-fixed.json
#    Environment: postman/mock-env.json
#    Output Directory: reports
#    Reporters: cli,html,json
#    Timestamp: 20251104-143000
#
# 🚀 Running Newman tests...
# newman
# ...
# ════════════════════════════════════════════════════════════════
# ✅ Newman tests passed
# ════════════════════════════════════════════════════════════════
#
# Reports generated:
#    HTML: reports/newman-c2mapiv2-test-collection-fixed-20251104-143000.html
#    JSON: reports/newman-c2mapiv2-test-collection-fixed-20251104-143000.json
```

**Pass Criteria**:
- ✅ Creates timestamped reports
- ✅ Generates both HTML and JSON
- ✅ Shows summary statistics
- ✅ Exit code matches test result

**Check Reports**:
```bash
ls -lh reports/newman-*.html
ls -lh reports/newman-*.json
open reports/newman-*.html  # macOS
```

---

### Test 7: Report Generation ✅

**What it tests**: Consolidated validation report generation

```bash
# Generate report (requires prior validation runs)
python scripts/validation/generate_report.py \
    --workspace personal \
    --build-type local \
    --verbose

# Expected output:
# 📊 Aggregating validation results...
#    Collecting secret configuration validation results...
#    Collecting pipeline output validation results...
#    Collecting mock server verification results...
#    Collecting Newman test results...
#
# 📋 Generating validation reports...
#    📝 Markdown report: reports/validation-20251104-143000.md
#    📄 JSON report: reports/validation-20251104-143000.json
#
# ════════════════════════════════════════════════════════════════
# ✅ Validation PASSED: 152/154 tests passed
# ════════════════════════════════════════════════════════════════
```

**Pass Criteria**:
- ✅ Collects results from all components
- ✅ Generates markdown report
- ✅ Generates JSON report
- ✅ Shows summary statistics
- ✅ Exit code matches overall status

**Check Reports**:
```bash
# View markdown report
cat reports/validation-*.md | less

# View JSON summary
cat reports/validation-*.json | jq '.summary'

# Check report structure
cat reports/validation-*.json | jq '.components | keys'
```

---

### Test 8: Complete Validation Flow ✅

**What it tests**: End-to-end validation with all components

**Prerequisites**:
```bash
# Ensure Prism is running
make prism-start

# Verify workspace
cat .postman-target
```

**Run Complete Validation**:
```bash
# Run full validation
make validate-local

# Expected flow:
# 🔍 Detected workspace: personal
#
# ════════════════════════════════════════════════════════════════
#   POST-BUILD VALIDATION - Local Build (Personal Workspace)
# ════════════════════════════════════════════════════════════════
#
# 📋 Running comprehensive validation suite...
#
# 🔐 Validating secrets and environment configuration...
# [Secret validation output...]
#
# 📊 Validating pipeline outputs...
# [Pipeline validation output...]
#
# 🧪 Validating mock servers...
# [Mock validation output...]
#
# 📊 Generating consolidated validation report...
#    📝 Markdown report: reports/validation-20251104-143000.md
#    📄 JSON report: reports/validation-20251104-143000.json
#
# ════════════════════════════════════════════════════════════════
# ✅ Validation PASSED: 152/154 tests passed
# ════════════════════════════════════════════════════════════════
```

**Pass Criteria**:
- ✅ Runs all validation components in order
- ✅ Generates consolidated report
- ✅ Shows clear visual separators
- ✅ Exit code reflects overall status
- ✅ Reports saved to `reports/` directory

**Verify Reports**:
```bash
# List all generated reports
ls -lh reports/

# View markdown report
cat reports/validation-*.md

# View JSON summary
cat reports/validation-*.json | jq '.summary'
```

---

### Test 9: Help Documentation ✅

**What it tests**: Makefile help system includes new targets

```bash
# Check all validation targets
make help | grep validate

# Expected output:
# validate-github-personal  CI validation for personal workspace (no Prism)
# validate-github-team      CI validation for team workspace (no Prism)
# validate-local            Run complete validation (auto-detect workspace from .postman-target)
# validate-local-personal   Run complete validation suite (personal workspace)
# validate-local-team       Run complete validation suite (team workspace)
# validate-mocks            Validate mock servers and run Newman tests
# validate-pipeline         Validate pipeline outputs (OpenAPI, collections, docs)
# validate-secrets          Validate secrets and environment configuration
```

**Pass Criteria**:
- ✅ All 8 validation targets appear
- ✅ Descriptions are clear and helpful
- ✅ Alphabetically sorted

---

### Test 10: Error Handling ✅

**What it tests**: Validation handles errors gracefully

**Test Missing Dependencies**:
```bash
# Test with mock server not running
make prism-stop
make validate-mocks

# Expected:
# ⚠️  Prism mock server is not running
# Run 'make prism-start' to start it
```

**Test Missing Files**:
```bash
# Test with missing OpenAPI spec (backup first!)
mv openapi/c2mapiv2-openapi-spec-final.yaml /tmp/backup.yaml
make validate-pipeline

# Expected:
# [FAIL] Final OpenAPI spec missing

# Restore file
mv /tmp/backup.yaml openapi/c2mapiv2-openapi-spec-final.yaml
```

**Pass Criteria**:
- ✅ Clear error messages
- ✅ Helpful suggestions
- ✅ Non-zero exit codes on failure
- ✅ Doesn't crash

---

## Testing Summary Checklist

Copy this checklist and check off each test as you complete it:

- [ ] Test 1: Workspace Detection
- [ ] Test 2: Secret Validation
- [ ] Test 3: Pipeline Validation
- [ ] Test 4: Mock Server Detection
- [ ] Test 5: Mock Verification Script
- [ ] Test 6: Newman Wrapper Script
- [ ] Test 7: Report Generation
- [ ] Test 8: Complete Validation Flow
- [ ] Test 9: Help Documentation
- [ ] Test 10: Error Handling

---

## Common Issues & Solutions

### Issue: Python packages missing

**Error**: `ModuleNotFoundError: No module named 'requests'`

**Solution**:
```bash
pip install requests pyyaml jsonschema
```

### Issue: Prism not running

**Error**: `⚠️ Prism mock server is not running`

**Solution**:
```bash
make prism-start
# Wait a few seconds
lsof -i :4010  # Verify it's running
```

### Issue: Newman not found

**Error**: `npx: command not found`

**Solution**:
```bash
make install  # Install npm dependencies
```

### Issue: No reports generated

**Error**: No files in `reports/` directory

**Solution**:
```bash
# Ensure directory exists
mkdir -p reports

# Run validation again
make validate-local

# Check for errors
echo $?
```

### Issue: Permission denied

**Error**: `Permission denied: scripts/validation/verify_mocks.py`

**Solution**:
```bash
chmod +x scripts/validation/verify_mocks.py
chmod +x scripts/validation/run_newman.sh
chmod +x scripts/validation/generate_report.py
```

---

## Test Results Template

Use this template to record your test results:

```markdown
# Validation Testing Results

**Date**: YYYY-MM-DD
**Tester**: Your Name
**Branch**: feature/post-build-validation

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| 1. Workspace Detection | ✅ PASS | Detected: personal |
| 2. Secret Validation | ✅ PASS | All secrets valid |
| 3. Pipeline Validation | ✅ PASS | 42/42 tests passed |
| 4. Mock Server Detection | ✅ PASS | Prism running on 4010 |
| 5. Mock Verification Script | ✅ PASS | 9/9 endpoints passed |
| 6. Newman Wrapper Script | ✅ PASS | Reports generated |
| 7. Report Generation | ✅ PASS | MD + JSON created |
| 8. Complete Validation Flow | ✅ PASS | End-to-end working |
| 9. Help Documentation | ✅ PASS | All targets listed |
| 10. Error Handling | ✅ PASS | Clear error messages |

## Overall Assessment

**Status**: ✅ READY FOR MERGE / ⚠️ NEEDS FIXES / ❌ MAJOR ISSUES

**Issues Found**: None / List issues

**Recommendation**: Proceed with Phase 4 / Fix issues first / Other
```

---

## Next Steps After Testing

### If All Tests Pass ✅

1. **Option A: Merge to Main**
   ```bash
   git checkout main
   git merge feature/post-build-validation
   git push origin main
   ```

2. **Option B: Continue with Phase 4**
   - Stay on feature branch
   - Proceed with CI/CD integration
   - Test in GitHub Actions

3. **Option C: Use as-is**
   - Keep on feature branch
   - Use locally for validation
   - Deploy Phases 4-5 later

### If Tests Fail ⚠️

1. Document failures in test results
2. Create GitHub issues for each failure
3. Fix issues on feature branch
4. Re-run tests
5. Proceed when all pass

---

## Support

For testing issues:
1. Check this guide's "Common Issues" section
2. Review script README files:
   - `scripts/validation/README.md`
   - `reports/README.md`
3. Check validation documentation:
   - `VALIDATION_SUMMARY.md`
   - `VALIDATION_GAP_ANALYSIS.md`

---

**Ready to Start Testing?**

Run this command to begin:

```bash
# Start with the simplest test
make validate-secrets
```

Then work through each test in order. Good luck! 🚀
