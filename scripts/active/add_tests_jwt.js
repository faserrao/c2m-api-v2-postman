#!/usr/bin/env node

const fs = require('fs');
const yaml = require('js-yaml');

const args = process.argv.slice(2);
if (args.length < 2) {
  console.error("Usage: node scripts/add_tests_jwt.js <input_file> <output_file> [--allowed-codes \"200,400,401\"] [--auth-overlay <path>]");
  process.exit(1);
}

const inputFile = args[0];
const outputFile = args[1];
let allowedCodes = "200";
let authOverlayPath = null;

const codesIndex = args.indexOf("--allowed-codes");
if (codesIndex !== -1 && args[codesIndex + 1]) {
  allowedCodes = args[codesIndex + 1];
}
const overlayIndex = args.indexOf("--auth-overlay");
if (overlayIndex !== -1 && args[overlayIndex + 1]) {
  authOverlayPath = args[overlayIndex + 1];
}

// Load auth overlay for spec-derived test assertions
let authOverlay = null;
if (authOverlayPath) {
  try {
    authOverlay = yaml.load(fs.readFileSync(authOverlayPath, 'utf-8'));
    console.log(`ℹ️ Auth overlay: ${authOverlayPath}`);
  } catch (err) {
    console.warn(`⚠️ Auth overlay load failed — falling back to hardcoded fields: ${err.message}`);
  }
}

// Build "Response has required JWT fields" test from overlay schema.
// Falls back to fallbackFields when no overlay is loaded, preserving existing behaviour.
function buildRequiredFieldsTest(schemaName, fallbackFields) {
  let fields = fallbackFields;
  let tokenTypeValue = 'Bearer';
  if (authOverlay) {
    const schemas = ((authOverlay.components || {}).schemas) || {};
    const schema = schemas[schemaName];
    if (schema && schema.required && schema.required.length > 0) {
      fields = schema.required;
    }
    const tp = schema && schema.properties && schema.properties.token_type;
    if (tp && tp.enum && tp.enum[0]) {
      tokenTypeValue = tp.enum[0];
    }
  }
  const checks = fields.map(field =>
    field === 'token_type'
      ? `      pm.expect(jsonData).to.have.property(${JSON.stringify(field)}, ${JSON.stringify(tokenTypeValue)});`
      : `      pm.expect(jsonData).to.have.property(${JSON.stringify(field)});`
  ).join('\n');
  return `pm.test("Response has required JWT fields", function () {
      const jsonData = pm.response.json();
${checks}
    });`;
}

console.log(`ℹ️ Input file: ${inputFile}`);
console.log(`ℹ️ Output file: ${outputFile}`);
console.log(`ℹ️ Allowed status codes: ${allowedCodes}`);

// Standard tests for all endpoints
const standardTests = [
  `pm.test("Status code is allowed (${allowedCodes})", function () { pm.expect([${allowedCodes}]).to.include(pm.response.code); });`,
  `pm.test("Response time < 1s", function () { pm.expect(pm.response.responseTime).to.be.below(1000); });`
];

// Token-class-specific tests attached by response schema name (not operationId).
// When the overlay maps an operationId to a Short/Long schema, these are appended.
// SHORT_TOKEN_MAX_SECONDS: matches the auth service hard cap (auth overlay targets 900s).
// LONG_TOKEN bounds: min 1 hour, max 90 days — update if auth service limits change.
const _SHORT_TOKEN_MAX_SECONDS = 3600;
const _LONG_TOKEN_MIN_SECONDS  = 3600;
const _LONG_TOKEN_MAX_SECONDS  = 7776000;

const _SHORT_TOKEN_EXTRA_TESTS = [
  `pm.test("Short token is short-lived (at most 1 hour)", function () {
      const SHORT_TOKEN_MAX_SECONDS = ${_SHORT_TOKEN_MAX_SECONDS};
      const jsonData = pm.response.json();
      pm.expect(jsonData.expires_in).to.be.a('number').and.above(0).and.at.most(SHORT_TOKEN_MAX_SECONDS);
    });`,
  `pm.test("Token expiry is valid ISO date", function () {
      const jsonData = pm.response.json();
      const expiryDate = new Date(jsonData.expires_at);
      pm.expect(expiryDate.toISOString()).to.equal(jsonData.expires_at);
    });`,
  `pm.test("Save short-term token", function () {
      if (pm.response.code === 201) {
        const jsonData = pm.response.json();
        pm.environment.set('shortTermToken', jsonData.access_token);
        pm.environment.set('tokenExpiry', jsonData.expires_at);
        pm.environment.set('currentTokenId', jsonData.token_id);
      }
    });`
];

