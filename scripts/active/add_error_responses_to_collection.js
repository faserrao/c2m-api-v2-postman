#!/usr/bin/env node
/**
 * add_error_responses_to_collection.js
 *
 * Adds realistic error response examples to Postman collections.
 * These error responses enable mock servers to randomly return both success and error responses.
 *
 * Usage:
 *   node add_error_responses_to_collection.js <input_collection> <output_collection>
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const yaml = require('js-yaml');

// Single source of truth — override via --support-email CLI arg (passed by Makefile)
const DEFAULT_SUPPORT_EMAIL = 'support@click2mail.com';
const CONTENT_TYPE_JSON = 'application/json';  // L2: avoids raw string repetition

// Computed once per invocation — ensures example values reflect the build date
const _NOW_ISO = new Date().toISOString();
const _EXPIRED_ISO = new Date(Date.now() - 3600000).toISOString();
const _REQUEST_ID = `req-${crypto.randomBytes(4).toString('hex')}`;

// HTTP status text mapping (required by Postman mock server for x-mock-response-code matching).
// These are RFC 9110 reason phrases (short form), not prose descriptions.
// Parallel to _HTTP_STATUS_DESCRIPTIONS in ebnf_to_openapi_dynamic_v3.py (different format/consumer).
const HTTP_STATUS_TEXT = {
  400: 'Bad Request',
  401: 'Unauthorized',
  403: 'Forbidden',
  404: 'Not Found',
  422: 'Unprocessable Entity',
  429: 'Too Many Requests',
  500: 'Internal Server Error'
};

function generateUUID() {
  return crypto.randomUUID ? crypto.randomUUID() : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

// Error code metadata — loaded from config/error-response-examples.yaml in main().
// (D10 step 2 replaces this with the spec's examples, which come from the DD @error_examples block.)
let ERROR_CODE_METADATA = {};

/**
 * Load ERROR_CODE_METADATA from config/error-response-examples.yaml.
 * Returns a dict keyed by "<status>:<errorCode>" whose values are lists of examples,
 * substituting {timestamp}, {expired}, {requestId} and {supportEmail} placeholders.
 * Keyed by status AND code because the DD @http_error_map may list one code under
 * several statuses (e.g. INVALID_FORMAT under 400 and 422). Keying by code alone made
 * the later status overwrite the earlier one (N2, 2026-10-06).
 */
function loadErrorCodeMetadataFromYaml(yamlPath, supportEmail) {
  const content = fs.readFileSync(yamlPath, 'utf8');
  const raw = yaml.load(content);
  const metadata = {};
  for (const [httpStatus, examples] of Object.entries(raw)) {
    for (const exData of Object.values(examples)) {
      let details = String(exData.errorDetails || '{}');
      details = details
        .replace(/{timestamp}/g, _NOW_ISO)
        .replace(/{expired}/g, _EXPIRED_ISO)
        .replace(/{requestId}/g, _REQUEST_ID)
        .replace(/{supportEmail}/g, supportEmail || DEFAULT_SUPPORT_EMAIL);
      const key = `${parseInt(httpStatus, 10)}:${exData.errorCode}`;
      (metadata[key] = metadata[key] || []).push({
        status: parseInt(httpStatus, 10),
        name: exData.summary,
        message: exData.errorMessage,
        details
      });
    }
  }
  return metadata;
}

/**
 * Replace {<field>_enum} tokens in errorDetails strings with spec-derived JSON arrays.
 * Token format: {<schemaName>_enum} → JSON.stringify(spec.components.schemas[schemaName].enum).
 * Example: {mailClass_enum} → '["first_class","standard","non_profit"]'
 * Must run BEFORE the error responses are built: they copy entry.details (N1, 2026-10-06).
 * An unresolvable token is fatal — leaving it in place produces invalid JSON.
 */
function resolveEnumTokens(metadata, spec) {
  const schemas = (spec && spec.components && spec.components.schemas) || {};
  for (const entries of Object.values(metadata)) {
    for (const entry of entries) {
      if (typeof entry.details === 'string' && entry.details.includes('{')) {
        entry.details = entry.details.replace(/\{(\w+)_enum\}/g, (match, fieldName) => {
          const schema = schemas[fieldName];
          if (schema && Array.isArray(schema.enum) && schema.enum.length > 0) {
            return JSON.stringify(schema.enum);
          }
          console.error(`❌ Cannot resolve ${match}: no enum schema '${fieldName}' in the spec`);
          process.exit(1);
        });
      }
    }
  }
  return metadata;
}

/**
 * Read the errorType enum from the OpenAPI spec.
 * Returns the array of valid errorType values, or a safe default if not found.
 */
