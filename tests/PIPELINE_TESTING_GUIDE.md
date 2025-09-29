# C2M API Pipeline Testing Guide

## Overview

This document describes the comprehensive test suite for the C2M API pipeline. The tests are designed to validate the pipeline functionality, ensure regression prevention, and provide confidence in both local and CI/CD environments.

## Test Suite Components

### 1. **Smoke Test** (`smoke-test.sh`)
- **Purpose**: Quick sanity check to ensure basic pipeline functionality
- **Runtime**: ~30 seconds
- **Type**: Integration test
- **Environment**: Local

#### What it tests:
- Core files existence (Makefile, .env, EBNF)
- Required commands availability
- OpenAPI generation
- Collection generation
- Postman API connectivity
- Critical Makefile targets

#### When to run:
- After cloning the repository
- After restoring from backup
- Before starting development
- When troubleshooting basic issues

#### Usage:
```bash
cd tests
chmod +x smoke-test.sh
./smoke-test.sh
```

### 2. **Pipeline Test Suite** (`pipeline-test-suite.sh`)
- **Purpose**: Comprehensive validation of all pipeline components
- **Runtime**: 2-5 minutes
- **Type**: Module + Integration tests
- **Environment**: Local and GitHub Actions compatible

#### Test Categories:

##### Module Tests:
- **Prerequisites**: Commands, environment files, API keys
- **Directory Structure**: All required directories exist
- **Source Files**: EBNF, overlays, custom overrides
- **Scripts**: Python and Node.js script validation
- **Makefile Targets**: All required targets exist

##### Integration Tests:
- **OpenAPI Generation**: EBNF → OpenAPI conversion
- **Collection Generation**: OpenAPI → Postman collection
- **Collection Processing**: Script chain functionality
- **Pipeline Dry Run**: Target execution validation

##### API Tests:
- **Postman Connectivity**: API key and workspace validation
- **GitHub Actions**: Workflow files and CI targets

#### Usage:
```bash
cd tests
chmod +x pipeline-test-suite.sh

# Run all tests
./pipeline-test-suite.sh

# Run specific test categories
./pipeline-test-suite.sh --quick      # Essential tests only
./pipeline-test-suite.sh --module     # Module tests only
./pipeline-test-suite.sh --integration # Integration tests only
./pipeline-test-suite.sh --github     # GitHub Actions tests only
```

### 3. **Pipeline Output Validation** (`validate-pipeline-outputs.sh`)
- **Purpose**: Validate outputs after a pipeline run
- **Runtime**: ~1 minute
- **Type**: Validation/Acceptance test
- **Environment**: Local (after pipeline execution)

#### What it validates:
- **OpenAPI Specs**: Base, final, and with-examples versions
- **Collections**: Structure, flattening, naming, scripts
- **Postman Artifacts**: UIDs, mock servers, environments
- **Documentation**: Redoc output, bundled specs
- **Test Results**: Newman reports, Prism logs

#### When to run:
- After `make postman-instance-build-and-test`
- After CI/CD pipeline completion
- When validating changes
- For acceptance testing

#### Usage:
```bash
cd tests
chmod +x validate-pipeline-outputs.sh
./validate-pipeline-outputs.sh
```

## Testing Strategy

### Local Development Testing

1. **Initial Setup Validation**:
   ```bash
   ./tests/smoke-test.sh
   ```

2. **Pre-Pipeline Validation**:
   ```bash
   ./tests/pipeline-test-suite.sh --module
   ```

3. **Run Pipeline**:
   ```bash
   make postman-cleanup-all
   make postman-instance-build-and-test
   ```

4. **Post-Pipeline Validation**:
   ```bash
   ./tests/validate-pipeline-outputs.sh
   ```

### Continuous Integration Testing

The test suite is designed to work in GitHub Actions:

```yaml
# In .github/workflows/api-ci-cd.yml
- name: Run pipeline tests
  run: |
    ./tests/pipeline-test-suite.sh --github
    
- name: Build pipeline
  run: make openapi-build postman-collection-build docs

- name: Validate outputs
  run: ./tests/validate-pipeline-outputs.sh
```

### Regression Testing

Use these tests to prevent regressions:

1. **Before Major Changes**:
   ```bash
   # Capture baseline
   ./tests/pipeline-test-suite.sh > baseline.txt
   ```

2. **After Changes**:
   ```bash
   # Compare with baseline
   ./tests/pipeline-test-suite.sh > current.txt
   diff baseline.txt current.txt
   ```

## Test Output Interpretation

### Success Indicators

- **Green `[PASS]` messages**: Test passed
- **Blue `[INFO]` messages**: Informational, not failures
- **Exit code 0**: All tests passed

### Failure Indicators

- **Red `[FAIL]` messages**: Test failed
- **Yellow `[WARN]` messages**: Potential issues
- **Exit code 1**: One or more tests failed

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "Command missing" | Install required tool (make, jq, npx, etc.) |
| "POSTMAN_API_KEY not set" | Add to `.env` file |
| "OpenAPI generation failed" | Check Python venv and EBNF file |
| "Collection has nested folders" | Flattening step failed |
| "No test scripts found" | `add_tests.js` script didn't run |

## Extending the Test Suite

### Adding New Tests

1. **Add to existing test functions**:
   ```bash
   # In pipeline-test-suite.sh
   test_my_new_feature() {
       log_section "Testing My New Feature"
       # Add test logic
   }
   ```

2. **Create new test categories**:
   ```bash
   # Add new command line option
   --my-tests)
       test_my_new_feature
       generate_report
       ;;
   ```

### Custom Validation

Create feature-specific validation scripts:

```bash
#!/bin/bash
# tests/validate-auth-integration.sh

# Check auth endpoints
grep -q "/auth/tokens" openapi/c2mapiv2-openapi-spec-final.yaml || exit 1

# Check JWT pre-request script
jq -e '.event[] | select(.listen == "prerequest")' \
    postman/generated/c2mapiv2-linked-collection-flat.json || exit 1
```

## Best Practices

1. **Run smoke test frequently** - It's fast and catches basic issues
2. **Use module tests during development** - Validate as you go
3. **Run full suite before commits** - Ensure nothing is broken
4. **Validate outputs after pipeline runs** - Confirm expected results
5. **Keep tests updated** - Add tests for new features

## Troubleshooting

### Test Suite Issues

**Problem**: Tests fail on fresh clone
**Solution**: 
```bash
make install
python3 -m venv scripts/python_env/e2o.venv
source scripts/python_env/e2o.venv/bin/activate
pip install -r scripts/python_env/requirements.txt
```

**Problem**: Postman API tests fail
**Solution**: Check `.env` file has valid API key and workspace ID

**Problem**: Pipeline tests pass but pipeline fails
**Solution**: Run with verbose output:
```bash
make postman-instance-build-and-test V=1
```

### GitHub Actions Issues

**Problem**: Tests pass locally but fail in CI
**Solution**: Use CI-specific targets:
```bash
# Local
make postman-instance-build-and-test

# CI
make openapi-build
make postman-collection-build
make docs
```

## Summary

The C2M API pipeline test suite provides:

- ✅ **Quick validation** via smoke tests
- ✅ **Comprehensive coverage** via full test suite
- ✅ **Output validation** for acceptance testing
- ✅ **Regression prevention** through consistent testing
- ✅ **CI/CD compatibility** for automated validation

Regular use of these tests ensures pipeline reliability and prevents regressions in both local and CI/CD environments.