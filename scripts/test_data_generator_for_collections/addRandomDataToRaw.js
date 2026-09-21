#!/usr/bin/env node
/**
 * addRandomDataToRaw_oneOf.js
 * 
 * OneOf-aware version of the random data generator for Postman collections.
 * This script properly handles oneOf schemas in the C2M API by generating
 * appropriate complex objects instead of simple strings.
 * 
 * Features:
 * - Recognizes and properly handles oneOf fields
 * - Rotates through different oneOf variants for comprehensive testing
 * - Preserves existing valid examples
 * - Falls back to intelligent faker-based generation for other fields
 */

const fs = require('fs');
const path = require('path');
const { faker } = require('@faker-js/faker');
const yaml = require('js-yaml');

/**
 * Parse command line arguments
 */
function parseArgs() {
    const args = process.argv.slice(2);
    const options = {
        input: null,
        output: null,
        errorRate: 0,
        preview: false,
        force: false,
        defaultTemplate: null,
        spec: null,
        fakerHints: null
    };

    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--input':
                options.input = args[++i];
                break;
            case '--output':
                options.output = args[++i];
                break;
            case '--error-rate':
                options.errorRate = parseInt(args[++i]) || 0;
                break;
            case '--preview':
                options.preview = true;
                break;
            case '--force':
                options.force = true;
                break;
            case '--default-template':
                options.defaultTemplate = args[++i];
                break;
            case '--spec':
                options.spec = args[++i];
                break;
            case '--faker-hints':
                options.fakerHints = args[++i];
                break;
        }
    }

    // Validate required arguments
    if (!options.input) {
        console.error('Error: --input is required');
        console.log('Usage: node addRandomDataToRaw_oneOf.js --input <file> --output <file> [--error-rate <0-100>] [--preview]');
        process.exit(1);
    }

    // Default output to input-randomized.json if not specified
    if (!options.output && !options.preview) {
        const inputPath = path.parse(options.input);
        options.output = path.join(inputPath.dir, `${inputPath.name}-randomized${inputPath.ext}`);
    }

    // Validate error rate
    if (options.errorRate < 0 || options.errorRate > 100) {
        console.error('Error: --error-rate must be between 0 and 100');
        process.exit(1);
    }

    return options;
}

/**
 * Faker hints loaded from config/faker_hints.yaml (populated in main() when --faker-hints is passed).
 * Keys are DD rule names; values are hint descriptors { type, method/value/min/max }.
 */
let fakerHints = {};

/**
 * Generate a 6-character uppercase hex suffix for tracking IDs.
 * Canonical format: TRK-YYYYMMDD-XXXXXX where XXXXXX is 6 hex chars.
 * Matches the Python implementation in ebnf_to_openapi_dynamic_v3.py and
 * add_response_examples.py.
 */
function hexSuffix() {
    return Array.from({ length: 6 }, () => '0123456789ABCDEF'[Math.floor(Math.random() * 16)]).join('');
}

/**
 * OneOf fixtures for C2M API fields — named-wrapper format.
 * Each variant is wrapped in its type name as the top-level key,
 * matching the OpenAPI spec's named-wrapper oneOf structure.
 *
 * When --spec is passed, loadOneOfFixturesFromSpec() replaces all spec-derivable entries
 * at startup so this block serves only as a fallback (and for errorResponse, which has no
 * spec schema and remains hardcoded here permanently).
 */
