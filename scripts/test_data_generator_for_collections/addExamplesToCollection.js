#!/usr/bin/env node

/**
 * Adds random test data to "request.body.raw" fields of a Postman Collection.
 * - Replaces placeholders (<string>, <number>, <integer>, <boolean>) with random values.
 * - With --force, inserts default template JSON into empty/missing raw bodies.
 * - Handles both valid JSON and non-JSON raw bodies.
 *
 * Usage:
 *   node addRandomDataToRaw.js --input input.json --output output.json [--error-rate 20] [--preview] [--force]
 */

const fs = require('fs');
const path = require('path');
const { faker } = require('@faker-js/faker');

// --- Parse CLI args ---
function parseArgs() {
  const args = process.argv.slice(2);
  const argMap = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].substring(2);
      const val = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
      argMap[key] = val;
    }
  }
  if (!argMap.input) {
    console.error('Usage: node addRandomDataToRaw.js --input <file> --output <file> [--error-rate <0-100>] [--preview] [--force]');
    process.exit(1);
  }
  argMap.errorRate = parseInt(argMap['error-rate'] || '0', 10);
  argMap.force = !!argMap.force;
  return argMap;
}

// --- Random Value Generators ---
function typeBasedRandomValue(typeHint) {
  switch (typeHint) {
    case '<number>': return parseFloat((Math.random() * 1000).toFixed(2));
    case '<integer>': return Math.floor(Math.random() * 1000);
    case '<boolean>': return Math.random() > 0.5;
    case '<string>':
    default: return faker.word.sample();
  }
}

function randomValue(key, typeHint = '<string>') {
  if (typeHint !== '<string>') return typeBasedRandomValue(typeHint);
  const k = key.toLowerCase();
  if (k.includes('first') || k.includes('name')) return faker.person.firstName();
  if (k.includes('last')) return faker.person.lastName();
  if (k.includes('email')) return faker.internet.email();
  if (k.includes('phone')) return faker.phone.number();
  if (k.includes('address')) return faker.location.streetAddress();
  if (k.includes('city')) return faker.location.city();
  if (k.includes('state')) return faker.location.state();
  if (k.includes('zip') || k.includes('postal')) return faker.location.zipCode();
  if (k.includes('country')) return faker.location.country();
  if (k.includes('invoice')) return faker.finance.accountNumber();
  if (k.includes('amount')) return faker.finance.amount();
  if (k.includes('card')) return faker.finance.creditCardNumber();
  if (k.includes('cvv')) return faker.finance.creditCardCVV();
  if (k.includes('month')) return faker.number.int({ min: 1, max: 12 }).toString();
  if (k.includes('year')) return (new Date().getFullYear() + 1).toString();
  return faker.word.sample();
}

function erroneousValue() {
  const pool = ['!!!@@@###', '', '<script>alert(1)</script>', null, undefined, '🚫INVALID🚫'];
  return pool[Math.floor(Math.random() * pool.length)];
}

// --- JSON-aware Replacement ---
function replaceValues(obj, errorRate) {
  if (Array.isArray(obj)) {
    obj.forEach((item) => replaceValues(item, errorRate));
  } else if (typeof obj === 'object' && obj !== null) {
    Object.keys(obj).forEach((key) => {
      if (typeof obj[key] === 'string' && obj[key].startsWith('<') && obj[key].endsWith('>')) {
        const injectError = Math.random() < errorRate / 100;
        const typeHint = obj[key];
        obj[key] = injectError ? erroneousValue() : randomValue(key, typeHint);
      } else if (typeof obj[key] === 'object') {
        replaceValues(obj[key], errorRate);
      }
    });
  }
}

// --- Fallback Regex Replacement for Non-JSON ---
function replacePlaceholdersInText(text, errorRate) {
  const replacers = {
    '<string>': () => (Math.random() < errorRate / 100 ? erroneousValue() : faker.word.sample()),
    '<number>': () => (Math.random() < errorRate / 100 ? erroneousValue() : (Math.random() * 1000).toFixed(2)),
    '<integer>': () => (Math.random() < errorRate / 100 ? erroneousValue() : Math.floor(Math.random() * 1000)),
    '<boolean>': () => (Math.random() < errorRate / 100 ? erroneousValue() : (Math.random() > 0.5)),
  };
  return text.replace(/<string>|<number>|<integer>|<boolean>/g, (match) => replacers[match]());
}

function fillRaw(rawStr, errorRate) {
  try {
    const jsonObj = JSON.parse(rawStr);
    replaceValues(jsonObj, errorRate);
    return JSON.stringify(jsonObj, null, 2);
  } catch {
    // Fallback for non-JSON raw strings
    return replacePlaceholdersInText(rawStr, errorRate);
  }
}

// --- Traverse Collection ---
function processCollection(item, errorRate, previewMode, forceMode) {
  let previewData = { before: null, after: null, captured: false };

  function processItem(it) {
    if (Array.isArray(it)) {
      it.forEach((sub) => processItem(sub));
    } else if (it && typeof it === 'object') {
      if (it.request && it.request.body) {
        if (!it.request.body.raw && forceMode) {
          // Insert default JSON template if raw is empty/missing
          it.request.body.raw = JSON.stringify({ example: "<string>" }, null, 2);
        }

        if (it.request.body.raw) {
          const originalRaw = it.request.body.raw;
          const newRaw = fillRaw(originalRaw, errorRate);
          it.request.body.raw = newRaw;

          if (previewMode && !previewData.captured) {
            previewData.before = originalRaw;
            previewData.after = newRaw;
            previewData.captured = true;
          }
        }
      }

      if (it.response) {
        it.response.forEach((resp) => {
          if (resp.body) resp.body = fillRaw(resp.body, errorRate);
        });
      }

      if (it.item) processItem(it.item);
    }
  }

  processItem(item);
  return previewData;
}

// --- Main ---
(function main() {
  const { input, output, errorRate, preview, force } = parseArgs();
  const collection = JSON.parse(fs.readFileSync(path.resolve(input), 'utf-8'));
  const previewData = processCollection(collection.item, errorRate, preview, force);

  if (preview) {
    console.log('--- PREVIEW MODE ---');
    console.log('\n--- BEFORE ---\n', previewData.before);
    console.log('\n--- AFTER ---\n', previewData.after);
    console.log('\n(No files were written.)');
  } else {
    fs.writeFileSync(path.resolve(output), JSON.stringify(collection, null, 2));
    console.log(`✅ Random data added. Output saved to ${output}`);
  }
})();
