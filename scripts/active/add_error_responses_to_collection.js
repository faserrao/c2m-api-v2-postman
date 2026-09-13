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

// Computed once per invocation — ensures example values reflect the build date
const _NOW_ISO = new Date().toISOString();
const _EXPIRED_ISO = new Date(Date.now() - 3600000).toISOString();
const _REQUEST_ID = `req-${crypto.randomBytes(4).toString('hex')}`;

// HTTP status text mapping (required by Postman mock server for x-mock-response-code matching)
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
// That file is the single source of truth shared with add_response_examples.py.
let ERROR_CODE_METADATA = {};

/**
 * Load ERROR_CODE_METADATA from config/error-response-examples.yaml.
 * Converts the YAML structure (keyed by HTTP status then example name) into a flat
 * dict keyed by errorCode, substituting {timestamp} and {expired} placeholders.
 * When the same errorCode appears under multiple HTTP statuses the higher status wins
 * (e.g. INVALID_FORMAT appears at 400 and 422 — the 422 entry is used for the JS dict).
 */
function loadErrorCodeMetadataFromYaml(yamlPath) {
  const content = fs.readFileSync(yamlPath, 'utf8');
  const raw = yaml.load(content);
  const metadata = {};
  for (const [httpStatus, examples] of Object.entries(raw)) {
    for (const exData of Object.values(examples)) {
      let details = String(exData.errorDetails || '{}');
      details = details
        .replace(/{timestamp}/g, _NOW_ISO)
        .replace(/{expired}/g, _EXPIRED_ISO)
        .replace(/{requestId}/g, _REQUEST_ID);
      metadata[exData.errorCode] = {
        status: parseInt(httpStatus, 10),
        name: exData.summary,
        message: exData.errorMessage,
        details
      };
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
  console.warn('⚠️  No errorType enum found in spec, using defaults');
  return ['ValidationError', 'AuthenticationError', 'AuthorizationError', 'ResourceNotFoundError', 'ServerError'];
}

/**
 * Derive the errorType for an error code using prefix/suffix convention.
 * Validated against validErrorTypes read from the spec's errorType enum.
 *
 * Convention (applied in priority order):
 *   _NOT_FOUND suffix      → ResourceNotFoundError
 *   AUTH / TOKEN / EXPIRED → AuthenticationError
 *   INSUFFICIENT_ / ACCOUNT_ prefix → AuthorizationError
 *   RATE_LIMIT_*           → RateLimitError
 *   _ERROR suffix          → ServerError
 *   (default)              → ValidationError
 */
function deriveErrorType(errorCode, validErrorTypes) {
  const pick = (name) => validErrorTypes.find(t => t === name) || validErrorTypes[0];

  if (errorCode.endsWith('_NOT_FOUND')) return pick('ResourceNotFoundError');
  if (errorCode === 'MISSING_AUTH_HEADER' || errorCode === 'INVALID_TOKEN' || errorCode === 'EXPIRED_TOKEN') return pick('AuthenticationError');
  if (errorCode.startsWith('INSUFFICIENT_') || errorCode.startsWith('ACCOUNT_')) return pick('AuthorizationError');
  if (errorCode.startsWith('RATE_LIMIT_') || errorCode === 'RATE_LIMIT_EXCEEDED') return pick('RateLimitError');
  if (errorCode.endsWith('_ERROR')) return pick('ServerError');
  return pick('ValidationError');
}

/**
 * Load error codes from OpenAPI spec and generate ERROR_RESPONSES object
 */
function loadErrorResponsesFromSpec(openapiSpecPath) {
  console.log(`Loading error codes from OpenAPI spec: ${openapiSpecPath}`);

  // Read and parse OpenAPI spec
  const specContent = fs.readFileSync(openapiSpecPath, 'utf8');
  const spec = yaml.load(specContent);

  // Extract error types from spec (used to validate derived values)
  const validErrorTypes = loadErrorTypesFromSpec(spec);

  // Extract error codes from errorCode enum in components/schemas
  let errorCodes = [];
  if (spec.components && spec.components.schemas && spec.components.schemas.errorCode) {
    errorCodes = spec.components.schemas.errorCode.enum || [];
  }

  if (errorCodes.length === 0) {
    console.warn('⚠️  No error codes found in OpenAPI spec, using hardcoded metadata');
    errorCodes = Object.keys(ERROR_CODE_METADATA);
  }

  console.log(`Found ${errorCodes.length} error codes in OpenAPI spec`);

  // Build reverse map: errorCode → HTTP status, from x-http-error-map in the spec.
  // Used to auto-stub any code not in ERROR_CODE_METADATA so nothing is silently dropped.
  const httpErrorMap = (spec.info && spec.info['x-http-error-map']) || {};
  const codeToStatus = {};
  Object.entries(httpErrorMap).forEach(([status, entry]) => {
    (entry.errorCodes || []).forEach(code => { codeToStatus[code] = parseInt(status, 10); });
  });

  // Group error codes by HTTP status
  const errorResponsesByStatus = {};
  const stubs = [];

  errorCodes.forEach(errorCode => {
    let metadata = ERROR_CODE_METADATA[errorCode];
    if (!metadata) {
      const status = codeToStatus[errorCode];
      if (!status) {
        console.warn(`⚠️  No metadata and no x-http-error-map entry for ${errorCode}, skipping`);
        return;
      }
      const label = errorCode.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      metadata = { status, name: label, message: label, details: '{}' };
      stubs.push(`  ${status}: ${errorCode}`);
    }

    const statusCode = metadata.status.toString();
    if (!errorResponsesByStatus[statusCode]) {
      errorResponsesByStatus[statusCode] = [];
    }

    // Generate tracking ID
    const trackingId = `TRK-${new Date().toISOString().split('T')[0].replace(/-/g, '')}-${generateUUID().split('-')[0].toUpperCase()}`;

    // Derive errorType from the error code using spec-validated prefix convention
    const errorType = deriveErrorType(errorCode, validErrorTypes);

    // Create error response object
    errorResponsesByStatus[statusCode].push({
      id: generateUUID(),
      name: metadata.name,
      status: HTTP_STATUS_TEXT[metadata.status] || `HTTP ${metadata.status}`,
      code: metadata.status,
      _postman_previewlanguage: 'json',
      header: [{ key: 'Content-Type', value: 'application/json' }],
      body: JSON.stringify({
        errorType: errorType,
        errorMessage: metadata.message,
        errorCode: errorCode,
        errorDetails: metadata.details,
        errorTrackingId: trackingId
      }, null, 2)
    });
  });

  if (stubs.length > 0) {
    console.log(`Auto-generated ${stubs.length} stub(s) for errorCodes not in ERROR_CODE_METADATA:`);
    stubs.forEach(s => console.log(s));
  } else {
    console.log('All EBNF errorCode values have hand-crafted metadata');
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

      // Add all error responses (400, 401, 403, 404, 422, 500)
      Object.keys(ERROR_RESPONSES).forEach(errorCode => {
        ERROR_RESPONSES[errorCode].forEach(errorResponse => {
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
  const positional = args.filter((_, i) => i !== supportEmailIdx && i !== supportEmailIdx + 1);

  if (positional.length !== 2) {
    console.error('Usage: node add_error_responses_to_collection.js <input_collection> <output_collection> [--support-email <email>]');
    process.exit(1);
  }

  const scriptDir = path.dirname(__filename);

  // Load error code metadata from YAML (single source of truth with add_response_examples.py)
  const errYamlPath = path.resolve(scriptDir, '../../config/error-response-examples.yaml');
  ERROR_CODE_METADATA = loadErrorCodeMetadataFromYaml(errYamlPath);

  // Patch support email into ACCOUNT_SUSPENDED before building responses
  if (ERROR_CODE_METADATA.ACCOUNT_SUSPENDED) {
    ERROR_CODE_METADATA.ACCOUNT_SUSPENDED.details =
      ERROR_CODE_METADATA.ACCOUNT_SUSPENDED.details.replace('support@click2mail.com', supportEmail);
  }

  const [inputFile, outputFile] = positional;

  // Determine OpenAPI spec path (relative to script location)
  const openapiSpecPath = path.resolve(scriptDir, '../../openapi/c2mapiv2-openapi-spec-final.yaml');

  // Load error responses from OpenAPI spec
  ERROR_RESPONSES = loadErrorResponsesFromSpec(openapiSpecPath);

  // Read input collection
  console.log(`Reading collection from: ${inputFile}`);
  const collection = JSON.parse(fs.readFileSync(inputFile, 'utf8'));

  // Add error responses
  console.log('Adding error response examples...');
  const responseCount = processItems(collection.item || []);

  // Write output collection
  console.log(`Writing collection to: ${outputFile}`);
  fs.writeFileSync(outputFile, JSON.stringify(collection, null, 2));

  console.log(`✅ Added ${responseCount} error response examples`);
}

main();