let oneOfFixtures = {
    recipientAddressSource: [
        // Variant 1: singleAddress
        {
            singleAddress: {
                firstName: "John",
                lastName: "Smith",
                address1: "123 Main St",
                address2: "",
                address3: "",
                city: "Springfield",
                state: "IL",
                zip: "62701",
                country: "USA",
                foo1: "",
                foo2: ""
            }
        },
        // Variant 2: recipientAddressByList
        {
            recipientAddressByList: {
                mappingId: 1,
                addressList: [
                    {
                        firstName: "Jane",
                        lastName: "Doe",
                        address1: "456 Oak Ave",
                        city: "Chicago",
                        state: "IL",
                        zip: "60601",
                        country: "USA"
                    }
                ],
                addressListName: "Marketing Campaign Q1"
            }
        },
        // Variant 3: recipientAddressByAddressId (integer)
        {
            recipientAddressByAddressId: 5000
        },
        // Variant 4: recipientAddressByListId (integer)
        {
            recipientAddressByListId: 1001
        }
    ],

    paymentDetails: [
        // Variant 1: creditCardPayment
        {
            creditCardDetails: {
                cardType: "visa",
                cardNumber: "4111111111111111",
                expirationDate: {
                    month: 12,
                    year: 2029
                },
                cvv: 123
            }
        },
        // Variant 2: invoicePayment
        {
            invoiceDetails: {
                invoiceNumber: `INV-${new Date().getFullYear()}-001`,
                amountDue: 99.99
            }
        },
        // Variant 3: achPayment
        {
            achDetails: {
                routingNumber: "021000021",
                accountNumber: "1234567890",
                checkDigit: 5
            }
        },
        // Variant 4: userCreditPayment
        {
            creditAmount: {
                amount: 50.00,
                currency: "USD"
            }
        }
    ],

    docSourceAll: [
        // Variant 1: documentIdSource
        { documentIdSource: { documentId: 12345 } },
        // Variant 2: requestIdSource
        { requestIdSource: { requestId: 67890, filename: "document.pdf" } },
        // Variant 3: urlSource
        { urlSource: { url: "https://example.com/documents/sample.pdf" } },
        // Variant 4: zipDocumentIdSource
        { zipDocumentIdSource: { zipDocumentId: 11111, filename: "letter.pdf" } },
        // Variant 5: zipRequestIdSource
        { zipRequestIdSource: { requestId: 22222, zipFilename: "archive.zip", filename: "letter.pdf" } }
    ],

    docSourceStandard: [
        // Variant 1: documentIdSource
        { documentIdSource: { documentId: 12345 } },
        // Variant 2: requestIdSource
        { requestIdSource: { requestId: 67890, filename: "document.pdf" } },
        // Variant 3: urlSource
        { urlSource: { url: "https://example.com/documents/sample.pdf" } }
    ],

    docSourceZipFile: [
        // Variant 1: zipDocumentIdSource
        { zipDocumentIdSource: { zipDocumentId: 11111, filename: "letter.pdf" } },
        // Variant 2: zipRequestIdSource
        { zipRequestIdSource: { requestId: 22222, zipFilename: "archive.zip", filename: "letter.pdf" } }
    ],

    zipDocumentSource: [
        // Variant 1: zipDocumentIdSource
        { zipDocumentIdSource: { zipDocumentId: 11111, filename: "letter.pdf" } },
        // Variant 2: zipRequestIdSource
        { zipRequestIdSource: { requestId: 22222, zipFilename: "archive.zip", filename: "letter.pdf" } }
    ],

    mergeDocumentSource: [
        // Variant 1: two mergeByDocumentId items
        [
            { mergeByDocumentId: { documentId: 12345 } },
            { mergeByDocumentId: { documentId: 67890 } }
        ],
        // Variant 2: two mergeByRequestId items
        [
            { mergeByRequestId: { requestId: 12345, filename: "doc-a.pdf" } },
            { mergeByRequestId: { requestId: 67890, filename: "doc-b.pdf" } }
        ],
        // Variant 3: mixed
        [
            { mergeByDocumentId: { documentId: 11111 } },
            { mergeByRequestId: { requestId: 22222, filename: "doc-b.pdf" } }
        ]
    ],

    // A2: errorType values must stay in sync with the spec's errorType.enum.
    // Canonical values: ValidationError, AuthenticationError, AuthorizationError,
    // ResourceNotFoundError, ServerError (from EBNF DD errorType rule).
    // This fixture block is intentionally excluded from spec-driven generation
    // (errorResponse is not a oneOf variant schema — see loadOneOfFixturesFromSpec comment).
    errorResponse: [
        // Variant 1: ValidationError - Missing Field
        {
            errorType: "ValidationError",
            errorMessage: "Required field is missing from request body",
            errorCode: "MISSING_REQUIRED_FIELD",
            errorDetails: JSON.stringify({ field: "documentId", location: "requestBody" }),
            errorTrackingId: `TRK-${new Date().toISOString().slice(0,10).replace(/-/g, '')}-${hexSuffix()}`
        },
        // Variant 2: ValidationError - Invalid OneOf (field name matches EBNF DD: docSourceAll)
        {
            errorType: "ValidationError",
            errorMessage: "Request contains invalid oneOf field structure",
            errorCode: "INVALID_ONEOF",
            errorDetails: JSON.stringify({ field: "docSourceAll", issue: "must contain exactly one variant" }),
            errorTrackingId: `TRK-${new Date().toISOString().slice(0,10).replace(/-/g, '')}-${hexSuffix()}`
        },
        // Variant 3: ValidationError - Invalid Format (field name matches EBNF DD: zip)
        {
            errorType: "ValidationError",
            errorMessage: "Field contains invalid format or value",
            errorCode: "INVALID_FORMAT",
            errorDetails: JSON.stringify({ field: "zip", provided: "1234", expected: "5 or 9 digits" }),
            errorTrackingId: `TRK-${new Date().toISOString().slice(0,10).replace(/-/g, '')}-${hexSuffix()}`
        },
        // Variant 4: AuthenticationError - Missing Auth
        {
            errorType: "AuthenticationError",
            errorMessage: "Authorization header is missing or invalid",
            errorCode: "MISSING_AUTH_HEADER",
            errorDetails: JSON.stringify({ expected: "Bearer <token>", received: "none" }),
            errorTrackingId: `TRK-${new Date().toISOString().slice(0,10).replace(/-/g, '')}-${hexSuffix()}`
        },
        // Variant 5: AuthenticationError - Expired Token
        {
            errorType: "AuthenticationError",
            errorMessage: "Authentication token has expired",
            errorCode: "EXPIRED_TOKEN",
            errorDetails: JSON.stringify({ expiredAt: "2026-02-16T12:00:00Z", currentTime: "2026-02-16T15:30:00Z" }),
            errorTrackingId: `TRK-${new Date().toISOString().slice(0,10).replace(/-/g, '')}-${hexSuffix()}`
        },
        // Variant 6: AuthorizationError - Insufficient Permissions
        {
            errorType: "AuthorizationError",
            errorMessage: "User does not have required permissions for this operation",
            errorCode: "INSUFFICIENT_PERMISSIONS",
            errorDetails: JSON.stringify({ required: "jobs:write", user: "read-only-user" }),  // L-2: must match _ERROR_AUTH_SCOPE_REQUIRED in ebnf_to_openapi_dynamic_v3.py
            errorTrackingId: `TRK-${new Date().toISOString().slice(0,10).replace(/-/g, '')}-${hexSuffix()}`
        },
        // Variant 7: ResourceNotFoundError - Job Not Found
        {
            errorType: "ResourceNotFoundError",
            errorMessage: "Requested job does not exist",
            errorCode: "JOB_NOT_FOUND",
            errorDetails: JSON.stringify({ resourceType: "job", jobId: "JOB-12345" }),
            errorTrackingId: `TRK-${new Date().toISOString().slice(0,10).replace(/-/g, '')}-${hexSuffix()}`
        },
        // Variant 8: ResourceNotFoundError - Resource Not Found
        {
            errorType: "ResourceNotFoundError",
            errorMessage: "Requested resource does not exist",
            errorCode: "RESOURCE_NOT_FOUND",
            errorDetails: JSON.stringify({ resourceType: "document", resourceId: "DOC-67890" }),
            errorTrackingId: `TRK-${new Date().toISOString().slice(0,10).replace(/-/g, '')}-${hexSuffix()}`
        },
        // Variant 9: ValidationError - Multiple Field Errors (field names match EBNF DD)
        {
            errorType: "ValidationError",
            errorMessage: "Request validation failed for multiple fields",
            errorCode: "INVALID_FORMAT",
            errorDetails: JSON.stringify({
                errors: [
                    { field: "documentId", issue: "not found in document library" },
                    { field: "recipientAddressSource.zip", issue: "invalid format - must be 5 or 9 digits" }  // B-new-2: DD rule is recipientAddressSource
                ]
            }),
            errorTrackingId: `TRK-${new Date().toISOString().slice(0,10).replace(/-/g, '')}-${hexSuffix()}`
        },
        // Variant 10: ServerError - Internal Error
        {
            errorType: "ServerError",
            errorMessage: "An unexpected error occurred while processing the request",
            errorCode: "SERVER_ERROR",  // A1: DD canonical code (was "INTERNAL_SERVER_ERROR")
            errorDetails: JSON.stringify({ timestamp: new Date().toISOString(), requestId: `req-${hexSuffix()}${hexSuffix()}` }),
            errorTrackingId: `TRK-${new Date().toISOString().slice(0,10).replace(/-/g, '')}-${hexSuffix()}`
        }
    ]
};

