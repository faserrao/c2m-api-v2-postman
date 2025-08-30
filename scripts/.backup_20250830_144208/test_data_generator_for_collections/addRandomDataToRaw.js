#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { faker } = require('@faker-js/faker');

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
        defaultTemplate: null
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
        }
    }

    // Validate required arguments
    if (!options.input) {
        console.error('Error: --input is required');
        console.log('Usage: node addRandomDataToRaw.js --input <file> --output <file> [--error-rate <0-100>] [--preview]');
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
 * Generate random value based on type and context
 */
function randomValue(key, typeHint) {
    const keyLower = key ? key.toLowerCase() : '';

    // Context-aware generation based on key name
    if (keyLower.includes('email')) {
        return faker.internet.email();
    } else if (keyLower.includes('phone') || keyLower.includes('tel')) {
        return faker.phone.number();
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
    } else if (keyLower.includes('jobtitle') || keyLower.includes('position')) {
        return faker.person.jobTitle();
    } else if (keyLower.includes('description') || keyLower.includes('desc')) {
        return faker.lorem.paragraph();
    } else if (keyLower.includes('url') || keyLower.includes('website')) {
        return faker.internet.url();
    } else if (keyLower.includes('date')) {
        return faker.date.recent().toISOString().split('T')[0];
    } else if (keyLower.includes('time')) {
        return faker.date.recent().toISOString();
    } else if (keyLower.includes('uuid') || keyLower.includes('guid')) {
        return faker.string.uuid();
    } else if (keyLower.includes('id')) {
        return faker.string.alphanumeric(10);
    } else if (keyLower.includes('price') || keyLower.includes('cost') || keyLower.includes('amount')) {
        return parseFloat(faker.commerce.price());
    } else if (keyLower.includes('quantity') || keyLower.includes('count')) {
        return faker.number.int({ min: 1, max: 100 });
    } else if (keyLower.includes('age')) {
        return faker.number.int({ min: 18, max: 80 });
    } else if (keyLower.includes('year')) {
        return faker.number.int({ min: 2000, max: 2024 });
    }

    // Type-based generation
    switch (typeHint) {
        case '<string>':
            return faker.lorem.word();
        case '<number>':
            return faker.number.float({ min: 0, max: 1000, multipleOf: 0.01 });
        case '<integer>':
            return faker.number.int({ min: 0, max: 999 });
        case '<boolean>':
            return faker.datatype.boolean();
        default:
            return faker.lorem.word();
    }
}

/**
 * Generate erroneous value for testing error handling
 */
function erroneousValue() {
    const errors = [
        null,
        undefined,
        '',
        'null',
        'undefined',
        'NaN',
        -999999,
        999999999999,
        '!@#$%^&*()',
        '{{{{',
        '}}}}',
        '<script>alert("xss")</script>',
        'DROP TABLE users;',
        '\u0000',
        '\n\r\t',
        '�',
        new Array(1000).fill('x').join(''),
        0.1 + 0.2, // floating point issue
        '2024-13-45', // invalid date
        'not-an-email',
        'http://',
        '192.168.1.999', // invalid IP
    ];

    return errors[Math.floor(Math.random() * errors.length)];
}

/**
 * Recursively replace placeholder values in an object
 */
function replaceValues(obj, errorRate = 0) {
    if (typeof obj === 'string') {
        // Check if it's a placeholder
        if (obj.match(/^<(string|number|integer|boolean)>$/)) {
            // Decide whether to inject error or normal value
            if (Math.random() * 100 < errorRate) {
                return erroneousValue();
            }
            return randomValue('', obj);
        }
        return obj;
    } else if (Array.isArray(obj)) {
        return obj.map(item => replaceValues(item, errorRate));
    } else if (typeof obj === 'object' && obj !== null) {
        const result = {};
        for (const [key, value] of Object.entries(obj)) {
            if (typeof value === 'string' && value.match(/^<(string|number|integer|boolean)>$/)) {
                // Decide whether to inject error or normal value
                if (Math.random() * 100 < errorRate) {
                    result[key] = erroneousValue();
                } else {
                    result[key] = randomValue(key, value);
                }
            } else {
                result[key] = replaceValues(value, errorRate);
            }
        }
        return result;
    }
    return obj;
}

/**
 * Process raw body string
 */
function fillRaw(rawStr, errorRate) {
    if (!rawStr || typeof rawStr !== 'string') {
        return rawStr;
    }

    try {
        // Try to parse as JSON
        const parsed = JSON.parse(rawStr);
        const modified = replaceValues(parsed, errorRate);
        return JSON.stringify(modified, null, 2);
    } catch (e) {
        // If not valid JSON, return as-is
        console.warn('Warning: Could not parse raw body as JSON, skipping...');
        return rawStr;
    }
}

/**
 * Process a single item in the collection
 */
function processItem(item, errorRate, previewMode, stats) {
    let modified = false;

    // Process request body
    if (item.request && item.request.body && item.request.body.mode === 'raw' && item.request.body.raw) {
        const originalRaw = item.request.body.raw;
        const modifiedRaw = fillRaw(originalRaw, errorRate);
        
        if (originalRaw !== modifiedRaw) {
            if (previewMode && !stats.previewShown) {
                console.log('\n=== Preview Mode ===');
                console.log(`Request: ${item.name || 'Unnamed'}`);
                console.log('\nBEFORE:');
                console.log(originalRaw);
                console.log('\nAFTER:');
                console.log(modifiedRaw);
                console.log('===================\n');
                stats.previewShown = true;
            }
            
            item.request.body.raw = modifiedRaw;
            modified = true;
            stats.modifiedRequests++;
        }
    }

    // Process response bodies
    if (item.response && Array.isArray(item.response)) {
        item.response.forEach(resp => {
            if (resp.body) {
                const originalBody = resp.body;
                const modifiedBody = fillRaw(originalBody, errorRate);
                if (originalBody !== modifiedBody) {
                    resp.body = modifiedBody;
                    modified = true;
                    stats.modifiedResponses++;
                }
            }

            // Process originalRequest in response
            if (resp.originalRequest && resp.originalRequest.body && 
                resp.originalRequest.body.mode === 'raw' && resp.originalRequest.body.raw) {
                const originalRaw = resp.originalRequest.body.raw;
                const modifiedRaw = fillRaw(originalRaw, errorRate);
                if (originalRaw !== modifiedRaw) {
                    resp.originalRequest.body.raw = modifiedRaw;
                    modified = true;
                    stats.modifiedOriginalRequests++;
                }
            }
        });
    }

    return modified;
}

/**
 * Recursively process collection items
 */
function processCollection(items, errorRate, previewMode, stats) {
    if (!Array.isArray(items)) {
        return;
    }

    items.forEach(item => {
        // Process current item
        processItem(item, errorRate, previewMode, stats);

        // Recursively process sub-items (folders)
        if (item.item && Array.isArray(item.item)) {
            processCollection(item.item, errorRate, previewMode, stats);
        }
    });
}

/**
 * Main function
 */
function main() {
    const options = parseArgs();

    // Read input file
    let collection;
    try {
        const content = fs.readFileSync(options.input, 'utf8');
        collection = JSON.parse(content);
    } catch (e) {
        console.error(`Error reading input file: ${e.message}`);
        process.exit(1);
    }

    // Validate it's a Postman collection
    if (!collection.info || !collection.item) {
        console.error('Error: Input file does not appear to be a valid Postman collection');
        process.exit(1);
    }

    // Statistics
    const stats = {
        modifiedRequests: 0,
        modifiedResponses: 0,
        modifiedOriginalRequests: 0,
        previewShown: false
    };

    // Process the collection
    console.log(`Processing collection: ${collection.info.name}`);
    console.log(`Error rate: ${options.errorRate}%`);
    
    processCollection(collection.item, options.errorRate, options.preview, stats);

    // Show statistics
    console.log(`\nStatistics:`);
    console.log(`- Modified requests: ${stats.modifiedRequests}`);
    console.log(`- Modified responses: ${stats.modifiedResponses}`);
    console.log(`- Modified original requests: ${stats.modifiedOriginalRequests}`);

    // Save output if not in preview mode
    if (!options.preview && options.output) {
        try {
            fs.writeFileSync(options.output, JSON.stringify(collection, null, 2));
            console.log(`\nOutput saved to: ${options.output}`);
        } catch (e) {
            console.error(`Error writing output file: ${e.message}`);
            process.exit(1);
        }
    } else if (options.preview) {
        console.log('\nPreview mode - no file was saved.');
    }
}

// Run the script
if (require.main === module) {
    main();
}