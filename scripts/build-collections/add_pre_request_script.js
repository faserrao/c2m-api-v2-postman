#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Parse command line arguments
const args = process.argv.slice(2);
const collectionFile = args[0];
const scriptFile = args[1];
const outputFile = args[2] || collectionFile;

if (!collectionFile || !scriptFile) {
  console.error('Usage: node add_pre_request_script.js <collection.json> <pre-request-script.js> [output.json]');
  process.exit(1);
}

try {
  // Read the collection
  const collection = JSON.parse(fs.readFileSync(collectionFile, 'utf8'));
  
  // Read the pre-request script
  const scriptContent = fs.readFileSync(scriptFile, 'utf8');
  
  // Split script into lines for the exec array
  const scriptLines = scriptContent.split('\n');
  
  // Add event array if it doesn't exist
  if (!collection.event) {
    collection.event = [];
  }
  
  // Check if pre-request already exists
  const preRequestIndex = collection.event.findIndex(e => e.listen === 'prerequest');
  
  const preRequestEvent = {
    listen: 'prerequest',
    script: {
      type: 'text/javascript',
      exec: scriptLines
    }
  };
  
  if (preRequestIndex >= 0) {
    // Update existing pre-request script
    collection.event[preRequestIndex] = preRequestEvent;
    console.log('✅ Updated existing pre-request script');
  } else {
    // Add new pre-request script
    collection.event.push(preRequestEvent);
    console.log('✅ Added pre-request script to collection');
  }
  
  // Write the updated collection
  fs.writeFileSync(outputFile, JSON.stringify(collection, null, 2));
  console.log(`✅ Collection written to ${outputFile}`);
  
} catch (error) {
  console.error('❌ Error:', error.message);
  process.exit(1);
}