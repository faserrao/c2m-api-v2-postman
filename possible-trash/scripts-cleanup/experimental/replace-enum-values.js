#!/usr/bin/env node

/**
 * Replace enum values in Postman collection with placeholders
 * This script finds fields that have enum constraints and replaces
 * their example values with <enum:fieldName> placeholders
 */

const fs = require('fs');
const path = require('path');

// Read OpenAPI spec to get enum definitions
function getEnumFields(openapiPath) {
    const spec = JSON.parse(fs.readFileSync(openapiPath, 'utf8'));
    const enumFields = {};
    
    // Traverse the components/schemas to find enum fields
    function findEnums(obj, prefix = '') {
        for (const [key, value] of Object.entries(obj)) {
            if (value && typeof value === 'object') {
                if (value.enum && Array.isArray(value.enum)) {
                    enumFields[key] = value.enum;
                } else if (value.properties) {
                    findEnums(value.properties, prefix);
                } else if (value.type === 'object') {
                    findEnums(value, prefix);
                }
            }
        }
    }
    
    if (spec.components && spec.components.schemas) {
        findEnums(spec.components.schemas);
    }
    
    return enumFields;
}

// Replace enum values in collection
function replaceEnumValues(collection, enumFields) {
    // Process each item recursively
    function processItem(item) {
        if (item.item && Array.isArray(item.item)) {
            item.item.forEach(processItem);
        }
        
        if (item.request && item.request.body && item.request.body.raw) {
            try {
                let body = JSON.parse(item.request.body.raw);
                body = replaceInObject(body, enumFields);
                item.request.body.raw = JSON.stringify(body, null, 2);
            } catch (e) {
                console.warn('Could not parse body for:', item.name);
            }
        }
    }
    
    function replaceInObject(obj, enumFields) {
        if (Array.isArray(obj)) {
            return obj.map(item => replaceInObject(item, enumFields));
        } else if (obj && typeof obj === 'object') {
            const newObj = {};
            for (const [key, value] of Object.entries(obj)) {
                if (enumFields[key] && enumFields[key].includes(value)) {
                    // Replace enum value with placeholder
                    newObj[key] = `<enum:${key}>`;
                } else {
                    newObj[key] = replaceInObject(value, enumFields);
                }
            }
            return newObj;
        }
        return obj;
    }
    
    collection.item.forEach(processItem);
    return collection;
}

// Main function
function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 3) {
        console.error('Usage: node replace-enum-values.js <openapi-spec> <input-collection> <output-collection>');
        process.exit(1);
    }
    
    const [openapiPath, inputPath, outputPath] = args;
    
    try {
        // Get enum fields from OpenAPI spec
        const enumFields = getEnumFields(openapiPath);
        console.log('Found enum fields:', Object.keys(enumFields));
        
        // Read and process collection
        const collection = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
        const updatedCollection = replaceEnumValues(collection, enumFields);
        
        // Write updated collection
        fs.writeFileSync(outputPath, JSON.stringify(updatedCollection, null, 2));
        console.log(`Updated collection written to: ${outputPath}`);
        
    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}