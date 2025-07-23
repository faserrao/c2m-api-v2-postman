#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const testsToAdd = [
  `pm.test("Status code is 200", function () { pm.response.to.have.status(200); });`,
  `pm.test("Response time < 1s", function () { pm.expect(pm.response.responseTime).to.be.below(1000); });`
];

function addTestsToItem(item) {
  if (item.request) {
    if (!item.event) item.event = [];

    let testEvent = item.event.find(e => e.listen === 'test');
    if (!testEvent) {
      testEvent = { listen: 'test', script: { type: 'text/javascript', exec: [] } };
      item.event.push(testEvent);
    }

    // Add missing tests
    testsToAdd.forEach(test => {
      if (!testEvent.script.exec.includes(test)) {
        testEvent.script.exec.push(test);
      }
    });
  }

  // Recurse for nested folders
  if (item.item) {
    item.item.forEach(subItem => addTestsToItem(subItem));
  }
}

function addTestsToCollection(filePath) {
  const rawData = fs.readFileSync(filePath, 'utf-8');
  const collection = JSON.parse(rawData);

  if (collection.item) {
    collection.item.forEach(item => addTestsToItem(item));
  }

  const outputPath = filePath.replace(/\.json$/, '.with.tests.json');
  fs.writeFileSync(outputPath, JSON.stringify(collection, null, 2));
  console.log(`✅ Tests added. Output saved to ${outputPath}`);
}

// Run
if (process.argv.length < 3) {
  console.error("Usage: node scripts/add_tests.js <collection_file>");
  process.exit(1);
}
addTestsToCollection(process.argv[2]);
