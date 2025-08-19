#!/usr/bin/env node

const fs = require('fs');

const args = process.argv.slice(2);
if (args.length < 2) {
  console.error("Usage: node scripts/add_tests.js <input_file> <output_file> [--allowed-codes \"200,400,401\"]");
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

const testsToAdd = [
  `pm.test("Status code is allowed (${allowedCodes})", function () { pm.expect([${allowedCodes}]).to.include(pm.response.code); });`,
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

    // Remove old "Status code is 200" tests
    testEvent.script.exec = testEvent.script.exec.filter(line => !line.includes('Status code is 200'));

    // Add new tests
    testsToAdd.forEach(test => {
      if (!testEvent.script.exec.includes(test)) {
        testEvent.script.exec.push(test);
      }
    });
  }

  // Recursively handle sub-items
  if (item.item) {
    item.item.forEach(subItem => addTestsToItem(subItem));
  }
}

function addTestsToCollection(inputPath, outputPath) {
  const rawData = fs.readFileSync(inputPath, 'utf-8');
  const collection = JSON.parse(rawData);

  if (collection.item) {
    collection.item.forEach(item => addTestsToItem(item));
  }

  fs.writeFileSync(outputPath, JSON.stringify(collection, null, 2));
  console.log(`✅ Tests added. Output saved to ${outputPath}`);
}

// Run
addTestsToCollection(inputFile, outputFile);
