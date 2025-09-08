# Tests Directory

This directory contains comprehensive test suites for the C2M API, including contract tests, integration tests, authentication tests, and CLI test utilities.

## Directory Structure

```
tests/
├── README.md                    # This file
├── jwt-auth-tests.js           # JWT authentication test suite
├── contract/                   # Contract testing
│   └── validate_against_spec.js # OpenAPI contract validation
├── integration/                # Integration tests
│   └── postman_tests.json     # Postman integration test collection
├── python-cli/                 # Python CLI test utility
│   ├── cli.py                 # CLI implementation
│   └── requirements.txt       # Python dependencies
└── typescript-cli/             # TypeScript CLI test utility
    ├── package.json           # Node dependencies
    ├── tsconfig.json          # TypeScript config
    └── src/
        └── index.ts           # CLI implementation
```

## Test Suites

### JWT Authentication Tests (`jwt-auth-tests.js`)

Comprehensive test suite for JWT authentication flow:

**Test Scenarios:**
1. Long-term token issuance
2. Short-term token exchange
3. Token revocation
4. Invalid credentials handling
5. Token expiration
6. Scope validation
7. Rate limiting
8. Error responses

**Running JWT Tests:**
```bash
# Via Makefile
make jwt-test

# Direct execution
node tests/jwt-auth-tests.js

# With specific environment
JWT_TEST_ENV=staging node tests/jwt-auth-tests.js
```

### Contract Tests (`contract/validate_against_spec.js`)

Validates API responses against OpenAPI specification:

**Features:**
- Schema validation
- Response format checking
- Required field validation
- Type checking
- Enum validation

**Usage:**
```bash
# Validate all endpoints
node tests/contract/validate_against_spec.js

# Validate specific endpoint
node tests/contract/validate_against_spec.js --endpoint /jobs/single-doc
```

### Integration Tests (`integration/postman_tests.json`)

Postman collection for end-to-end testing:

**Test Coverage:**
- All API endpoints
- Success scenarios
- Error scenarios
- Edge cases
- Performance benchmarks

**Running Integration Tests:**
```bash
# Using Newman
make postman-test-collection

# Direct Newman execution
newman run tests/integration/postman_tests.json \
  -e postman/environments/test.json
```

## CLI Test Utilities

### Python CLI (`python-cli/`)

Command-line tool for interactive API testing:

**Features:**
- Interactive endpoint selection
- Dynamic request building
- Response formatting
- Authentication handling

**Setup:**
```bash
cd tests/python-cli
pip install -r requirements.txt
```

**Usage:**
```bash
python cli.py --endpoint /jobs/single-doc-job-template \
              --template standard-letter \
              --document https://example.com/doc.pdf
```

### TypeScript CLI (`typescript-cli/`)

Type-safe CLI for API testing:

**Features:**
- Full TypeScript support
- Auto-completion
- Type validation
- Modern async/await

**Setup:**
```bash
cd tests/typescript-cli
npm install
npm run build
```

**Usage:**
```bash
npm run test -- --endpoint /jobs/single-doc \
                --method POST \
                --data '{"documentUrl": "..."}'
```

## Test Configuration

### Environment Variables

```bash
# API Configuration
API_BASE_URL=https://api.c2m.com/v2
API_KEY=your-api-key

# Test Configuration
TEST_TIMEOUT=30000
TEST_RETRY_COUNT=3
TEST_LOG_LEVEL=debug

# Mock Server
MOCK_SERVER_URL=http://localhost:4010
USE_MOCK=true
```

### Test Data

Test data files location:
- `fixtures/` - Static test data
- `generated/` - Dynamically generated test data
- `responses/` - Captured API responses

## Running Tests

### Full Test Suite
```bash
# Run all tests
make test

# Run with coverage
make test-coverage
```

### Individual Test Suites
```bash
# JWT tests only
make jwt-test

# Contract tests only
make contract-test

# Integration tests only
make integration-test
```

### Continuous Integration
```bash
# CI-friendly output
CI=true make test

# With JUnit reports
make test-ci
```

## Writing New Tests

### Test Structure
```javascript
describe('Endpoint Name', () => {
  it('should handle success case', async () => {
    // Arrange
    const request = buildRequest();
    
    // Act
    const response = await api.call(request);
    
    // Assert
    expect(response.status).toBe(200);
    expect(response.body).toMatchSchema();
  });
});
```

### Best Practices

1. **Isolation**: Tests should not depend on each other
2. **Idempotency**: Tests should be repeatable
3. **Cleanup**: Always clean up test data
4. **Mocking**: Use mocks for external dependencies
5. **Assertions**: Test both success and failure paths

## Test Reports

### Generated Reports
- `coverage/` - Code coverage reports
- `reports/junit.xml` - JUnit test results
- `reports/html/` - HTML test reports

### Viewing Reports
```bash
# Open coverage report
open coverage/index.html

# Open test report
open reports/html/index.html
```

## Debugging Tests

### Debug Mode
```bash
# Enable debug logging
DEBUG=* make test

# Debug specific test
DEBUG=jwt:* node tests/jwt-auth-tests.js
```

### VSCode Debugging
Launch configuration in `.vscode/launch.json`:
```json
{
  "type": "node",
  "request": "launch",
  "name": "Debug Tests",
  "program": "${workspaceFolder}/tests/jwt-auth-tests.js",
  "env": {
    "DEBUG": "*"
  }
}
```

## CI/CD Integration

Tests run automatically in GitHub Actions:
- On every push to main
- On pull requests
- Nightly full test runs

See `.github/workflows/api-ci-cd.yml` for configuration.

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check API key is valid
   - Verify token hasn't expired
   - Ensure correct environment

2. **Network Timeouts**
   - Increase TEST_TIMEOUT
   - Check API server status
   - Verify network connectivity

3. **Schema Validation Errors**
   - Update OpenAPI spec
   - Regenerate test schemas
   - Check for API changes

## Related Documentation

- [API Documentation](../docs/README.md)
- [Postman Collection](../postman/README.md)
- [OpenAPI Specification](../openapi/README.md)
- [CI/CD Pipeline](../.github/workflows/README.md)