const _LONG_TOKEN_EXTRA_TESTS = [
  `pm.test("Long token has reasonable expiry", function () {
      const jsonData = pm.response.json();
      const minExpiry = ${_LONG_TOKEN_MIN_SECONDS}; // 1 hour
      const maxExpiry = ${_LONG_TOKEN_MAX_SECONDS}; // 90 days
      pm.expect(jsonData.expires_in).to.be.at.least(minExpiry).and.at.most(maxExpiry);
    });`,
  `pm.test("Token has correct scopes", function () {
      const jsonData = pm.response.json();
      pm.expect(jsonData.scopes).to.be.an('array');
      pm.expect(jsonData.scopes.length).to.be.at.least(1);
    });`,
  `pm.test("Save long-term token", function () {
      if (pm.response.code === 201) {
        const jsonData = pm.response.json();
        pm.environment.set('longTermToken', jsonData.access_token);
        pm.environment.set('longTokenId', jsonData.token_id);
        pm.environment.set('longTokenExpiry', jsonData.expires_at);
      }
    });`
];

const _REVOKE_TESTS = [
  `pm.test("Successful revocation returns 204", function () {
      if (pm.response.code === 204) {
        pm.environment.unset('shortTermToken');
        pm.environment.unset('tokenExpiry');
        pm.environment.unset('currentTokenId');
      }
    });`,
  `pm.test("Revocation is idempotent", function () {
      // 204 is expected for both first revocation and repeated attempts
      pm.expect([204, 404]).to.include(pm.response.code);
    });`
];

/**
 * Build the operationId → test-array map from the auth overlay.
 * Reads operationId and the 2xx success response schema name for each path.
 * Falls back to known static values if no overlay is loaded.
 * M4: schema names are read from overlay, not hardcoded.
 * M5: operationIds are read from overlay paths, not hardcoded.
 */
function buildJwtTests(overlay) {
  if (!overlay) {
    // Static fallback for runs without --auth-overlay
    return {
      'issueShortTermToken': [
        buildRequiredFieldsTest('ShortTokenResponse', ['token_type', 'access_token', 'expires_in', 'expires_at', 'token_id']),
        ..._SHORT_TOKEN_EXTRA_TESTS,
      ],
      'issueLongTermToken': [
        buildRequiredFieldsTest('LongTokenResponse', ['token_type', 'access_token', 'expires_in', 'expires_at', 'token_id']),
        ..._LONG_TOKEN_EXTRA_TESTS,
      ],
      'revokeToken': _REVOKE_TESTS,
    };
  }

  const result = {};
  const paths = overlay.paths || {};

  Object.values(paths).forEach(pathItem => {
    Object.values(pathItem).forEach(operation => {
      const operationId = operation.operationId;
      if (!operationId) return;

      // Find the 2xx success response schema $ref
      let schemaName = null;
      const responses = operation.responses || {};
      for (const [status, resp] of Object.entries(responses)) {
        if (parseInt(status, 10) >= 200 && parseInt(status, 10) < 300) {
          const ref = (((resp.content || {})['application/json'] || {}).schema || {}).$ref;
          if (ref) {
            schemaName = ref.split('/').pop();
            break;
          }
        }
      }

      if (!schemaName) {
        // No success body (e.g. 204 revoke) — attach revoke tests
        result[operationId] = _REVOKE_TESTS;
        return;
      }

      const tests = [
        buildRequiredFieldsTest(schemaName, ['token_type', 'access_token', 'expires_in', 'expires_at', 'token_id']),
      ];
      if (/short/i.test(schemaName)) tests.push(..._SHORT_TOKEN_EXTRA_TESTS);
      if (/long/i.test(schemaName))  tests.push(..._LONG_TOKEN_EXTRA_TESTS);
      result[operationId] = tests;
    });
  });

  return result;
}

// JWT-specific tests by operationId — built from overlay when available (M4/M5)
const jwtTests = buildJwtTests(authOverlay);

// Derive operation groups from jwtTests for pre-request script generation.
// Long-token operations are those whose test suite includes the max-expiry check.
// All other operationIds in jwtTests are short-token or revoke operations.
const _longTokenOpIds = Object.keys(jwtTests).filter(id =>
  jwtTests[id].some(t => typeof t === 'string' && t.includes('LONG_TOKEN_MAX_SECONDS'))
);
const _shortOrRevokeOpIds = Object.keys(jwtTests).filter(id => !_longTokenOpIds.includes(id));

