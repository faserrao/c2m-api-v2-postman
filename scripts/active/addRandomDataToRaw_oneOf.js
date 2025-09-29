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
 * OneOf fixtures for C2M API fields
 * Each field has an array of valid variants that match the oneOf schema
 */
const oneOfFixtures = {
    documentSourceIdentifier: [
        // Variant 1: Just documentId (integer)
        1234,
        // Variant 2: Just externalUrl (string with URI format)
        "https://api.example.com/v1/documents/5678",
        // Variant 3: uploadRequestId + documentName
        {
            uploadRequestId: 100,
            documentName: "invoice_2024_01.pdf"
        },
        // Variant 4: uploadRequestId + zipId + documentName
        {
            uploadRequestId: 200,
            zipId: 10,
            documentName: "statement_jan.pdf"
        },
        // Variant 5: zipId + documentName
        {
            zipId: 20,
            documentName: "report_q1_2024.pdf"
        }
    ],
    
    recipientAddressSource: [
        // Variant 1: exactlyOneId (addressId)
        {
            addressId: 5000
        },
        // Variant 2: exactlyOneListId
        {
            addressListId: 100
        },
        // Variant 3: exactlyOneNewAddress (full address)
        {
            firstName: "John",
            lastName: "Smith",
            address1: "123 Main Street",
            address2: "Apt 4B",
            address3: "",
            city: "New York",
            state: "NY",
            zip: "10001",
            country: "USA",
            nickName: "Johnny",
            phoneNumber: "+1-555-123-4567"
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
                    year: 2025
                },
                cvv: 123
            }
        },
        // Variant 2: invoicePayment
        {
            invoiceDetails: {
                invoiceNumber: "INV-2024-001",
                amountDue: 150.00
            }
        },
        // Variant 3: achPayment
        {
            achDetails: {
                routingNumber: "021000021",
                accountNumber: "1234567890",
                checkDigit: 7
            }
        },
        // Variant 4: userCreditPayment
        {
            creditAmount: {
                amount: 50.00,
                currency: "USD"
            }
        },
        // Variant 5: applePayPayment
        {
            applePaymentDetails: {}
        },
        // Variant 6: googlePayPayment
        {
            googlePaymentDetails: {}
        }
    ]
};

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

    return value;
}

/**
 * Check if a value should be replaced
 */
function shouldReplaceValue(value, key) {
    // Always replace oneOf fields
    if (oneOfFixtures.hasOwnProperty(key)) {
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
        value === 'string' ||
        value === 'number'
    )) {
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
    } else if (keyLower.includes('id') && !keyLower.includes('email')) {
        return faker.string.alphanumeric(10);
    } else if (keyLower.includes('tags')) {
        return [faker.lorem.word(), faker.lorem.word()];
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
        return faker.finance.accountNumber();
    } else {
        // Default fallback
        return faker.lorem.word();
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
 * Process a single collection item (request)
 */
function processItem(item) {
    // Process request body
    if (item.request && item.request.body && item.request.body.raw) {
        try {
            const bodyObj = JSON.parse(item.request.body.raw);
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
            // Process response body
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