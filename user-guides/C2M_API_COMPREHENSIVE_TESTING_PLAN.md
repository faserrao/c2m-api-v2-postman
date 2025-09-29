# C2M API V2: Comprehensive Testing Plan
## Infrastructure & Migration Testing

**Date**: 2025-09-25  
**Purpose**: Ensure infrastructure stability before, during, and after API-first migration  
**Scope**: Full pipeline from EBNF → OpenAPI → Postman → Tests → Docs

---

## Table of Contents
1. [Pre-Migration Testing](#1-pre-migration-testing)
2. [Migration Testing](#2-migration-testing)
3. [Post-Migration Testing](#3-post-migration-testing)
4. [Regression Testing](#4-regression-testing)
5. [Performance Testing](#5-performance-testing)
6. [Test Automation Script](#6-test-automation-script)

---

## 1. Pre-Migration Testing

### 1.1 Current State Baseline

**Test ID**: PRE-001  
**Test Name**: Document Current System State  
**Priority**: Critical  
**Steps**:
```bash
# Capture current state
make postman-workspace-debug > baseline/workspace-state-$(date +%Y%m%d-%H%M%S).txt
make print-openapi-vars > baseline/openapi-vars-$(date +%Y%m%d-%H%M%S).txt

# List all Postman resources
ls -la postman/*.txt postman/*.uid 2>/dev/null > baseline/tracking-files.txt

# Capture current collection structure
find postman/generated -name "*.json" -exec jq '.info.name' {} \; > baseline/collections.txt
```

**Expected Result**: Baseline documentation created for comparison

---

### 1.2 Pipeline Component Tests

**Test ID**: PRE-002  
**Test Name**: EBNF to OpenAPI Conversion  
**Priority**: Critical  
**Steps**:
```bash
# Test EBNF conversion
make generate-openapi-spec-from-ebnf-dd

# Validate generated spec
make openapi-spec-lint

# Check for documentSourceIdentifier definition
grep -A 20 "documentSourceIdentifier:" openapi/c2mapiv2-openapi-spec-final.yaml
```

**Expected Result**: 
- OpenAPI spec generated without errors
- Lint passes
- documentSourceIdentifier shows oneOf structure

---

**Test ID**: PRE-003  
**Test Name**: Current Collection Generation  
**Priority**: Critical  
**Steps**:
```bash
# Generate collection from current workflow
make postman-api-linked-collection-generate

# Check generated collection structure
jq '.item[0].request.body.raw' postman/generated/*-collection.json | grep -o "documentSourceIdentifier"
```

**Expected Result**: documentSourceIdentifier appears but not expanded

---

**Test ID**: PRE-004  
**Test Name**: Mock Server Testing  
**Priority**: High  
**Steps**:
```bash
# Start Prism mock
make prism-start

# Test specific endpoint
make prism-test-endpoint PRISM_TEST_ENDPOINT=/jobs/single-doc-job-template

# Check response structure
curl -s http://localhost:4010/jobs/single-doc-job-template | jq '.documentSourceIdentifier'
```

**Expected Result**: Mock returns response (may have issues with oneOf)

---

**Test ID**: PRE-005  
**Test Name**: Test Data Generation  
**Priority**: High  
**Steps**:
```bash
# Run test data generation
make postman-test-collection-add-examples

# Check if documentSourceIdentifier was expanded
jq '.item[].request.body.raw' postman/generated/*with-examples.json | grep -B5 -A5 "documentSourceIdentifier"
```

**Expected Result**: documentSourceIdentifier remains unexpanded

---

### 1.3 CI/CD Pipeline Tests

**Test ID**: PRE-006  
**Test Name**: CI/CD Workflow Execution  
**Priority**: Critical  
**Steps**:
```bash
# Run CI version
make rebuild-all-no-delete-ci

# Check for errors
echo $?
```

**Expected Result**: Exit code 0, no errors

---

## 2. Migration Testing

### 2.1 API Synchronization Tests

**Test ID**: MIG-001  
**Test Name**: API Import and Sync  
**Priority**: Critical  
**Steps**:
```bash
# Import OpenAPI as API
make postman-import-openapi-spec

# Verify API created
test -f postman/postman_api_uid.txt && echo "✅ API UID saved" || echo "❌ No API UID"

# Test sync functionality
make postman-api-sync
```

**Expected Result**: 
- API UID file created
- Sync completes without error

---

**Test ID**: MIG-002  
**Test Name**: Collection Generation from API  
**Priority**: Critical  
**Steps**:
```bash
# Generate collection from API (new method)
make postman-collection-generate-from-api

# Compare structure with old method
diff <(jq -S . old-collection.json) <(jq -S . new-collection.json) || true
```

**Expected Result**: New collection generated with proper structure

---

**Test ID**: MIG-003  
**Test Name**: Schema Propagation Test  
**Priority**: Critical  
**Steps**:
```bash
# Modify EBNF
echo "# Test comment" >> data_dictionary/c2mapiv2-dd.ebnf

# Regenerate and sync
make generate-openapi-spec-from-ebnf-dd
make postman-api-sync
make postman-collection-generate-from-api

# Check if change propagated
# (Compare timestamps or content)
```

**Expected Result**: Changes flow through entire pipeline

---

### 2.2 Example Generation Tests

**Test ID**: MIG-004  
**Test Name**: OneOf Example Handling  
**Priority**: Critical  
**Steps**:
```bash
# Run updated example generator
python3 scripts/test_data_generator_for_openapi_specs/add_examples_to_spec.py openapi/c2mapiv2-openapi-spec-final.yaml

# Check documentSourceIdentifier examples
grep -A 10 "documentSourceIdentifier:" openapi/*with-examples.yaml | grep "example:"
```

**Expected Result**: documentSourceIdentifier has proper example

---

### 2.3 Rollback Tests

**Test ID**: MIG-005  
**Test Name**: Rollback Procedure  
**Priority**: Critical  
**Steps**:
```bash
# Simulate failure scenario
make some-breaking-change

# Execute rollback
git checkout backup-before-api-migration-*

# Verify system state
make postman-workspace-debug
```

**Expected Result**: System returns to pre-migration state

---

## 3. Post-Migration Testing

### 3.1 End-to-End Validation

**Test ID**: POST-001  
**Test Name**: Complete Pipeline Test  
**Priority**: Critical  
**Steps**:
```bash
# Run full scorched earth rebuild
make rebuild-all-with-delete

# Verify all components
make prism-mock-test
make postman-test-collection-validate
```

**Expected Result**: All tests pass

---

**Test ID**: POST-002  
**Test Name**: DocumentSourceIdentifier Expansion  
**Priority**: Critical  
**Steps**:
```bash
# Check final collection
jq '.item[].request.body.raw' postman/generated/*-collection.json | jq -r . | grep -A 10 "documentSourceIdentifier"

# Should see expanded structure like:
# "documentSourceIdentifier": {
#   "documentId": 123
# }
# OR
# "documentSourceIdentifier": {
#   "uploadRequestId": 456,
#   "documentName": "example.pdf"
# }
```

**Expected Result**: documentSourceIdentifier properly expanded

---

### 3.2 Integration Tests

**Test ID**: POST-003  
**Test Name**: Prism Mock with Examples  
**Priority**: High  
**Steps**:
```bash
# Start Prism with new spec
make prism-start

# Test all endpoints
for endpoint in $(grep "^  /" openapi/*-final.yaml | cut -d: -f1); do
  echo "Testing $endpoint"
  curl -s -X POST http://localhost:4010$endpoint \
    -H "Content-Type: application/json" \
    -d '{}' | jq -e '.documentSourceIdentifier' || echo "No documentSourceIdentifier"
done
```

**Expected Result**: Valid responses with proper structures

---

**Test ID**: POST-004  
**Test Name**: Newman Test Execution  
**Priority**: High  
**Steps**:
```bash
# Run Newman tests
make postman-mock

# Check results
grep -i "error\|fail" newman-report.html || echo "No errors found"
```

**Expected Result**: All tests pass

---

## 4. Regression Testing

### 4.1 Backwards Compatibility

**Test ID**: REG-001  
**Test Name**: Legacy Target Compatibility  
**Priority**: Medium  
**Steps**:
```bash
# Test legacy targets still work
make postman-instance-build-and-test-legacy
make rebuild-all-with-delete-legacy
```

**Expected Result**: Legacy targets function (if preserved)

---

### 4.2 Multi-Workspace Testing

**Test ID**: REG-002  
**Test Name**: Workspace Publishing  
**Priority**: High  
**Steps**:
```bash
# Test personal workspace
echo "personal" > .postman-target
make postman-publish-personal

# Test team workspace
echo "team" > .postman-target
make postman-publish-team
```

**Expected Result**: Both workspaces updated correctly

---

## 5. Performance Testing

**Test ID**: PERF-001  
**Test Name**: Pipeline Execution Time  
**Priority**: Medium  
**Steps**:
```bash
# Time full rebuild
time make rebuild-all-with-delete > timing-report.txt 2>&1

# Compare with baseline
# Should not be significantly slower
```

**Expected Result**: < 5 minute execution time

---

**Test ID**: PERF-002  
**Test Name**: Memory Usage  
**Priority**: Low  
**Steps**:
```bash
# Monitor during conversion
/usr/bin/time -l make generate-openapi-spec-from-ebnf-dd 2>&1 | grep "maximum resident"
```

**Expected Result**: < 500MB memory usage

---

## 6. Test Automation Script

### 6.1 Automated Test Runner

Create `run-tests.sh`:
```bash
#!/bin/bash
# C2M API Infrastructure Test Suite

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
PASSED=0
FAILED=0
SKIPPED=0

# Test function
run_test() {
    local test_id=$1
    local test_name=$2
    local test_cmd=$3
    
    echo -e "${YELLOW}Running $test_id: $test_name${NC}"
    
    if eval "$test_cmd"; then
        echo -e "${GREEN}✅ $test_id PASSED${NC}\n"
        ((PASSED++))
    else
        echo -e "${RED}❌ $test_id FAILED${NC}\n"
        ((FAILED++))
    fi
}

# Create test report directory
mkdir -p test-reports/$(date +%Y%m%d-%H%M%S)

echo "🧪 C2M API Infrastructure Test Suite"
echo "===================================="

# Pre-Migration Tests
echo -e "\n📋 Pre-Migration Tests"
run_test "PRE-001" "Document Current State" "make postman-workspace-debug > /dev/null 2>&1"
run_test "PRE-002" "EBNF Conversion" "make generate-openapi-spec-from-ebnf-dd"
run_test "PRE-003" "Collection Generation" "make postman-api-linked-collection-generate"

# Migration Tests
echo -e "\n🔄 Migration Tests"
run_test "MIG-001" "API Import" "make postman-import-openapi-spec"
run_test "MIG-002" "API Sync" "test -f postman/postman_api_uid.txt && echo 'API exists'"

# Post-Migration Tests
echo -e "\n✅ Post-Migration Tests"
run_test "POST-001" "Pipeline Validation" "make openapi-spec-lint"
run_test "POST-002" "Collection Structure" "test -f postman/generated/*-collection.json"

# Summary
echo -e "\n📊 Test Summary"
echo "==============="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed${NC}"
    exit 1
fi
```

### 6.2 Quick Validation Script

Create `validate-migration.sh`:
```bash
#!/bin/bash
# Quick validation of API-first migration

echo "🔍 Validating API-first Migration"

# Check 1: No standalone spec
if grep -q "postman-spec-create-standalone" Makefile; then
    echo "⚠️  Standalone spec creation still present"
else
    echo "✅ Standalone spec removed"
fi

# Check 2: API sync exists
if grep -q "postman-api-sync" Makefile; then
    echo "✅ API sync target found"
else
    echo "❌ API sync target missing"
fi

# Check 3: Collection from API
if grep -q "postman-collection-generate-from-api" Makefile; then
    echo "✅ API-based collection generation found"
else
    echo "❌ API-based collection generation missing"
fi

# Check 4: Example handling
if grep -q "oneOf.*in.*schema" scripts/test_data_generator_for_openapi_specs/add_examples_to_spec.py; then
    echo "✅ OneOf handling implemented"
else
    echo "⚠️  OneOf handling may be missing"
fi

echo -e "\n📋 Migration checklist complete"
```

---

## Test Execution Plan

1. **Before Migration**: Run sections 1 and 6.2
2. **During Migration**: Run section 2 after each change
3. **After Migration**: Run sections 3, 4, and 5
4. **Continuous**: Use 6.1 for automated regression testing

## Success Criteria

- All PRE tests pass before starting migration
- All MIG tests pass during migration
- All POST tests pass after migration
- No regression in REG tests
- Performance metrics within acceptable range