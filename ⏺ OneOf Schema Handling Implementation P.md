⏺ OneOf Schema Handling Implementation Plan for C2M API

  Executive Summary

  This document outlines a comprehensive solution to fix the oneOf schema handling issue in the C2M API Postman collection generation pipeline. The issue prevents
  proper representation of complex object structures in API requests, affecting testing and mock server functionality.

  Problem Statement

  Current Issue

  - What's happening: Fields defined with oneOf schemas (e.g., documentSourceIdentifier, recipientAddressSource, paymentDetails) are being populated with simple
  string values instead of proper complex object structures
  - Impact: Mock servers reject requests, tests fail, and API documentation shows incorrect examples
  - Root causes:
    a. openapi-to-postmanv2 tool doesn't properly handle oneOf examples from OpenAPI specs
    b. addRandomDataToRaw.js overwrites any existing examples with simple random strings

  Example

  // Current (incorrect):
  "documentSourceIdentifier": "ASqKrjIq43"

  // Expected (one of these):
  "documentSourceIdentifier": 1234
  "documentSourceIdentifier": "https://api.example.com/v1/documents/1234"
  "documentSourceIdentifier": {
      "uploadRequestId": 123,
      "documentName": "document_456.pdf"
  }

  Proposed Solution

  Overview

  Replace the current addRandomDataToRaw.js with a oneOf-aware version that:
  1. Recognizes oneOf fields from a predefined configuration
  2. Preserves existing valid examples
  3. Rotates through different oneOf variants for comprehensive testing
  4. Falls back to intelligent data generation for non-oneOf fields

  Why This Solution Will Work

  1. Direct Problem Resolution: By making the data generator oneOf-aware, we address the exact point where examples get corrupted
  2. Preserves Pipeline: No need to modify the OpenAPI spec or change the conversion tool
  3. Backward Compatible: The new script maintains the same interface as the old one
  4. Enhanced Testing: Rotation feature ensures all oneOf variants get tested over time
  5. Maintainable: New oneOf schemas can be added to a central configuration

  Implementation Plan

  Phase 1: Preparation (Day 1)

  Step 1.1: Backup Current Implementation

  # Backup existing script
  cp scripts/test_data_generator_for_collections/addRandomDataToRaw.js \
     scripts/test_data_generator_for_collections/addRandomDataToRaw.js.backup

  # Create test collection snapshots
  cp postman/generated/*.json backup/pre-fix/

  Step 1.2: Document Current OneOf Schemas

  Create a comprehensive list of all oneOf fields in the API:
  - documentSourceIdentifier (5 variants)
  - recipientAddressSource (3 variants)
  - paymentDetails (6 variants)
  - submitSingleDocWithTemplateParams (3 variants)

  Phase 2: Implementation (Day 1-2)

  Step 2.1: Create OneOf-Aware Script

  Create scripts/active/addRandomDataToRaw_oneOf.js with:
  - OneOf fixture definitions
  - Rotation mechanism
  - Preservation logic for existing examples
  - Fallback to faker for other fields

  Step 2.2: Integration Testing

  # Test with a single collection
  node scripts/active/addRandomDataToRaw_oneOf.js \
    --input postman/generated/c2mapiv2-collection.json \
    --output postman/generated/test-oneOf.json

  # Verify oneOf fields have proper structure
  jq '.item[].item[]?.request.body.raw' postman/generated/test-oneOf.json | \
    grep -A5 documentSourceIdentifier

  Step 2.3: Update Makefile

  # Add new variable
  ADD_EXAMPLES_ONEOF_AWARE := node $(SCRIPTS_DIR)/active/addRandomDataToRaw_oneOf.js

  # Update the examples target
  postman-test-collection-add-examples:
        @echo "🧩 Adding smart example data with oneOf support..."
        $(ADD_EXAMPLES_ONEOF_AWARE) \
          --input $(POSTMAN_COLLECTION_RAW) \
          --output $(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES)

  Phase 3: Validation (Day 2)

  Step 3.1: Unit Testing

  Create test cases for:
  - Each oneOf variant generates correctly
  - Rotation works across multiple calls
  - Existing examples are preserved
  - Non-oneOf fields still get random data

  Step 3.2: Pipeline Testing

  # Full pipeline test
  make postman-cleanup-all
  make postman-instance-build-and-test

  # Verify mock server accepts requests
  newman run postman/generated/c2mapiv2-test-collection-fixed.json \
    --environment postman/mock-env.json

  Step 3.3: Regression Testing

  - Run existing test suite
  - Compare output with baseline
  - Ensure no breaking changes

  Phase 4: Rollout (Day 3)

  Step 4.1: Staged Deployment

  1. Deploy to development environment
  2. Run CI/CD pipeline
  3. Monitor for issues
  4. Deploy to production

  Step 4.2: Documentation Updates

  - Update CLAUDE.md with new oneOf handling
  - Add examples to README
  - Create troubleshooting guide

  Risk Analysis & Mitigation

  Risk 1: Breaking Existing Tests

  - Probability: Medium
  - Impact: High
  - Mitigation:
    - Keep backward compatibility flag
    - Run parallel testing with old/new versions
    - Gradual rollout with feature flag

  Risk 2: Performance Degradation

  - Probability: Low
  - Impact: Medium
  - Mitigation:
    - Profile script performance
    - Optimize fixture lookups
    - Cache parsed JSON structures

  Risk 3: Incomplete OneOf Coverage

  - Probability: Medium
  - Impact: Medium
  - Mitigation:
    - Audit all oneOf schemas in OpenAPI spec
    - Create automated detection of new oneOf fields
    - Regular review process

  Risk 4: CI/CD Pipeline Disruption

  - Probability: Low
  - Impact: High
  - Mitigation:
    - Test in isolated environment first
    - Have rollback plan ready
    - Monitor pipeline metrics

  Success Criteria

  1. Functional: All oneOf fields generate valid complex objects
  2. Coverage: Each oneOf variant appears in test runs
  3. Performance: No increase in generation time > 10%
  4. Compatibility: Existing tests continue to pass
  5. Maintainability: New oneOf schemas can be added in < 5 minutes

  Monitoring & Maintenance

  Monitoring Points

  - Collection generation success rate
  - Mock server request acceptance rate
  - Test pass/fail rates
  - OneOf variant distribution in tests

  Maintenance Tasks

  - Weekly: Review for new oneOf schemas
  - Monthly: Analyze rotation coverage
  - Quarterly: Performance optimization review

  Alternative Approaches (Not Recommended)

  Alternative 1: Patch openapi-to-postmanv2

  - Why not: Requires forking and maintaining external tool
  - Complexity: High
  - Risk: Updates to tool break our patches

  Alternative 2: Post-process with Python/jq

  - Why not: Adds another step to pipeline
  - Complexity: Medium
  - Risk: Harder to maintain business logic

  Alternative 3: Manual examples in Postman

  - Why not: Not scalable, breaks automation
  - Complexity: Low
  - Risk: Human error, maintenance burden

  Implementation Checklist

  - Backup current implementation
  - Document all oneOf schemas
  - Create oneOf-aware script
  - Test script in isolation
  - Update Makefile integration
  - Run unit tests
  - Run integration tests
  - Update documentation
  - Deploy to development
  - Monitor for 24 hours
  - Deploy to production
  - Close out implementation

  Conclusion

  This solution directly addresses the oneOf handling issue at the point where it occurs, maintaining compatibility with the existing pipeline while adding robust
  support for complex schemas. The rotation feature provides comprehensive test coverage, and the implementation is maintainable and extensible for future API
  evolution.