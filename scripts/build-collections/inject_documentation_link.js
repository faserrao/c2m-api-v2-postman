#!/usr/bin/env node
/**
 * Inject Redoc Documentation Link into Postman Collections
 *
 * This script adds a documentation link to the collection description
 * for easier discovery and navigation to the Redoc API documentation.
 *
 * Usage:
 *   node inject_documentation_link.js <collection.json> <docs-url>
 *
 * Example:
 *   node inject_documentation_link.js postman/generated/c2mapiv2-test-collection.json \
 *     https://click2mail.github.io/c2m-api-v2-postman-artifacts/
 */

const fs = require('fs');
const path = require('path');

// Get command-line arguments
const args = process.argv.slice(2);
if (args.length !== 2) {
  console.error('Usage: node inject_documentation_link.js <collection.json> <docs-url>');
  process.exit(1);
}

const [collectionPath, docsUrl] = args;

// Read collection
let collection;
try {
  const collectionContent = fs.readFileSync(collectionPath, 'utf8');
  collection = JSON.parse(collectionContent);
} catch (error) {
  console.error(`ERROR: Failed to read collection: ${error.message}`);
  process.exit(1);
}

// Validate collection structure
if (!collection.info || !collection.info.name) {
  console.error('ERROR: Invalid collection format - missing info.name');
  process.exit(1);
}

// Create documentation section
const documentationSection = `

---

## Documentation

Detailed API documentation can be found at the following location:

**${docsUrl}**

The link below provides the same documentation in Postman's native format for viewing within the Postman environment.

---
`;

// Add or update collection description
if (!collection.info.description) {
  // No description exists - add new one
  collection.info.description = documentationSection.trim();
} else {
  // Description exists - check if docs link already present
  const descriptionText = typeof collection.info.description === 'string'
    ? collection.info.description
    : collection.info.description.content || '';

  if (descriptionText.includes(docsUrl)) {
    console.log(`Documentation link already present in ${collection.info.name}`);
    process.exit(0);
  }

  // Prepend documentation section
  if (typeof collection.info.description === 'string') {
    collection.info.description = documentationSection + collection.info.description;
  } else {
    collection.info.description.content = documentationSection + (collection.info.description.content || '');
  }
}

// Write updated collection
try {
  fs.writeFileSync(collectionPath, JSON.stringify(collection, null, 2));
  console.log(`Documentation link injected into ${collection.info.name}`);
  console.log(`  URL: ${docsUrl}`);
} catch (error) {
  console.error(`ERROR: Failed to write collection: ${error.message}`);
  process.exit(1);
}
