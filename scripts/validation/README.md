# Validation Scripts

Comprehensive validation scripts for post-build verification of the C2M API V2 system.

## Scripts

### verify_mocks.py

Verifies that Prism and Postman mock servers return correct responses matching the OpenAPI specification.

**Features**:
- Tests all endpoints from OpenAPI spec
- Validates response status codes
- Validates response bodies against JSON schemas
- Compares Prism vs Postman consistency
- Generates structured JSON output

**Usage**:
```bash
# Test both mocks
python scripts/validation/verify_mocks.py \
    --prism-url http://localhost:4010 \
    --postman-url https://...mock.pstmn.io

# Test only Prism
python scripts/validation/verify_mocks.py --skip-postman

# Test only Postman
python scripts/validation/verify_mocks.py --skip-prism \
    --postman-url https://...mock.pstmn.io

# Save results to file
python scripts/validation/verify_mocks.py --output reports/mock-verification.json

# Verbose output
python scripts/validation/verify_mocks.py -v
```

**Requirements**:
```bash
pip install requests pyyaml jsonschema
```

### run_newman.sh

Standardized wrapper for Newman test execution with timestamped reporting.

**Features**:
- Multiple reporters (CLI, HTML, JSON, JUnit)
- Timestamped report files
- Configurable output directory
- Verbose mode
- Custom Newman options via environment variable

**Usage**:
```bash
# Basic usage
./scripts/validation/run_newman.sh \
    -c postman/generated/c2mapiv2-test-collection-fixed.json \
    -e postman/mock-env.json

# Custom output directory
./scripts/validation/run_newman.sh \
    -c collection.json \
    -e environment.json \
    -o /tmp/newman-reports

# Custom reporters
./scripts/validation/run_newman.sh \
    -c collection.json \
    -e environment.json \
    -r cli,html,junit

# Verbose mode
./scripts/validation/run_newman.sh \
    -c collection.json \
    -e environment.json \
    -v

# With custom Newman options
NEWMAN_OPTIONS="--delay-request 100" ./scripts/validation/run_newman.sh \
    -c collection.json \
    -e environment.json
```

**Output Files**:
- `reports/newman-{collection}-{timestamp}.html` - HTML report
- `reports/newman-{collection}-{timestamp}.json` - JSON report

## Integration with Makefile

These scripts are integrated into the validation orchestration system:

```bash
# Run all validations (includes mock verification)
make validate-local

# Run only mock verification
make validate-mocks

# Individual components
make validate-secrets
make validate-pipeline
```

## CI/CD Integration

For GitHub Actions:
```yaml
- name: Verify Mocks
  run: |
    python scripts/validation/verify_mocks.py \
      --skip-prism \
      --postman-url https://...mock.pstmn.io \
      --output reports/mock-verification.json

- name: Run Newman Tests
  run: |
    ./scripts/validation/run_newman.sh \
      -c postman/generated/collection.json \
      -e postman/mock-env.json \
      -o reports
```

## Report Output

### verify_mocks.py JSON Output

```json
{
  "spec_path": "openapi/c2mapiv2-openapi-spec-final.yaml",
  "total_endpoints": 9,
  "mocks": {
    "prism": {
      "url": "http://localhost:4010",
      "status": "operational",
      "endpoints_tested": 9,
      "passed": 8,
      "failed": 1,
      "results": [
        {
          "endpoint": "POST /jobs/single-doc",
          "mock": "prism",
          "status_code": 200,
          "success": true,
          "schema_valid": true,
          "schema_error": null,
          "error": null
        }
      ]
    },
    "postman": {
      "url": "https://...mock.pstmn.io",
      "status": "operational",
      "endpoints_tested": 9,
      "passed": 9,
      "failed": 0,
      "results": [...]
    }
  }
}
```

### run_newman.sh Console Output

```
 Running Newman tests...

newman

C2M API v2 Test Collection

→ POST /jobs/single-doc
  YES  Status code is 200
  YES  Response has jobId

┌─────────────────────────┬───────────────────┬───────────────────┐
│                         │          executed │            failed │
├─────────────────────────┼───────────────────┼───────────────────┤
│              iterations │                 1 │                 0 │
├─────────────────────────┼───────────────────┼───────────────────┤
│                requests │                 9 │                 0 │
├─────────────────────────┼───────────────────┼───────────────────┤
│            test-scripts │                18 │                 0 │
├─────────────────────────┼───────────────────┼───────────────────┤
│      prerequest-scripts │                 9 │                 0 │
├─────────────────────────┼───────────────────┼───────────────────┤
│              assertions │                18 │                 0 │
└─────────────────────────┴───────────────────┴───────────────────┘

════════════════════════════════════════════════════════════════
YES Newman tests passed
════════════════════════════════════════════════════════════════

Reports generated:
   HTML: reports/newman-c2mapiv2-test-collection-fixed-20251104-143000.html
   JSON: reports/newman-c2mapiv2-test-collection-fixed-20251104-143000.json
```

## Troubleshooting

### verify_mocks.py

**Error: Missing required package**
```bash
pip install requests pyyaml jsonschema
```

**Error: OpenAPI spec not found**
```bash
# Generate spec first
make generate-openapi-spec-from-ebnf-dd
```

**Error: Connection refused (Prism)**
```bash
# Start Prism mock server
make prism-start
```

### run_newman.sh

**Error: Collection file not found**
```bash
# Generate collection first
make postman-test-collection-generate
```

**Error: npx: command not found**
```bash
# Install Node.js and npm
make install
```

**Error: Newman tests failed**
- Review HTML report for details
- Check environment variables in environment file
- Verify mock server is running
- Check test assertions in collection

## Development

### Adding New Validation Scripts

1. Create script in `scripts/validation/`
2. Make it executable: `chmod +x script.sh`
3. Add documentation to this README
4. Integrate with Makefile validation targets
5. Test locally before committing

### Testing Scripts Locally

```bash
# Test verify_mocks.py
python scripts/validation/verify_mocks.py -v

# Test run_newman.sh
./scripts/validation/run_newman.sh \
    -c postman/generated/c2mapiv2-test-collection-fixed.json \
    -e postman/mock-env.json \
    -v
```

## Related Documentation

- [Validation Gap Analysis](../../VALIDATION_GAP_ANALYSIS.md)
- [Validation Implementation Plan](../../VALIDATION_IMPLEMENTATION_PLAN.md)
- [Validation Summary](../../VALIDATION_SUMMARY.md)
- [Testing Guide](../../tests/README.md)

## Support

For issues or questions:
1. Check this README
2. Review main validation documentation
3. Check Makefile validation targets: `make help | grep validate`