// ── HC1/HC2: spec-driven fixtures and faker hints ────────────────────────────

/**
 * Apply a faker_hints entry to produce a concrete value.
 */
function applyHint(hint) {
    if (!hint) return null;
    switch (hint.type) {
        case 'static':
            return hint.value;
        case 'random_int':
            return faker.number.int({ min: hint.min || 1, max: hint.max || 9999 });
        case 'faker': {
            // Map Python faker method names to @faker-js/faker v9 equivalents
            const FAKER_METHOD_MAP = {
                'first_name':     () => faker.person.firstName(),
                'last_name':      () => faker.person.lastName(),
                'company':        () => faker.company.name(),
                'street_address': () => faker.location.streetAddress(),
                'city':           () => faker.location.city(),
                'state':          () => faker.location.state(),
                'state_abbr':     () => faker.location.state({ abbreviated: true }),
                'zipcode':        () => faker.location.zipCode(),
                'zip_code':       () => faker.location.zipCode(),
                'email':          () => faker.internet.email(),
                'url':            () => faker.internet.url(),
                'phone_number':   () => faker.phone.number(),
            };
            const fn = FAKER_METHOD_MAP[hint.method];
            return fn ? fn() : faker.lorem.word();
        }
        case 'aba_routing_number':
            return faker.finance.routingNumber();
        default:
            return null;
    }
}

