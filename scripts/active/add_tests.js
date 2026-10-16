#!/usr/bin/env node

// Adds Newman tests to every request: the response status must be one the request's own
// operation declares in the spec (D7, 2026-10-16 — was one global list for every request),
// plus an informational response-time line.

const fs = require('fs');
const { loadDeclaredStatuses, statusesForRequest, statusTest } = require('./declared_statuses');

const args = process.argv.slice(2);
const specIndex = args.indexOf("--spec");
const specPath = specIndex !== -1 ? args[specIndex + 1] : null;
if (args.length < 2 || !specPath) {
  console.error("Usage: node scripts/active/add_tests.js <input_file> <output_file> --spec <openapi spec>");
  process.exit(1);
}
if (args.includes("--allowed-codes")) {
  console.error("❌ --allowed-codes is retired (D7): each request's statuses now come from its operation in --spec");
  process.exit(1);
}

const inputFile = args[0];
const outputFile = args[1];

let declared;
try {
  declared = loadDeclaredStatuses(specPath);
} catch (err) {
  console.error(`❌ Cannot read declared statuses from ${specPath}: ${err.message}`);
  process.exit(1);
}

console.log(`ℹ️ Input file: ${inputFile}`);
console.log(`ℹ️ Output file: ${outputFile}`);
console.log(`ℹ️ Statuses per operation from: ${specPath}`);

const responseTimeTest = `pm.test("Response time check (informational)", function () { const rt = pm.response.responseTime; console.log(\`⏱️  Response time: \${rt}ms \${rt > 1000 ? '(>1s - SLOW)' : '(OK)'}\`); });`;

// Status assertions this script (or its pre-D7 version) writes; replaced on every run.
const isStatusAssertion = line => typeof line === 'string' && (
  line.includes('Status code is allowed') ||
  line.includes('Status code is one this operation declares') ||
  line.includes('Status code is 200'));

let requestCount = 0;

function addTestsToItem(item) {
  if (item.request) {
    requestCount++;
    let codes;
    try {
      codes = statusesForRequest(item.request, declared);
    } catch (err) {
      console.error(`❌ ${item.name}: ${err.message}`);
      process.exit(1);
    }
    if (!item.event) item.event = [];

    let testEvent = item.event.find(e => e.listen === 'test');
    if (!testEvent) {
      testEvent = { listen: 'test', script: { type: 'text/javascript', exec: [] } };
      item.event.push(testEvent);
    }

    // Replace earlier status assertions and old hard response-time assertions
    testEvent.script.exec = testEvent.script.exec.filter(line =>
      !isStatusAssertion(line) &&
      !line.includes('Response time < 1s') &&
      !line.includes('pm.response.responseTime).to.be.below(1000)')
    );
    testEvent.script.exec.push(statusTest(codes));
    if (!testEvent.script.exec.includes(responseTimeTest)) {
      testEvent.script.exec.push(responseTimeTest);
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

  if (collection.item) {
    collection.item.forEach(item => addTestsToItem(item));
  }
  // No-op guard (2026-10-05): a step that changes nothing must fail the build, not pass silently.
  if (requestCount === 0) {
    console.error('❌ No requests found — no tests were added');
    process.exit(1);
  }

  fs.writeFileSync(outputPath, JSON.stringify(collection, null, 2));
  console.log(`✅ Tests added. Output saved to ${outputPath}`);
}

// Run
addTestsToCollection(inputFile, outputFile);
