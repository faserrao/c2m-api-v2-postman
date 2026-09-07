#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

// Parse command line arguments
const args = process.argv.slice(2);
const inputFile = args[0];
const outputFile = args[1] || inputFile;

if (!inputFile) {
  console.error('Usage: node add_auth_examples.js <input-collection.json> [output-collection.json]');
  process.exit(1);
}

/**
 * Load auth request body examples from the OpenAPI auth overlay.
 *
 * For each path in the overlay that has a POST with a requestBody, reads the
 * first example value and registers it under two keys so it matches both the
 * original Postman request name (from operation.summary) and the flattened
 * path name used in generated collections (e.g. "POST /auth/tokens/short").
 *
 * Endpoints with no requestBody (e.g. revoke) are skipped — no body injected.
 */
function loadAuthExamplesFromOverlay(overlayPath) {
  const content = fs.readFileSync(overlayPath, 'utf8');
  const overlay = yaml.load(content);
  const examples = {};

  for (const [pathKey, pathItem] of Object.entries(overlay.paths || {})) {
    const operation = pathItem.post;
    if (!operation || !operation.requestBody) continue;

    const jsonContent = operation.requestBody.content &&
                        operation.requestBody.content['application/json'];
    if (!jsonContent || !jsonContent.examples) continue;

    const firstExample = Object.values(jsonContent.examples)[0];
    if (!firstExample || !firstExample.value) continue;

    const exampleValue = firstExample.value;

    // Register under the operation summary (used as Postman item name)
    if (operation.summary) {
      examples[operation.summary] = exampleValue;
    }

    // Register under the flattened path name used in generated collections
    // ("{tokenId}" → ":tokenId" to match the Postman URL parameter convention)
    const flatPath = pathKey.replace(/\{(\w+)\}/g, ':$1');
    examples[`POST ${flatPath}`] = exampleValue;
  }

  console.log(`Loaded auth examples for: ${Object.keys(examples).join(', ')}`);
  return examples;
}

// Load auth examples from the overlay (single source of truth)
const overlayPath = path.resolve(__dirname, '../../openapi/overlays/auth.tokens.yaml');
const authExamples = loadAuthExamplesFromOverlay(overlayPath);

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