function loadErrorTypesFromSpec(spec) {
  const schema = spec && spec.components && spec.components.schemas && spec.components.schemas.errorType;
  if (schema && Array.isArray(schema.enum) && schema.enum.length > 0) {
    console.log(`Found ${schema.enum.length} errorType values in spec: ${schema.enum.join(', ')}`);
    return schema.enum;
  }
  console.error('❌ No errorType enum found in spec — cannot derive error types. Ensure the OpenAPI spec is built before running this script.');
  process.exit(1);
}

/**
 * Build ERROR_RESPONSES (keyed by HTTP status) from the spec's x-http-error-map, which the
 * translator emits from the DD @http_error_map block. One example per (status, errorCode)
 * pair, so a code mapped to several statuses gets an example under each (N2). errorType
 * comes from that status's map entry. Pairs with no YAML example get a minimal stub.
 */
function buildErrorResponses(spec) {
  const httpErrorMap = (spec.info && spec.info['x-http-error-map']) || {};
  if (Object.keys(httpErrorMap).length === 0) {
    console.error('❌ x-http-error-map not found in spec — cannot build error examples');
    process.exit(1);
  }
  const validErrorTypes = loadErrorTypesFromSpec(spec);

  // YAML examples filed under a (status, code) pair the DD does not map would never be used
  const mappedKeys = new Set();
  Object.entries(httpErrorMap).forEach(([status, entry]) =>
    (entry.errorCodes || []).forEach(code => mappedKeys.add(`${parseInt(status, 10)}:${code}`)));
  const unmapped = Object.keys(ERROR_CODE_METADATA).filter(k => !mappedKeys.has(k));
  if (unmapped.length > 0) {
    console.error(`❌ error-response-examples.yaml has (status:code) pairs not in the DD @http_error_map: ${unmapped.join(', ')}`);
    process.exit(1);
  }

  const errorResponsesByStatus = {};
  const stubs = [];
  Object.keys(httpErrorMap).sort().forEach(statusKey => {
    const status = parseInt(statusKey, 10);
    const { errorType, errorCodes = [] } = httpErrorMap[statusKey];
    if (!validErrorTypes.includes(errorType)) {
      console.error(`❌ x-http-error-map ${statusKey}: errorType '${errorType}' is not in the errorType enum`);
      process.exit(1);
    }
    errorCodes.forEach(errorCode => {
      let entries = ERROR_CODE_METADATA[`${status}:${errorCode}`];
      if (!entries) {
        const label = errorCode.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        entries = [{ status, name: label, message: label, details: '{}' }];
        stubs.push(`  ${status}: ${errorCode}`);
      }
      entries.forEach(metadata => {
        try {
          JSON.parse(metadata.details);
        } catch (e) {
          console.error(`❌ errorDetails for ${status} ${errorCode} is not valid JSON: ${metadata.details}`);
          process.exit(1);
        }
        // Generate tracking ID — 6 uppercase hex chars matches Python canonical format TRK-YYYYMMDD-XXXXXX
        const hexSuffix = Array.from({ length: 6 }, () => '0123456789ABCDEF'[Math.floor(Math.random() * 16)]).join('');
        const trackingId = `TRK-${new Date().toISOString().split('T')[0].replace(/-/g, '')}-${hexSuffix}`;
        (errorResponsesByStatus[statusKey] = errorResponsesByStatus[statusKey] || []).push({
          id: generateUUID(),
          name: metadata.name,
          status: HTTP_STATUS_TEXT[status] || `HTTP ${status}`,
          code: status,
          _postman_previewlanguage: 'json',
          header: [{ key: 'Content-Type', value: CONTENT_TYPE_JSON }],
          body: JSON.stringify({
            errorType: errorType,
            errorMessage: metadata.message,
            errorCode: errorCode,
            errorDetails: metadata.details,
            errorTrackingId: trackingId
          }, null, 2)
        });
      });
    });
  });

  if (stubs.length > 0) {
    console.log(`Auto-generated ${stubs.length} stub(s) for mapped (status, errorCode) pairs with no YAML example:`);
    stubs.forEach(line => console.log(line));
  } else {
    console.log('Every mapped (status, errorCode) pair has a hand-crafted example');
  }
  return errorResponsesByStatus;
}

// Global ERROR_RESPONSES object (will be populated from OpenAPI spec)
let ERROR_RESPONSES = {};

/**
 * Recursively process collection items to add error responses
 */