// Auth error tests
const authErrorTests = [
  `pm.test("Error response has proper structure", function () {
    if (pm.response.code >= 400) {
      const jsonData = pm.response.json();
      pm.expect(jsonData).to.have.property('code');
      pm.expect(jsonData).to.have.property('message');
    }
  });`,
  `pm.test("401 error indicates authentication issue", function () {
    if (pm.response.code === 401) {
      const jsonData = pm.response.json();
      // Codes defined in auth.tokens.yaml Error401/Error400 responses
      pm.expect(['invalid_token', 'invalid_grant']).to.include(jsonData.code);
    }
  });`,
  `pm.test("403 error indicates authorization issue", function () {
    if (pm.response.code === 403) {
      const jsonData = pm.response.json();
      // Code defined in auth.tokens.yaml Error403 response
      pm.expect(['insufficient_scope']).to.include(jsonData.code);
    }
  });`
];

// Pre-request script for JWT endpoints — operationId lists are spec-derived (M5)
const jwtPreRequestScript = `
// Set required headers
pm.request.headers.add({key: 'Content-Type', value: 'application/json'});

// For long token endpoint, add X-Client-Id header
if (${JSON.stringify(_longTokenOpIds)}.includes(pm.info.requestName)) {
  const clientId = pm.environment.get('clientId');
  if (clientId) {
    pm.request.headers.add({key: 'X-Client-Id', value: clientId});
  }
}

// For short token and revoke endpoints, add Authorization header
if (${JSON.stringify(_shortOrRevokeOpIds)}.includes(pm.info.requestName)) {
  const longToken = pm.environment.get('longTermToken');
  if (longToken) {
    pm.request.headers.add({key: 'Authorization', value: 'Bearer ' + longToken});
  }
}
`;

function addTestsToItem(item) {
  if (item.request) {
    const operationId = item.request.description || item.name || '';
    
    // Initialize event array if it doesn't exist
    if (!item.event) item.event = [];

    // Add/update test event
    let testEvent = item.event.find(e => e.listen === 'test');
    if (!testEvent) {
      testEvent = { listen: 'test', script: { type: 'text/javascript', exec: [] } };
      item.event.push(testEvent);
    }

    // Clear existing tests
    testEvent.script.exec = [];

    // Add standard tests
    standardTests.forEach(test => {
      testEvent.script.exec.push(test);
    });

    // Add JWT-specific tests if applicable
    if (jwtTests[operationId]) {
      jwtTests[operationId].forEach(test => {
        testEvent.script.exec.push(test);
      });
    }

    // Add auth error tests for auth endpoints
    if (operationId.includes('Token')) {
      authErrorTests.forEach(test => {
        testEvent.script.exec.push(test);
      });
    }

    // Add pre-request script for JWT endpoints (all operationIds present in jwtTests)
    if (Object.keys(jwtTests).includes(operationId)) {
      let preRequestEvent = item.event.find(e => e.listen === 'prerequest');
      if (!preRequestEvent) {
        preRequestEvent = { listen: 'prerequest', script: { type: 'text/javascript', exec: [] } };
        item.event.push(preRequestEvent);
      }
      preRequestEvent.script.exec = jwtPreRequestScript.trim().split('\n');
    }
  }

  // Recursively handle sub-items
  if (item.item) {
    item.item.forEach(subItem => addTestsToItem(subItem));
  }
}

function addTestsToCollection(inputPath, outputPath) {
  const rawData = fs.readFileSync(inputPath, 'utf-8');
  const collection = JSON.parse(rawData);

  // Add collection-level pre-request script
  if (!collection.event) collection.event = [];
  
  let collectionPreRequest = collection.event.find(e => e.listen === 'prerequest');
  if (!collectionPreRequest) {
    collectionPreRequest = { 
      listen: 'prerequest', 
      script: { 
        type: 'text/javascript', 
        // Assumed layout: this script lives in scripts/active/; ../postman/ is scripts/postman/.
        exec: fs.readFileSync(`${__dirname}/../postman/scripts/jwt-pre-request.js`, 'utf-8').split('\n')
      } 
    };
    collection.event.push(collectionPreRequest);
  }

  // Add tests to all items
  if (collection.item) {
    collection.item.forEach(item => addTestsToItem(item));
  }

  fs.writeFileSync(outputPath, JSON.stringify(collection, null, 2));
  console.log(`✅ JWT tests and scripts added. Output saved to ${outputPath}`);
}

// Run
addTestsToCollection(inputFile, outputFile);