/**
 * Load faker hints from a YAML file.
 * Returns the faker_hints map keyed by DD rule name.
 */
function loadFakerHints(hintsPath) {
    try {
        const content = fs.readFileSync(hintsPath, 'utf8');
        const data = yaml.load(content);
        return (data && data.faker_hints) || {};
    } catch (err) {
        console.error(`Warning: Could not load faker hints from ${hintsPath}: ${err.message}`);
        return {};
    }
}

/**
 * Resolve a $ref string (e.g. '#/components/schemas/Foo') to its schema object.
 */
function resolveRef(spec, ref) {
    if (!ref || !ref.startsWith('#/')) return null;
    const parts = ref.slice(2).split('/');
    let node = spec;
    for (const part of parts) {
        if (!node || typeof node !== 'object') return null;
        node = node[part];
    }
    // Follow one more level of $ref if the resolved node is itself a $ref
    if (node && node.$ref && node.$ref !== ref) {
        return resolveRef(spec, node.$ref);
    }
    return node || null;
}

/**
 * Build a sample JSON value from an OpenAPI schema, using fakerHints for leaf fields.
 * fieldName is the property name used for hint lookup (DD rule name).
 */
function buildSampleFromSchema(spec, schema, depth, fieldName) {
    if (depth > 7 || !schema) return null;

    // Hint lookup by property name
    if (fieldName && fakerHints[fieldName] !== undefined) {
        return applyHint(fakerHints[fieldName]);
    }

    // Resolve $ref — also try the schema name from the ref for hint lookup
    if (schema.$ref) {
        const refSchemaName = schema.$ref.split('/').pop();
        if (fakerHints[refSchemaName] !== undefined) {
            return applyHint(fakerHints[refSchemaName]);
        }
        const resolved = resolveRef(spec, schema.$ref);
        if (!resolved) return null;
        return buildSampleFromSchema(spec, resolved, depth + 1, fieldName);
    }

    if (schema.type === 'object' && schema.properties) {
        const result = {};
        for (const [propName, propSchema] of Object.entries(schema.properties)) {
            const val = buildSampleFromSchema(spec, propSchema, depth + 1, propName);
            if (val !== null && val !== undefined) result[propName] = val;
        }
        return Object.keys(result).length > 0 ? result : null;
    }

    if (schema.type === 'array') {
        if (!schema.items) return [];
        const item = buildSampleFromSchema(spec, schema.items, depth + 1, fieldName);
        return item !== null ? [item] : [];
    }

    if (schema.type === 'integer') return faker.number.int({ min: 10000, max: 99999 });
    if (schema.type === 'number')  return parseFloat(faker.commerce.price());
    if (schema.type === 'string') {
        if (schema.enum && schema.enum.length > 0) return schema.enum[0];
        if (schema.format === 'uri') return 'https://example.com/documents/sample.pdf';
        return faker.lorem.word();
    }
    if (schema.type === 'boolean') return true;

    return null;
}

/**
 * Load oneOf fixtures from the OpenAPI spec at runtime.
 * Discovers all top-level schemas with oneOf and builds named-wrapper variant objects.
 *
 * Special case: mergeDocumentSource is an array (documentsToMerge) whose items are
 * mergeDocumentRef (oneOf) — so its variants are arrays of items, not single objects.
 *
 * errorResponse is excluded — it is not a spec schema and remains hardcoded above.
 */
