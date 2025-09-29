#!/usr/bin/env node
/**
 * fix_oneOf_placeholders.js
 * 
 * Post-processes a Postman collection to replace type placeholders for oneOf fields
 * with <oneOf> to better indicate that these fields can accept multiple types.
 * 
 * This addresses the limitation of openapi-to-postmanv2 which simplifies oneOf
 * schemas to just their first type.
 */

const fs = require('fs');
const path = require('path');

/**
 * Known oneOf fields in the C2M API
 * These fields should have <oneOf> instead of type-specific placeholders
 */
const oneOfFields = {
    // Primary oneOf fields
    'documentSourceIdentifier': true,
    'recipientAddressSource': true,
    'paymentDetails': true,
    
    // Note: We could also detect nested oneOf fields if needed
};

/**
 * Parse command line arguments
 */
function parseArgs() {
    const args = process.argv.slice(2);
    
    if (args.length < 2) {
        console.error('Usage: node fix_oneOf_placeholders.js <input-file> <output-file>');
        process.exit(1);
    }
    
    return {
        input: args[0],
        output: args[1]
    };
}

/**
 * Process a value to replace oneOf field placeholders
 */
function processValue(value, key) {
    // Check if this key is a known oneOf field
    if (!oneOfFields[key]) {
        return value;
    }
    
    // If the value is a placeholder string, replace it with <oneOf>
    if (typeof value === 'string' && (
        value === '<string>' ||
        value === '<integer>' ||
        value === '<number>' ||
        value === '<boolean>' ||
        value === '<object>' ||
        value === '<array>' ||
        value.startsWith('"<') && value.endsWith('>"')
    )) {
        return '<oneOf>';
    }
    
    // If it's already a complex object/array, leave it as is
    // (this might happen if examples were already added)
    return value;
}

/**
 * Recursively process an object to fix oneOf placeholders
 */
function processObject(obj, parentKey = '') {
    if (!obj || typeof obj !== 'object') {
        return obj;
    }
    
    // Handle arrays
    if (Array.isArray(obj)) {
        return obj.map((item, index) => processObject(item, parentKey));
    }
    
    // Handle objects
    const result = {};
    for (const [key, value] of Object.entries(obj)) {
        // Check if this value should be replaced
        const processedValue = processValue(value, key);
        
        // Recursively process nested objects/arrays
        if (processedValue !== '<oneOf>' && typeof processedValue === 'object') {
            result[key] = processObject(processedValue, key);
        } else {
            result[key] = processedValue;
        }
    }
    
    return result;
}

/**
 * Process a raw body string (JSON in a string)
 */
function processRawBody(rawStr) {
    if (!rawStr || typeof rawStr !== 'string') {
        return rawStr;
    }
    
    try {
        // Parse the JSON
        const bodyObj = JSON.parse(rawStr);
        
        // Process the object
        const processed = processObject(bodyObj);
        
        // Convert back to formatted JSON string
        return JSON.stringify(processed, null, 2);
    } catch (e) {
        // If parsing fails, return original
        console.warn('Warning: Could not parse raw body as JSON');
        return rawStr;
    }
}

/**
 * Process a single collection item (request)
 */
function processItem(item) {
    // Process request body
    if (item.request && item.request.body && item.request.body.raw) {
        item.request.body.raw = processRawBody(item.request.body.raw);
    }
    
    // Process response examples
    if (item.response && Array.isArray(item.response)) {
        item.response.forEach(response => {
            // Process response body
            if (response.body) {
                response.body = processRawBody(response.body);
            }
            
            // Process originalRequest in responses
            if (response.originalRequest && response.originalRequest.body && response.originalRequest.body.raw) {
                response.originalRequest.body.raw = processRawBody(response.originalRequest.body.raw);
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
        // Read the collection
        console.log(`Reading collection from: ${options.input}`);
        const collectionData = fs.readFileSync(options.input, 'utf8');
        const collection = JSON.parse(collectionData);
        
        console.log(`Processing collection: ${collection.info ? collection.info.name : 'Unnamed'}`);
        
        // Count replacements
        let replacementCount = 0;
        const originalData = JSON.stringify(collection);
        
        // Process all items in the collection
        if (collection.item && Array.isArray(collection.item)) {
            collection.item.forEach(item => processItem(item));
        }
        
        // Count how many replacements were made
        const newData = JSON.stringify(collection);
        const matches = newData.match(/<oneOf>/g);
        replacementCount = matches ? matches.length : 0;
        
        // Write the output
        fs.writeFileSync(options.output, JSON.stringify(collection, null, 2));
        console.log(`✅ Processed collection written to: ${options.output}`);
        console.log(`📊 Replaced ${replacementCount} oneOf placeholders`);
        
        // Show which fields were found
        if (replacementCount > 0) {
            console.log('\nOneOf fields found in the collection:');
            Object.keys(oneOfFields).forEach(field => {
                if (newData.includes(`"${field}"`) && newData.includes('<oneOf>')) {
                    console.log(`- ${field}`);
                }
            });
        }
        
    } catch (error) {
        console.error('Error processing collection:', error.message);
        process.exit(1);
    }
}

// Run the script
main();