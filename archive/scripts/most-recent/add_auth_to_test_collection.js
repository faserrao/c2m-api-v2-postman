#!/usr/bin/env node

/**
 * Add authentication pre-request script to test collection
 * This script provides a more reliable way to add auth scripts that works in CI
 * while maintaining the flexibility to use different auth providers
 */

const fs = require('fs');
const path = require('path');

// Parse command line arguments
const args = process.argv.slice(2);
const collectionFile = args[0];
const outputFile = args[1] || collectionFile;

if (!collectionFile) {
  console.error('Usage: node add_auth_to_test_collection.js <collection.json> [output.json]');
  process.exit(1);
}

// Configuration
const SECURITY_SCRIPTS_DIR = '../c2m-api-v2-security/postman/scripts';
const LOCAL_SCRIPTS_DIR = 'postman/scripts';
const SECURITY_SCRIPT = 'jwt-auth-provider.js';
const LOCAL_SCRIPT = 'jwt-pre-request.js';

try {
  // Read the collection
  const collection = JSON.parse(fs.readFileSync(collectionFile, 'utf8'));
  
  // Determine which script to use
  let scriptPath;
  let scriptSource;
  
  // Check for security repo script first (for flexibility)
  const securityScriptPath = path.join(SECURITY_SCRIPTS_DIR, SECURITY_SCRIPT);
  if (fs.existsSync(securityScriptPath)) {
    scriptPath = securityScriptPath;
    scriptSource = 'security repo';
    console.log('📋 Using auth provider script from security repo...');
  } else {
    // Fall back to local script
    scriptPath = path.join(LOCAL_SCRIPTS_DIR, LOCAL_SCRIPT);
    if (!fs.existsSync(scriptPath)) {
      console.error('❌ No auth provider script found in either location');
      console.error('   Checked:', securityScriptPath);
      console.error('   Checked:', scriptPath);
      process.exit(1);
    }
    scriptSource = 'local repo';
    console.log('📋 Using auth provider script from local repo...');
  }
  
  // Read the selected script
  const scriptContent = fs.readFileSync(scriptPath, 'utf8');
  console.log(`✅ Loaded auth script from ${scriptSource}: ${path.basename(scriptPath)}`);
  
  // Split script into lines for the exec array
  const scriptLines = scriptContent.split('\n');
  
  // Add event array if it doesn't exist
  if (!collection.event) {
    collection.event = [];
  }
  
  // Remove any existing pre-request scripts
  collection.event = collection.event.filter(e => e.listen !== 'prerequest');
  
  // Add the new pre-request script
  collection.event.push({
    listen: 'prerequest',
    script: {
      type: 'text/javascript',
      exec: scriptLines
    }
  });
  
  // Write the updated collection
  fs.writeFileSync(outputFile, JSON.stringify(collection, null, 2));
  console.log(`✅ Auth provider script added to test collection`);
  console.log(`✅ Collection written to ${outputFile}`);
  
} catch (error) {
  console.error('❌ Error adding auth script:', error.message);
  process.exit(1);
}