function processItems(items) {
  let responseCount = 0;

  items.forEach(item => {
    // If item has sub-items (folder), process recursively
    if (item.item && Array.isArray(item.item)) {
      responseCount += processItems(item.item);
    }

    // If item is a request with response array
    if (item.request && !item.item) {
      if (!item.response) {
        item.response = [];
      }

      // Auth endpoints use the AuthError schema (code/message/details) from the overlay,
      // not the job StandardResponse error format (errorType/errorCode/errorTrackingId).
      // Skip error injection for auth endpoints entirely to avoid polluting the mock
      // server with wrong-format examples that would be returned instead of the 201.
      const isAuthEndpoint = item.request.url &&
        (item.request.url.path || []).some(p => p === 'auth');

      if (isAuthEndpoint) {
        // Strip placeholder error responses but keep 2xx success examples
        item.response = item.response.filter(resp => {
          const code = parseInt(resp.code || resp.status || 200);
          return code >= 200 && code < 300;
        });
        return; // Do not inject job-format errors into auth endpoints
      }

      // Remove existing placeholder error responses — keep only 2xx success examples
      item.response = item.response.filter(resp => {
        const code = parseInt(resp.code || resp.status || 200);
        return code >= 200 && code < 300;
      });

      // Build originalRequest from the parent item's request.
      // Required by Postman mock server for x-mock-response-code header matching.
      // ALL examples (2xx and errors) must share the same originalRequest body so that
      // Postman's body-matching score is equal across all examples and it falls back to
      // lowest-status-code selection (returning 200/201 by default).
      const originalRequest = {
        method: item.request.method,
        header: item.request.header || [],
        body: item.request.body || null,
        url: item.request.url
      };

      // Sync existing 2xx examples to the same originalRequest so body-match scores
      // are equal and Postman selects by status code (lowest wins = 200/201).
      item.response.forEach(resp => {
        resp.originalRequest = originalRequest;
      });

      // Add every error response for every status in the DD error map
      Object.keys(ERROR_RESPONSES).forEach(status => {
        ERROR_RESPONSES[status].forEach(errorResponse => {
          item.response.push({
            ...errorResponse,
            id: generateUUID(),
            originalRequest: originalRequest
          });
          responseCount++;
        });
      });
    }
  });

  return responseCount;
}

/**
 * Main function
 */
function main() {
  const args = process.argv.slice(2);

  const supportEmailIdx = args.indexOf('--support-email');
  const supportEmail = supportEmailIdx !== -1 ? args[supportEmailIdx + 1] : DEFAULT_SUPPORT_EMAIL;
  const specIdx = args.indexOf('--spec');
  const specArg = specIdx !== -1 ? args[specIdx + 1] : null;
  const positional = args.filter((_, i) =>
    i !== supportEmailIdx && i !== supportEmailIdx + 1 &&
    i !== specIdx && i !== specIdx + 1
  );

  if (positional.length !== 2) {
    console.error('Usage: node add_error_responses_to_collection.js <input_collection> <output_collection> [--support-email <email>] [--spec <path>]');
    process.exit(1);
  }

  // Assumed layout: this script lives in scripts/active/; ../../ is the repo root.
  // If the script is ever moved, update the defaults below accordingly.
  const scriptDir = path.dirname(__filename);

  // Load error code metadata — {supportEmail} placeholder is resolved at load time (L8)
  const errYamlPath = path.resolve(scriptDir, '../../config/error-response-examples.yaml');
  ERROR_CODE_METADATA = loadErrorCodeMetadataFromYaml(errYamlPath, supportEmail);

  const [inputFile, outputFile] = positional;

  // --spec overrides the default; Makefile passes $(C2MAPIV2_OPENAPI_SPEC).
  // K6: filename matches C2MAPIV2_OPENAPI_SPEC in the Makefile (same coupling as add_auth_examples.js:69).
  const openapiSpecPath = specArg || path.resolve(scriptDir, '../../openapi/c2mapiv2-openapi-spec-final.yaml');

  // Resolve {field_enum} tokens first, then build the responses from the resolved metadata (N1)
  console.log(`Loading error map from OpenAPI spec: ${openapiSpecPath}`);
  const spec = yaml.load(fs.readFileSync(openapiSpecPath, 'utf8'));
  ERROR_CODE_METADATA = resolveEnumTokens(ERROR_CODE_METADATA, spec);
  ERROR_RESPONSES = buildErrorResponses(spec);

  // Read input collection
  console.log(`Reading collection from: ${inputFile}`);
  const collection = JSON.parse(fs.readFileSync(inputFile, 'utf8'));

  // Add error responses
  console.log('Adding error response examples...');
  const responseCount = processItems(collection.item || []);
  // No-op guard (2026-10-05): a step that changes nothing must fail the build, not pass silently.
  if (responseCount === 0) {
    console.error('❌ No error response examples were added — no matching requests found');
    process.exit(1);
  }

  // Write output collection
  console.log(`Writing collection to: ${outputFile}`);
  fs.writeFileSync(outputFile, JSON.stringify(collection, null, 2));

  console.log(`✅ Added ${responseCount} error response examples`);
}

main();
