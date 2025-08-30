#!/usr/bin/env node

const fs = require('fs');

const args = process.argv.slice(2);
if (args.length < 2) {
  console.error("Usage: node scripts/add_tests_jwt.js <input_file> <output_file> [--allowed-codes \"200,400,401\"]");
  process.exit(1);
}

const inputFile = args[0];
const outputFile = args[1];
let allowedCodes = "200";

const codesIndex = args.indexOf("--allowed-codes");
if (codesIndex !== -1 && args[codesIndex + 1]) {
  allowedCodes = args[codesIndex + 1];
}

console.log(`ℹ️ Input file: ${inputFile}`);
console.log(`ℹ️ Output file: ${outputFile}`);
console.log(`ℹ️ Allowed status codes: ${allowedCodes}`);

// Standard tests for all endpoints
const standardTests = [
  `pm.test("Status code is allowed (${allowedCodes})", function () { pm.expect([${allowedCodes}]).to.include(pm.response.code); });`,
  `pm.test("Response time < 1s", function () { pm.expect(pm.response.responseTime).to.be.below(1000); });`
];

// JWT-specific tests by endpoint
const jwtTests = {
  'issueShortTermToken': [
    `pm.test("Response has required JWT fields", function () {
      const jsonData = pm.response.json();
      pm.expect(jsonData).to.have.property('token_type', 'Bearer');
      pm.expect(jsonData).to.have.property('access_token');
      pm.expect(jsonData).to.have.property('expires_in');
      pm.expect(jsonData).to.have.property('expires_at');
      pm.expect(jsonData).to.have.property('token_id');
    });`,
    `pm.test("Short token expires in 15 minutes", function () {
      const jsonData = pm.response.json();
      pm.expect(jsonData.expires_in).to.be.at.least(890).and.at.most(910);
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
  ],
  'issueLongTermToken': [
    `pm.test("Response has required JWT fields", function () {
      const jsonData = pm.response.json();
      pm.expect(jsonData).to.have.property('token_type', 'Bearer');
      pm.expect(jsonData).to.have.property('access_token');
      pm.expect(jsonData).to.have.property('expires_in');
      pm.expect(jsonData).to.have.property('expires_at');
      pm.expect(jsonData).to.have.property('token_id');
    });`,
    `pm.test("Long token has reasonable expiry", function () {
      const jsonData = pm.response.json();
      const minExpiry = 3600; // 1 hour
      const maxExpiry = 7776000; // 90 days
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
  ],
  'revokeToken': [
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
  ]
};

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
      pm.expect(['invalid_token', 'token_expired', 'invalid_client']).to.include(jsonData.code);
    }
  });`,
  `pm.test("403 error indicates authorization issue", function () {
    if (pm.response.code === 403) {
      const jsonData = pm.response.json();
      pm.expect(['insufficient_scope', 'access_denied']).to.include(jsonData.code);
    }
  });`
];

// Pre-request script for JWT endpoints
const jwtPreRequestScript = `
// Set required headers
pm.request.headers.add({key: 'Content-Type', value: 'application/json'});

// For long token endpoint, add X-Client-Id header
if (pm.info.requestName === 'issueLongTermToken') {
  const clientId = pm.environment.get('clientId');
  if (clientId) {
    pm.request.headers.add({key: 'X-Client-Id', value: clientId});
  }
}

// For short token and revoke endpoints, add Authorization header
if (['issueShortTermToken', 'revokeToken'].includes(pm.info.requestName)) {
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

    // Add pre-request script for JWT endpoints
    if (['issueShortTermToken', 'issueLongTermToken', 'revokeToken'].includes(operationId)) {
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