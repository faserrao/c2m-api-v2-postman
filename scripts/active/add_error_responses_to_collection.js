#!/usr/bin/env node
/**
 * add_error_responses_to_collection.js
 *
 * Replaces the saved responses of every job request in a Postman collection with the
 * examples the OpenAPI spec declares for that operation — the success (2xx) example and
 * every error example. The spec's examples are generated from the DD (@error_examples
 * block and standardResponse @hint values), so Postman shows exactly what Redoc shows
 * (D10, 2026-10-08). config/error-response-examples.yaml is retired.
 *
 * Saved responses let a Postman mock server return success or any declared error
 * (select one with the x-mock-response-code / x-mock-response-name request headers).
 *
 * Usage:
 *   node add_error_responses_to_collection.js <input_collection> <output_collection> [--spec <path>]
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { STATUS_CODES } = require('http');  // RFC 9110 reason phrases for the saved-response status line
const yaml = require('js-yaml');

const CONTENT_TYPE_JSON = 'application/json';  // L2: avoids raw string repetition
const HTTP_METHODS = ['get', 'post', 'put', 'patch', 'delete'];

function generateUUID() {
  return crypto.randomUUID ? crypto.randomUUID() : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

/**
 * The collection request's path in spec form: Postman `:param` segments become `{param}`.
 */
function specPathOf(request) {
  const segments = (request.url && request.url.path) || [];
  return '/' + segments.map(s => (s.startsWith(':') ? `{${s.slice(1)}}` : s)).join('/');
}

/**
 * Saved responses for one spec operation: one per example the spec declares, in status
 * order (lowest first, so a mock server returns the success example by default).
 */
function savedResponsesFor(operation) {
  const saved = [];
  const statuses = Object.keys(operation.responses || {}).sort();
  for (const status of statuses) {
    const response = operation.responses[status];
    const media = (response.content || {})[CONTENT_TYPE_JSON] || {};
    for (const example of Object.values(media.examples || {})) {
      saved.push({
        name: example.summary || response.description || `HTTP ${status}`,
        status: STATUS_CODES[status] || `HTTP ${status}`,
        code: parseInt(status, 10),
        _postman_previewlanguage: 'json',
        header: [{ key: 'Content-Type', value: CONTENT_TYPE_JSON }],
        body: JSON.stringify(example.value, null, 2)
      });
    }
  }
  return saved;
}

/**
 * Recursively replace the saved responses of job requests. Auth endpoints use the overlay's
 * AuthError format and keep only their success examples (unchanged behaviour).
 * Returns the number of saved responses written.
 */
function processItems(items, spec, unmatched) {
  let responseCount = 0;
  items.forEach(item => {
    if (item.item && Array.isArray(item.item)) {
      responseCount += processItems(item.item, spec, unmatched);
    }
    if (!item.request || item.item) return;

    const isAuthEndpoint = ((item.request.url && item.request.url.path) || []).some(p => p === 'auth');
    if (isAuthEndpoint) {
      item.response = (item.response || []).filter(resp => {
        const code = parseInt(resp.code || resp.status || 200);
        return code >= 200 && code < 300;
      });
      return;
    }

    const method = (item.request.method || '').toLowerCase();
    const pathKey = specPathOf(item.request);
    const operation = ((spec.paths || {})[pathKey] || {})[method];
    if (!operation || !HTTP_METHODS.includes(method)) {
      unmatched.push(`${method.toUpperCase()} ${pathKey}`);
      return;
    }

    // Every example shares the request's originalRequest, so Postman's body-match scores
    // are equal and the mock falls back to the lowest status code (the success example).
    const originalRequest = {
      method: item.request.method,
      header: item.request.header || [],
      body: item.request.body || null,
      url: item.request.url
    };
    item.response = savedResponsesFor(operation).map(saved => ({
      ...saved,
      id: generateUUID(),
      originalRequest
    }));
    responseCount += item.response.length;
  });
  return responseCount;
}

function main() {
  const args = process.argv.slice(2);
  const specIdx = args.indexOf('--spec');
  const specArg = specIdx !== -1 ? args[specIdx + 1] : null;
  const positional = args.filter((_, i) => i !== specIdx && i !== specIdx + 1);

  if (positional.length !== 2) {
    console.error('Usage: node add_error_responses_to_collection.js <input_collection> <output_collection> [--spec <path>]');
    process.exit(1);
  }
  const [inputFile, outputFile] = positional;

  // --spec overrides the default; Makefile passes $(C2MAPIV2_OPENAPI_SPEC).
  // Assumed layout: this script lives in scripts/active/; ../../ is the repo root.
  const openapiSpecPath = specArg || path.resolve(path.dirname(__filename), '../../openapi/c2mapiv2-openapi-spec-final.yaml');
  console.log(`Loading response examples from OpenAPI spec: ${openapiSpecPath}`);
  const spec = yaml.load(fs.readFileSync(openapiSpecPath, 'utf8'));

  console.log(`Reading collection from: ${inputFile}`);
  const collection = JSON.parse(fs.readFileSync(inputFile, 'utf8'));

  const unmatched = [];
  const responseCount = processItems(collection.item || [], spec, unmatched);

  // A job request with no matching spec operation would silently keep stale examples.
  if (unmatched.length > 0) {
    console.error(`❌ Requests with no matching spec operation: ${unmatched.join(', ')}`);
    process.exit(1);
  }
  // No-op guard (2026-10-05): a step that changes nothing must fail the build, not pass silently.
  if (responseCount === 0) {
    console.error('❌ No saved responses were written — no job requests matched the spec');
    process.exit(1);
  }

  console.log(`Writing collection to: ${outputFile}`);
  fs.writeFileSync(outputFile, JSON.stringify(collection, null, 2));
  console.log(`✅ Wrote ${responseCount} saved responses from the spec's examples`);
}

main();
