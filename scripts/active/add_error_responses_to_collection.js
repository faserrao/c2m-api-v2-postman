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

// Error response templates (realistic data, not placeholders)
const ERROR_RESPONSES = {
  '400': [
    {
      name: 'Missing required field',
      code: 400,
      _postman_previewlanguage: 'json',
      header: [{ key: 'Content-Type', value: 'application/json' }],
      body: JSON.stringify({
        errorType: 'ValidationError',
        errorMessage: 'Required field is missing from request body',
        errorCode: 'MISSING_REQUIRED_FIELD',
        errorDetails: '{"field": "documentId", "location": "requestBody"}',
        errorTrackingId: 'TRK-20260216-ABC123'
      }, null, 2)
    },
    {
      name: 'Invalid field format',
      code: 400,
      _postman_previewlanguage: 'json',
      header: [{ key: 'Content-Type', value: 'application/json' }],
      body: JSON.stringify({
        errorType: 'ValidationError',
        errorMessage: 'Field contains invalid format or value',
        errorCode: 'INVALID_FORMAT',
        errorDetails: '{"field": "postalCode", "provided": "1234", "expected": "5 or 9 digits"}',
        errorTrackingId: 'TRK-20260216-DEF456'
      }, null, 2)
    }
  ],
  '401': [
    {
      name: 'Missing authentication',
      code: 401,
      _postman_previewlanguage: 'json',
      header: [{ key: 'Content-Type', value: 'application/json' }],
      body: JSON.stringify({
        errorType: 'AuthenticationError',
        errorMessage: 'Authorization header is missing or invalid',
        errorCode: 'MISSING_AUTH_HEADER',
        errorDetails: '{"expected": "Bearer <token>", "received": "none"}',
        errorTrackingId: 'TRK-20260216-GHI789'
      }, null, 2)
    }
  ],
  '403': [
    {
      name: 'Insufficient permissions',
      code: 403,
      _postman_previewlanguage: 'json',
      header: [{ key: 'Content-Type', value: 'application/json' }],
      body: JSON.stringify({
        errorType: 'AuthorizationError',
        errorMessage: 'User does not have required permissions for this operation',
        errorCode: 'INSUFFICIENT_PERMISSIONS',
        errorDetails: '{"required": "jobs:write", "user": "read-only-user"}',
        errorTrackingId: 'TRK-20260216-JKL012'
      }, null, 2)
    }
  ],
  '404': [
    {
      name: 'Resource not found',
      code: 404,
      _postman_previewlanguage: 'json',
      header: [{ key: 'Content-Type', value: 'application/json' }],
      body: JSON.stringify({
        errorType: 'ResourceNotFoundError',
        errorMessage: 'Requested resource does not exist',
        errorCode: 'RESOURCE_NOT_FOUND',
        errorDetails: '{"resourceType": "document", "resourceId": "DOC-12345"}',
        errorTrackingId: 'TRK-20260216-MNO345'
      }, null, 2)
    }
  ],
  '422': [
    {
      name: 'Validation failed',
      code: 422,
      _postman_previewlanguage: 'json',
      header: [{ key: 'Content-Type', value: 'application/json' }],
      body: JSON.stringify({
        errorType: 'ValidationError',
        errorMessage: 'Request validation failed for multiple fields',
        errorCode: 'INVALID_FORMAT',
        errorDetails: '{"errors": [{"field": "documentId", "issue": "not found"}, {"field": "recipientAddress.postalCode", "issue": "invalid format"}]}',
        errorTrackingId: 'TRK-20260216-PQR678'
      }, null, 2)
    }
  ],
  '500': [
    {
      name: 'Internal server error',
      code: 500,
      _postman_previewlanguage: 'json',
      header: [{ key: 'Content-Type', value: 'application/json' }],
      body: JSON.stringify({
        errorType: 'ServerError',
        errorMessage: 'An unexpected error occurred while processing the request',
        errorCode: 'SERVER_ERROR',
        errorDetails: '{"timestamp": "2026-02-16T18:30:45Z", "requestId": "req-abc123"}',
        errorTrackingId: 'TRK-20260216-STU901'
      }, null, 2)
    }
  ]
};

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

      // Add all error responses (400, 401, 403, 404, 422, 500)
      Object.keys(ERROR_RESPONSES).forEach(errorCode => {
        ERROR_RESPONSES[errorCode].forEach(errorResponse => {
          item.response.push(errorResponse);
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