function loadOneOfFixturesFromSpec(spec) {
    const schemas = (spec.components && spec.components.schemas) || {};
    const fixtures = {};

    for (const [schemaName, schema] of Object.entries(schemas)) {
        // mergeDocumentRef items are composed into mergeDocumentSource below
        if (schemaName === 'mergeDocumentRef') continue;

        const resolved = schema.$ref ? resolveRef(spec, schema.$ref) : schema;
        if (!resolved || !resolved.oneOf) continue;

        const variants = resolved.oneOf
            .map(variant => {
                const s = variant.$ref ? resolveRef(spec, variant.$ref) : variant;
                return s ? buildSampleFromSchema(spec, s, 0, null) : null;
            })
            .filter(v => v !== null && v !== undefined);

        if (variants.length > 0) fixtures[schemaName] = variants;
    }

    // Special case: mergeDocumentSource = array of mergeDocumentRef variants
    const mergeRefSchema = schemas['mergeDocumentRef'];
    if (mergeRefSchema && mergeRefSchema.oneOf) {
        const buildItem = (idx) => {
            const v = mergeRefSchema.oneOf[idx];
            const s = v.$ref ? resolveRef(spec, v.$ref) : v;
            return s ? buildSampleFromSchema(spec, s, 0, null) : null;
        };
        const n = mergeRefSchema.oneOf.length;
        const arrayVariants = [];

        // Two items both using first variant (e.g. two mergeByDocumentId)
        const a = buildItem(0), b = buildItem(0);
        if (a && b) arrayVariants.push([a, b]);

        // Two items both using second variant (e.g. two mergeByRequestId)
        if (n >= 2) {
            const c = buildItem(1), d = buildItem(1);
            if (c && d) arrayVariants.push([c, d]);
        }

        // Mixed: one item per variant
        if (n >= 2) {
            const e = buildItem(0), f = buildItem(1);
            if (e && f) arrayVariants.push([e, f]);
        }

        if (arrayVariants.length > 0) fixtures['mergeDocumentSource'] = arrayVariants;
    }

    return fixtures;
}

// ── end HC1/HC2 ──────────────────────────────────────────────────────────────

// Track rotation index per field to ensure we cycle through all variants
const rotationIndex = {};

// Statistics tracking
const stats = {
    modifiedRequests: 0,
    modifiedResponses: 0,
    modifiedOriginalRequests: 0,
    oneOfReplacements: {}
};

/**
 * Get the next oneOf value in rotation for a given field
 */
function getNextOneOfValue(fieldName) {
    const variants = oneOfFixtures[fieldName];
    if (!variants || variants.length === 0) return null;

    // Initialize rotation index for this field if needed
    if (!(fieldName in rotationIndex)) {
        rotationIndex[fieldName] = 0;
    }

    // Get current variant
    const currentIndex = rotationIndex[fieldName];
    const value = JSON.parse(JSON.stringify(variants[currentIndex])); // Deep clone to avoid mutations

    // Update rotation index for next time
    rotationIndex[fieldName] = (currentIndex + 1) % variants.length;

    // Track statistics
    stats.oneOfReplacements[fieldName] = (stats.oneOfReplacements[fieldName] || 0) + 1;

    // CRITICAL FIX: Recursively replace placeholders within the oneOf object
    // The fixtures contain placeholders like "<integer>" and "<string>" that need to be replaced
    processBodyObject(value, fieldName);

    return value;
}

/**
 * Returns true if the value is an array whose every item is a type placeholder.
 * These arrays should be replaced wholesale rather than recursed into, because
 * primitive items ("<integer>", "<string>") are not objects and the recursive
 * traversal would silently skip them.
 */
function isPlaceholderArray(value) {
    if (!Array.isArray(value) || value.length === 0) return false;
    const placeholders = new Set(['<string>', '<integer>', '<number>', '<oneOf>']);
    return value.every(item => typeof item === 'string' && placeholders.has(item));
}

/**
 * Check if a value should be replaced
 */
function shouldReplaceValue(value, key) {
    // Always replace oneOf fields
    if (oneOfFixtures.hasOwnProperty(key)) {
        return true;
    }

    // Replace arrays that contain only type placeholders (e.g. ["<integer>", "<integer>"])
    if (isPlaceholderArray(value)) {
        return true;
    }

    // Replace null, empty, or placeholder values
    if (value === null || value === undefined || value === '') {
        return true;
    }

    // Replace Postman dynamic variables
    if (typeof value === 'string' && value.startsWith('{{$')) {
        return true;
    }

    // Replace generic placeholder strings
    if (typeof value === 'string' && (
        value === '<string>' ||
        value === '<number>' ||
        value === '<integer>' ||
        value === '<oneOf>' ||
        value === 'string' ||
        value === 'number'
    )) {
        return true;
    }

    // HC6: Replace jobOptions enum placeholders generated by fix_oneOf_placeholders.js.
    // Format: ph<val1|val2|...> — see fix_oneOf_placeholders.js convertJobOptionsToPlaceholders().
    if (typeof value === 'string' && value.startsWith('ph<') && value.endsWith('>')) {
        return true;
    }

    // Don't replace existing valid values
    return false;
}

