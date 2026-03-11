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

// HTTP status text mapping (required by Postman mock server for x-mock-response-code matching)
const HTTP_STATUS_TEXT = {
  400: 'Bad Request',
  401: 'Unauthorized',
  403: 'Forbidden',
  404: 'Not Found',
  422: 'Unprocessable Entity',
  500: 'Internal Server Error'
};

function generateUUID() {
  return crypto.randomUUID ? crypto.randomUUID() : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

// Error code metadata: maps error code to HTTP status, error type, and message template
const ERROR_CODE_METADATA = {
  'MISSING_REQUIRED_FIELD': {
    status: 400,
    errorType: 'ValidationError',
    name: 'Missing required field',
    message: 'Required field is missing from request body',
    details: '{"field": "documentId", "location": "requestBody"}'
  },
  'INVALID_ONEOF': {
    status: 400,
    errorType: 'ValidationError',
    name: 'Invalid oneOf selection',
    message: 'Request must match exactly one of the defined schemas',
    details: '{"field": "document", "issue": "matches multiple schemas or no schema"}'
  },
  'INVALID_JSON': {
    status: 400,
    errorType: 'ValidationError',
    name: 'Invalid JSON',
    message: 'Request body contains malformed JSON',
    details: '{"error": "Unexpected token at position 42", "line": 3}'
  },
  'MISSING_AUTH_HEADER': {
    status: 401,
    errorType: 'AuthenticationError',
    name: 'Missing authentication',
    message: 'Authorization header is missing or invalid',
    details: '{"expected": "Bearer <token>", "received": "none"}'
  },
  'INVALID_TOKEN': {
    status: 401,
    errorType: 'AuthenticationError',
    name: 'Invalid token',
    message: 'Authentication token is invalid or malformed',
    details: '{"reason": "invalid signature", "token": "<redacted>"}'
  },
  'EXPIRED_TOKEN': {
    status: 401,
    errorType: 'AuthenticationError',
    name: 'Expired token',
    message: 'Authentication token has expired',
    details: '{"expired": "2026-03-10T15:30:00Z", "current": "2026-03-11T10:00:00Z"}'
  },
  'INSUFFICIENT_PERMISSIONS': {
    status: 403,
    errorType: 'AuthorizationError',
    name: 'Insufficient permissions',
    message: 'User does not have required permissions for this operation',
    details: '{"required": "jobs:write", "user": "read-only-user"}'
  },
  'ACCOUNT_SUSPENDED': {
    status: 403,
    errorType: 'AuthorizationError',
    name: 'Account suspended',
    message: 'User account has been suspended',
    details: '{"reason": "payment overdue", "contact": "support@click2mail.com"}'
  },
  'JOB_NOT_FOUND': {
    status: 404,
    errorType: 'ResourceNotFoundError',
    name: 'Job not found',
    message: 'The specified job does not exist',
    details: '{"resourceType": "job", "jobId": "JOB-12345"}'
  },
  'RESOURCE_NOT_FOUND': {
    status: 404,
    errorType: 'ResourceNotFoundError',
    name: 'Resource not found',
    message: 'Requested resource does not exist',
    details: '{"resourceType": "document", "resourceId": "DOC-12345"}'
  },
  'INVALID_ENUM_VALUE': {
    status: 422,
    errorType: 'ValidationError',
    name: 'Invalid enum value',
    message: 'Field contains a value not allowed by the enumeration',
    details: '{"field": "mailClass", "provided": "express", "allowed": ["First", "Standard"]}'
  },
  'MUTUAL_EXCLUSION_VIOLATION': {
    status: 422,
    errorType: 'ValidationError',
    name: 'Mutually exclusive fields',
    message: 'Request contains mutually exclusive fields',
    details: '{"conflict": "documentId and documentUrl cannot both be specified"}'
  },
  'INVALID_FORMAT': {
    status: 422,
    errorType: 'ValidationError',
    name: 'Invalid field format',
    message: 'Field contains invalid format or value',
    details: '{"field": "postalCode", "provided": "1234", "expected": "5 or 9 digits"}'
  },
  'SERVER_ERROR': {
    status: 500,
    errorType: 'ServerError',
    name: 'Internal server error',
    message: 'An unexpected error occurred while processing the request',
    details: '{"timestamp": "2026-03-11T18:30:45Z", "requestId": "req-abc123"}'
  },
  'DATABASE_ERROR': {
    status: 500,
    errorType: 'ServerError',
    name: 'Database error',
    message: 'Database operation failed',
    details: '{"operation": "insert", "table": "jobs", "error": "connection timeout"}'
  },
  'EXTERNAL_SERVICE_ERROR': {
    status: 500,
    errorType: 'ServerError',
    name: 'External service error',
    message: 'External service call failed',
    details: '{"service": "address-validation", "error": "timeout after 30s"}'
  }
};

/**
 * Load error codes from OpenAPI spec and generate ERROR_RESPONSES object
 */
function loadErrorResponsesFromSpec(openapiSpecPath) {
  console.log(`Loading error codes from OpenAPI spec: ${openapiSpecPath}`);

  // Read and parse OpenAPI spec
  const specContent = fs.readFileSync(openapiSpecPath, 'utf8');
  const spec = yaml.load(specContent);

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

  // Group error codes by HTTP status
  const errorResponsesByStatus = {};

  errorCodes.forEach(errorCode => {
    const metadata = ERROR_CODE_METADATA[errorCode];
    if (!metadata) {
      console.warn(`⚠️  No metadata for error code: ${errorCode}, skipping`);
      return;
    }

    const statusCode = metadata.status.toString();
    if (!errorResponsesByStatus[statusCode]) {
      errorResponsesByStatus[statusCode] = [];
    }

    // Generate tracking ID
    const trackingId = `TRK-${new Date().toISOString().split('T')[0].replace(/-/g, '')}-${generateUUID().split('-')[0].toUpperCase()}`;

    // Create error response object
    errorResponsesByStatus[statusCode].push({
      id: generateUUID(),
      name: metadata.name,
      status: HTTP_STATUS_TEXT[metadata.status],
      code: metadata.status,
      _postman_previewlanguage: 'json',
      header: [{ key: 'Content-Type', value: 'application/json' }],
      body: JSON.stringify({
        errorType: metadata.errorType,
        errorMessage: metadata.message,
        errorCode: errorCode,
        errorDetails: metadata.details,
        errorTrackingId: trackingId
      }, null, 2)
    });
  });

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

  if (args.length !== 2) {
    console.error('Usage: node add_error_responses_to_collection.js <input_collection> <output_collection>');
    process.exit(1);
  }

  const [inputFile, outputFile] = args;

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
