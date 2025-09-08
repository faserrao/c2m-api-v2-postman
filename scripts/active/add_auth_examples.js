#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Parse command line arguments
const args = process.argv.slice(2);
const inputFile = args[0];
const outputFile = args[1] || inputFile;

if (!inputFile) {
  console.error('Usage: node add_auth_examples.js <input-collection.json> [output-collection.json]');
  process.exit(1);
}

// Auth examples - supporting both original names and flattened names
const authExamples = {
  'Issue a short-term access token': {
    scopes: ["jobs:submit", "jobs:read", "templates:read"]
  },
  'POST /auth/tokens/short': {
    scopes: ["jobs:submit", "jobs:read", "templates:read"]
  },
  'Issue or rotate a long-term token': {
    grant_type: "client_credentials",
    client_id: "{{clientId}}",
    client_secret: "{{clientSecret}}",
    scopes: ["jobs:submit", "jobs:read", "jobs:update", "templates:read", "account:read"],
    ttl_seconds: 7776000
  },
  'POST /auth/tokens/long': {
    grant_type: "client_credentials",
    client_id: "{{clientId}}",
    client_secret: "{{clientSecret}}",
    scopes: ["jobs:submit", "jobs:read", "jobs:update", "templates:read", "account:read"],
    ttl_seconds: 7776000
  },
  'Revoke a token': {
    reason: "Compromised key",
    revoke_all_related: false
  },
  'POST /auth/tokens/:tokenId/revoke': {
    reason: "Compromised key",
    revoke_all_related: false
  }
};

// Read the collection
const collection = JSON.parse(fs.readFileSync(inputFile, 'utf8'));

// Function to find and update auth endpoints
function updateAuthEndpoints(items) {
  for (const item of items) {
    if (item.item) {
      // Recurse into folders
      updateAuthEndpoints(item.item);
    } else if (item.request) {
      // Check if this is an auth endpoint
      const requestName = item.name;
      if (authExamples[requestName]) {
        // Update the request body
        if (!item.request.body) {
          item.request.body = {};
        }
        item.request.body.mode = 'raw';
        item.request.body.raw = JSON.stringify(authExamples[requestName], null, 2);
        
        // Ensure JSON content type
        if (!item.request.header) {
          item.request.header = [];
        }
        const contentTypeHeader = item.request.header.find(h => h.key.toLowerCase() === 'content-type');
        if (!contentTypeHeader) {
          item.request.header.push({
            key: 'Content-Type',
            value: 'application/json'
          });
        }
        
        console.log(`✅ Updated request body for: ${requestName}`);
      }
    }
  }
}

// Update the collection
updateAuthEndpoints(collection.item || []);

// Write the updated collection
fs.writeFileSync(outputFile, JSON.stringify(collection, null, 2));
console.log(`✅ Collection saved to: ${outputFile}`);