/**
 * Generate random value based on field name and context
 * This is the fallback for non-oneOf fields
 */
function generateRandomValue(key, existingValue) {
    const keyLower = key ? key.toLowerCase() : '';

    // Check if this is a oneOf field first
    if (oneOfFixtures.hasOwnProperty(key)) {
        return getNextOneOfValue(key);
    }

    // HC2: Check faker hints for this field name before key-name heuristics
    if (fakerHints[key] !== undefined) {
        return applyHint(fakerHints[key]);
    }

    // HC6: ph<val1|val2|...> enum placeholder — pick the first (canonical) value.
    // faker_hints covers all jobOptions fields so this is a safety net for future fields.
    if (typeof existingValue === 'string' && existingValue.startsWith('ph<') && existingValue.endsWith('>')) {
        return existingValue.slice(3, -1).split('|')[0];
    }

    // Preserve array type for placeholder arrays — map each item individually.
    // Key-specific overrides below take priority over the generic item-by-item fallback.
    if (isPlaceholderArray(existingValue)) {
        if (keyLower.includes('scope')) return ['api:read', 'api:write'];
        if (keyLower.includes('tag'))   return ['important', 'customer-docs'];
        // Generic: replace each placeholder item with an appropriately-typed value
        return existingValue.map(item => {
            if (item === '<integer>') return faker.number.int({ min: 10000, max: 99999 });
            if (item === '<number>')  return parseFloat(faker.commerce.price());
            return faker.lorem.word(); // '<string>'
        });
    }

    // Context-aware generation based on key name
    if (keyLower.includes('email')) {
        return faker.internet.email();
    } else if (keyLower.includes('phone') || keyLower.includes('tel')) {
        return faker.phone.number();
    } else if (keyLower === 'filename' || keyLower.includes('filename')) {
        return 'document.pdf';
    } else if (keyLower.includes('firstname') || keyLower === 'fname') {
        return faker.person.firstName();
    } else if (keyLower.includes('lastname') || keyLower === 'lname') {
        return faker.person.lastName();
    } else if (keyLower.includes('name') && !keyLower.includes('username')) {
        return faker.person.fullName();
    } else if (keyLower.includes('username') || keyLower.includes('user')) {
        return faker.internet.userName();
    } else if (keyLower.includes('password') || keyLower.includes('pwd')) {
        return faker.internet.password();
    } else if (keyLower.includes('city')) {
        return faker.location.city();
    } else if (keyLower.includes('country')) {
        return faker.location.country();
    } else if (keyLower.includes('state') || keyLower.includes('province')) {
        return faker.location.state();
    } else if (keyLower.includes('zip') || keyLower.includes('postal')) {
        return faker.location.zipCode();
    } else if (keyLower.includes('address') || keyLower.includes('street')) {
        return faker.location.streetAddress();
    } else if (keyLower.includes('company') || keyLower.includes('organization')) {
        return faker.company.name();
    } else if (keyLower.includes('title') && !keyLower.includes('jobtitle')) {
        return faker.lorem.sentence(3);
    } else if (keyLower.includes('description')) {
        return faker.lorem.paragraph();
    } else if (keyLower.includes('amount') || keyLower.includes('price') || keyLower.includes('cost')) {
        return parseFloat(faker.commerce.price());
    } else if (keyLower.includes('quantity') || keyLower.includes('count')) {
        return faker.number.int({ min: 1, max: 100 });
    } else if (keyLower.includes('date') && !keyLower.includes('update')) {
        return faker.date.future().toISOString().split('T')[0];
    } else if (keyLower.includes('time') || keyLower.includes('timestamp')) {
        return faker.date.recent().toISOString();
    } else if (keyLower.includes('url') || keyLower.includes('uri') || keyLower.includes('link')) {
        return faker.internet.url();
    } else if (keyLower.includes('image') || keyLower.includes('photo') || keyLower.includes('avatar')) {
        return faker.image.url();
    } else if (keyLower.includes('id') && !keyLower.includes('email') && existingValue !== '<string>') {
        return faker.number.int({ min: 10000, max: 99999 });
    } else if (keyLower.includes('tags')) {
        return ['important', 'customer-docs'];
    } else if (keyLower === 'jobtemplate' || keyLower === 'job_template') {
        // faker_hints.yaml (EBNF @hint annotation) should provide this value via the
        // hint-lookup path above — this branch is a safety net for missing hint entries.
        // If reached, add a @hint for jobTemplate in the EBNF DD.
        console.warn('[addRandomDataToRaw] jobTemplate not in faker_hints — using hardcoded fallback; add @hint in EBNF DD');
        return 'standard_letter';  // L-3: must match `jobTemplate = ... ; (* @hint static standard_letter *)` in c2mapiv2-dd.ebnf
    } else if (keyLower.includes('template')) {
        return `template_${faker.string.alphanumeric(8)}`;
    } else if (keyLower.includes('year')) {
        return faker.number.int({ min: 2024, max: 2030 });
    } else if (keyLower.includes('month')) {
        return faker.number.int({ min: 1, max: 12 });
    } else if (keyLower.includes('cvv')) {
        return faker.number.int({ min: 100, max: 999 });
    } else if (keyLower.includes('routing')) {
        return faker.finance.routingNumber();
    } else if (keyLower.includes('account')) {
        return '1234567890';
    } else if (keyLower.includes('status')) {
        return 'accepted';
    } else if (keyLower.includes('message')) {
        return 'Your request has been queued';
    } else if (keyLower === 'jobid' || (keyLower.includes('job') && keyLower.includes('id'))) {
        return `job_${Date.now()}_${faker.string.alphanumeric(6)}`;
    } else if (keyLower === 'startpage') {
        return faker.number.int({ min: 1, max: 10 });
    } else if (keyLower === 'endpage') {
        return faker.number.int({ min: 11, max: 50 });
    } else if (keyLower.includes('page')) {
        return faker.number.int({ min: 1, max: 50 });
    } else if (existingValue === '<integer>') {
        return faker.number.int({ min: 1, max: 9999 });
    } else {
        // Better default fallback - use a sensible default
        return faker.helpers.arrayElement(['default', 'standard', 'basic', 'primary']);
    }
}

