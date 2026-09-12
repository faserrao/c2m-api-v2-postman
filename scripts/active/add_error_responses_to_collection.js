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

// Computed once per invocation — ensures example timestamps reflect the build date
const _NOW_ISO = new Date().toISOString();
const _EXPIRED_ISO = new Date(Date.now() - 3600000).toISOString();

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

// Error code metadata: maps error code to HTTP status and message template.
// errorType is intentionally omitted — derived dynamically via deriveErrorType().
const ERROR_CODE_METADATA = {
  'MISSING_REQUIRED_FIELD': {
    status: 400,
    name: 'Missing required field',
    message: 'Required field is missing from request body',
    details: '{"field": "documentId", "location": "requestBody"}'
  },
  'INVALID_ONEOF': {
    status: 400,
    name: 'Invalid oneOf selection',
    message: 'Request must match exactly one of the defined schemas',
    details: '{"field": "document", "issue": "matches multiple schemas or no schema"}'
  },
  'INVALID_JSON': {
    status: 400,
    name: 'Invalid JSON',
    message: 'Request body contains malformed JSON',
    details: '{"error": "Unexpected token at position 42", "line": 3}'
  },
  'MISSING_AUTH_HEADER': {
    status: 401,
    name: 'Missing authentication',
    message: 'Authorization header is missing or invalid',
    details: '{"expected": "Bearer <token>", "received": "none"}'
  },
  'INVALID_TOKEN': {
    status: 401,
    name: 'Invalid token',
    message: 'Authentication token is invalid or malformed',
    details: '{"reason": "invalid signature", "token": "<redacted>"}'
  },
  'EXPIRED_TOKEN': {
    status: 401,
    name: 'Expired token',
    message: 'Authentication token has expired',
    details: `{"expired": "${_EXPIRED_ISO}", "current": "${_NOW_ISO}"}`
  },
  'INSUFFICIENT_PERMISSIONS': {
    status: 403,
    name: 'Insufficient permissions',
    message: 'User does not have required permissions for this operation',
    details: '{"required": "jobs:write", "user": "read-only-user"}'
  },
  'ACCOUNT_SUSPENDED': {
    status: 403,
    name: 'Account suspended',
    message: 'User account has been suspended',
    details: `{"reason": "payment overdue", "contact": "${DEFAULT_SUPPORT_EMAIL}"}`
  },
  'JOB_NOT_FOUND': {
    status: 404,
    name: 'Job not found',
    message: 'The specified job does not exist',
    details: '{"resourceType": "job", "jobId": "JOB-12345"}'
  },
  'RESOURCE_NOT_FOUND': {
    status: 404,
    name: 'Resource not found',
    message: 'Requested resource does not exist',
    details: '{"resourceType": "document", "resourceId": "DOC-12345"}'
  },
  'INVALID_ENUM_VALUE': {
    status: 422,
    name: 'Invalid enum value',
    message: 'Field contains a value not allowed by the enumeration',
    details: '{"field": "mailClass", "provided": "express", "allowed": ["First", "Standard"]}'
  },
  'MUTUAL_EXCLUSION_VIOLATION': {
    status: 422,
    name: 'Mutually exclusive fields',
    message: 'Request contains mutually exclusive fields',
    details: '{"conflict": "documentId and documentUrl cannot both be specified"}'
  },
  'INVALID_FORMAT': {
    status: 422,
    name: 'Invalid field format',
    message: 'Field contains invalid format or value',
    details: '{"field": "postalCode", "provided": "1234", "expected": "5 or 9 digits"}'
  },
  'SERVER_ERROR': {
    status: 500,
    name: 'Internal server error',
    message: 'An unexpected error occurred while processing the request',
    details: `{"timestamp": "${_NOW_ISO}", "requestId": "req-abc123"}`
  },
  'DATABASE_ERROR': {
    status: 500,
    name: 'Database error',
    message: 'Database operation failed',
    details: '{"operation": "insert", "table": "jobs", "error": "connection timeout"}'
  },
  'EXTERNAL_SERVICE_ERROR': {
    status: 500,
    name: 'External service error',
    message: 'External service call failed',
    details: '{"service": "address-validation", "error": "timeout after 30s"}'
  },
  'RATE_LIMIT_EXCEEDED': {
    status: 429,
    name: 'Rate limit exceeded',
    message: 'Request rate limit exceeded — please slow down and retry',
    details: '{"limit": "100 requests/minute", "retryAfterSeconds": 60}'
  }
};

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

      // Remove existing error responses (bad placeholders from OpenAPI spec)
      // Keep only success responses (200-299) and auth responses (403 for /auth/*)
      const isAuthEndpoint = item.request.url &&
        (item.request.url.path || []).some(p => p.includes('auth'));

      item.response = item.response.filter(resp => {
        const code = parseInt(resp.code || resp.status || 200);
        return (code >= 200 && code < 300) || (isAuthEndpoint && code === 403);
      });

      // Build originalRequest from the parent item's request
      // Required by Postman mock server for x-mock-response-code header matching
      const originalRequest = {
        method: item.request.method,
        header: item.request.header || [],
        body: item.request.body || null,
        url: item.request.url
      };

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

  // Patch support email into ACCOUNT_SUSPENDED before building responses
  if (ERROR_CODE_METADATA.ACCOUNT_SUSPENDED) {
    ERROR_CODE_METADATA.ACCOUNT_SUSPENDED.details =
      ERROR_CODE_METADATA.ACCOUNT_SUSPENDED.details.replace('support@click2mail.com', supportEmail);
  }

  const [inputFile, outputFile] = positional;

  // Determine OpenAPI spec path (relative to script location)
  const scriptDir = path.dirname(__filename);
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