/**
 * Process a request/response body object recursively
 */
function processBodyObject(obj, path = '') {
    if (!obj || typeof obj !== 'object') return;

    // Handle arrays
    if (Array.isArray(obj)) {
        obj.forEach((item, index) => {
            if (typeof item === 'object') {
                processBodyObject(item, `${path}[${index}]`);
            }
        });
        return;
    }

    // Handle objects
    Object.keys(obj).forEach(key => {
        const value = obj[key];
        const currentPath = path ? `${path}.${key}` : key;

        if (shouldReplaceValue(value, key)) {
            obj[key] = generateRandomValue(key, value);
        } else if (typeof value === 'object' && value !== null) {
            processBodyObject(value, currentPath);
        }
    });
}

/**
 * Counter for alternating between jobTemplate and jobOptions patterns
 */
let jobPatternCounter = 0;

/**
 * Enforce mutual exclusion for jobTemplate and jobOptions
 * Business rule: Both are optional, but cannot coexist (API will reject)
 * Strategy: Alternate between template-based and options-based examples
 */
function enforceMutualExclusion(bodyObj) {
    // Only apply if both fields exist
    if (!bodyObj.hasOwnProperty('jobTemplate') || !bodyObj.hasOwnProperty('jobOptions')) {
        return; // Nothing to do - only one or neither exists
    }

    // Alternate between keeping template vs options
    // Even requests: keep template, remove options
    // Odd requests: keep options, remove template
    if (jobPatternCounter % 2 === 0) {
        delete bodyObj.jobOptions;
        console.log('  [Mutual Exclusion] Keeping jobTemplate, removing jobOptions');
    } else {
        delete bodyObj.jobTemplate;
        console.log('  [Mutual Exclusion] Keeping jobOptions, removing jobTemplate');
    }

    jobPatternCounter++;
}

/**
 * Process a single collection item (request)
 */
function processItem(item) {
    // Process request body
    if (item.request && item.request.body && item.request.body.raw) {
        try {
            const bodyObj = JSON.parse(item.request.body.raw);

            // Enforce jobTemplate/jobOptions mutual exclusion FIRST
            enforceMutualExclusion(bodyObj);

            // Then process normally
            processBodyObject(bodyObj);
            item.request.body.raw = JSON.stringify(bodyObj, null, 2);
            stats.modifiedRequests++;
        } catch (e) {
            // Skip non-JSON bodies
        }
    }

    // Process response examples
    if (item.response && Array.isArray(item.response)) {
        item.response.forEach(response => {
            // Skip error responses (400-599) - they have realistic examples already
            const statusCode = parseInt(response.code || response.status || 200);
            if (statusCode >= 400 && statusCode < 600) {
                return; // Skip this error response
            }

            // Process success response body (200-299)
            if (response.body) {
                try {
                    const responseBody = JSON.parse(response.body);
                    processBodyObject(responseBody);
                    response.body = JSON.stringify(responseBody, null, 2);
                    stats.modifiedResponses++;
                } catch (e) {
                    // Skip non-JSON bodies
                }
            }

            // Process originalRequest in responses
            if (response.originalRequest && response.originalRequest.body && response.originalRequest.body.raw) {
                try {
                    const originalBody = JSON.parse(response.originalRequest.body.raw);
                    processBodyObject(originalBody);
                    response.originalRequest.body.raw = JSON.stringify(originalBody, null, 2);
                    stats.modifiedOriginalRequests++;
                } catch (e) {
                    // Skip non-JSON bodies
                }
            }
        });
    }

    // Recursively process sub-items (folders)
    if (item.item && Array.isArray(item.item)) {
        item.item.forEach(subItem => processItem(subItem));
    }
}

/**
 * Main execution
 */
function main() {
    const options = parseArgs();

    try {
        // HC2: Load faker hints if provided — must come before spec loading (buildSampleFromSchema uses them)
        if (options.fakerHints) {
            fakerHints = loadFakerHints(options.fakerHints);
            console.log(`Loaded ${Object.keys(fakerHints).length} faker hint(s) from ${options.fakerHints}`);
        }

        // HC1: Load spec-derived oneOf fixtures if spec provided
        if (options.spec) {
            const specContent = fs.readFileSync(options.spec, 'utf8');
            const spec = yaml.load(specContent);
            const specFixtures = loadOneOfFixturesFromSpec(spec);
            Object.assign(oneOfFixtures, specFixtures);
            const variantCount = Object.values(specFixtures).reduce((s, v) => s + v.length, 0);
            console.log(`Loaded ${Object.keys(specFixtures).length} oneOf fixture(s) from spec (${variantCount} total variants)`);
        }

        // Read collection
        const collectionData = fs.readFileSync(options.input, 'utf8');
        const collection = JSON.parse(collectionData);

        console.log(`Processing collection: ${collection.info ? collection.info.name : 'Unnamed'}`);

        // Process all items in the collection
        if (collection.item && Array.isArray(collection.item)) {
            collection.item.forEach(item => processItem(item));
        }

        // Apply error rate if specified
        if (options.errorRate > 0) {
            console.log(`Error rate: ${options.errorRate}%`);
            // TODO: Implement error injection if needed
        } else {
            console.log(`Error rate: 0%`);
        }

        // Output statistics
        console.log(`\nStatistics:`);
        console.log(`- Modified requests: ${stats.modifiedRequests}`);
        console.log(`- Modified responses: ${stats.modifiedResponses}`);
        console.log(`- Modified original requests: ${stats.modifiedOriginalRequests}`);

        // Show oneOf replacement statistics
        if (Object.keys(stats.oneOfReplacements).length > 0) {
            console.log(`\nOneOf field replacements:`);
            Object.entries(stats.oneOfReplacements).forEach(([field, count]) => {
                const totalVariants = oneOfFixtures[field] ? oneOfFixtures[field].length : 0;
                console.log(`- ${field}: ${count} replacements across ${totalVariants} variants`);
            });
        }

        // Show rotation state
        if (Object.keys(rotationIndex).length > 0) {
            console.log(`\nCurrent rotation indices:`);
            Object.entries(rotationIndex).forEach(([field, index]) => {
                const totalVariants = oneOfFixtures[field] ? oneOfFixtures[field].length : 0;
                console.log(`- ${field}: Next variant will be ${index}/${totalVariants}`);
            });
        }

        // Write output
        if (options.preview) {
            console.log('\nPreview mode - no file written');
            console.log('\nFirst 1000 characters of output:');
            console.log(JSON.stringify(collection, null, 2).substring(0, 1000) + '...');
        } else {
            fs.writeFileSync(options.output, JSON.stringify(collection, null, 2));
            console.log(`\nOutput saved to: ${options.output}`);
        }

    } catch (error) {
        console.error('Error processing collection:', error.message);
        process.exit(1);
    }
}

// Run the script
main();