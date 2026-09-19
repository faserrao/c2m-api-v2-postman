#!/usr/bin/env node
/**
 * fix_oneOf_placeholders.js
 *
 * Post-processes a Postman collection to replace type placeholders for oneOf fields
 * with <oneOf> to better indicate that these fields can accept multiple types.
 *
 * This script dynamically discovers oneOf fields from the OpenAPI spec instead of
 * using a hardcoded list, making it resilient to schema changes.
 *
 * Usage: node fix_oneOf_placeholders.js <openapi-spec> <input-collection> <output-collection>
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

/**
 * Parse command line arguments
 */
function parseArgs() {
    const args = process.argv.slice(2);

    if (args.length < 3) {
        console.error('Usage: node fix_oneOf_placeholders.js <openapi-spec> <input-collection> <output-collection>');
        console.error('');
        console.error('Arguments:');
        console.error('  openapi-spec      Path to OpenAPI YAML specification');
        console.error('  input-collection  Path to input Postman collection JSON');
        console.error('  output-collection Path to output Postman collection JSON');
        process.exit(1);
    }

    return {
        spec: args[0],
        input: args[1],
        output: args[2]
    };
}

/**
 * Discover oneOf fields and cross-field constraints from OpenAPI spec.
 * Returns { oneOfFields: Set, crossFieldRules: Array }
 */
function discoverOneOfFields(specPath) {
    console.log(`Reading OpenAPI spec from: ${specPath}`);

    try {
        // Read and parse OpenAPI spec
        const specContent = fs.readFileSync(specPath, 'utf8');
        const spec = yaml.load(specContent);

        const oneOfFields = new Set();

        // Traverse components/schemas to find oneOf definitions
        if (spec.components && spec.components.schemas) {
            const schemas = spec.components.schemas;

            for (const [schemaName, schemaDefinition] of Object.entries(schemas)) {
                // Check if this schema has a oneOf
                if (schemaDefinition.oneOf) {
                    oneOfFields.add(schemaName);
                }

                // Check properties for nested oneOf
                if (schemaDefinition.properties) {
                    for (const [propName, propDef] of Object.entries(schemaDefinition.properties)) {
                        if (propDef.oneOf) {
                            oneOfFields.add(propName);
                        }
                    }
                }
            }
        }

        console.log(`Discovered ${oneOfFields.size} oneOf fields from OpenAPI spec:`);
        Array.from(oneOfFields).sort().forEach(field => {
            console.log(`  - ${field}`);
        });

        // Load cross-field jobOptions constraints from spec info
        const crossFieldRules = (spec.info && spec.info['x-valid-combinations']) || [];
        if (crossFieldRules.length > 0) {
            console.log(`Loaded ${crossFieldRules.length} cross-field constraints from spec`);
        }

        // Build ph<val1|val2|...> placeholder map for jobOptions enum properties.
        // json-schema-faker picks a random concrete value for each enum-constrained
        // field; fix_oneOf only handles oneOf schemas so these slip through.
        // Format contract: ph<val1|val2|...> — see addRandomDataToRaw.js (HC6) which
        // resolves these to a concrete value, and diff_collections.py which recognises them.
        const enumPlaceholders = {};
        const joSchema = spec.components &&
                         spec.components.schemas &&
                         spec.components.schemas.jobOptions;
        if (joSchema && joSchema.properties) {
            for (const [propName, propDef] of Object.entries(joSchema.properties)) {
                if (Array.isArray(propDef.enum) && propDef.enum.length > 0) {
                    enumPlaceholders[propName] = `ph<${propDef.enum.join('|')}>`;
                }
            }
            console.log(`Discovered ${Object.keys(enumPlaceholders).length} jobOptions enum placeholders`);
        }

        // HC3: derive job array field names from spec at runtime (type: array schemas
        // whose names contain "Job") instead of a hardcoded list.
        const jobArrayFields = Object.entries(
            (spec.components && spec.components.schemas) || {}
        ).filter(([name, schema]) => schema.type === 'array' && /Job/.test(name))
         .map(([name]) => name);
        console.log(`Discovered ${jobArrayFields.length} job array fields from spec: ${jobArrayFields.join(', ')}`);

        return { oneOfFields, crossFieldRules, enumPlaceholders, jobArrayFields };

    } catch (error) {
        console.error(`Error reading OpenAPI spec: ${error.message}`);
        process.exit(1);
    }
}

/**
 * Process a value to replace oneOf field placeholders
 */
function processValue(value, key, oneOfFields) {
    // Check if this key is a known oneOf field
    if (!oneOfFields.has(key)) {
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

    // If it's an object or array, also replace with <oneOf>
    // openapi-to-postmanv2 sometimes generates full objects for oneOf fields
    if (typeof value === 'object' && value !== null) {
        // Check if this looks like a generated placeholder object
        // (has placeholder values like "<string>", "<integer>")
        const jsonStr = JSON.stringify(value);
        if (jsonStr.includes('"<string>"') ||
            jsonStr.includes('"<integer>"') ||
            jsonStr.includes('"<number>"') ||
            jsonStr.includes('"<boolean>"')) {
            return '<oneOf>';
        }
    }

    // If it's already a complex object with real data, leave it as is
    // (this means examples were already added by the test data generator)
    return value;
}

/**
 * Recursively process an object to fix oneOf placeholders
 * replacedFields: Set that collects field names actually changed to <oneOf>
 */
function processObject(obj, oneOfFields, replacedFields, parentKey = '') {
    if (!obj || typeof obj !== 'object') {
        return obj;
    }

    // Handle arrays
    if (Array.isArray(obj)) {
        return obj.map((item) => processObject(item, oneOfFields, replacedFields, parentKey));
    }

    // Handle objects
    const result = {};
    for (const [key, value] of Object.entries(obj)) {
        // Check if this value should be replaced
        const processedValue = processValue(value, key, oneOfFields);

        // Track actual replacements (value changed to <oneOf>)
        if (processedValue === '<oneOf>' && value !== '<oneOf>') {
            replacedFields.add(key);
        }

        // Recursively process nested objects/arrays
        if (processedValue !== '<oneOf>' && typeof processedValue === 'object') {
            result[key] = processObject(processedValue, oneOfFields, replacedFields, key);
        } else {
            result[key] = processedValue;
        }
    }

    return result;
}

// HC3: JOB_ARRAY_FIELDS is now derived from the spec inside discoverOneOfFields()
// and threaded through to processRawBody via jobArrayFields. Removed hardcoded list.

/**
 * Replace actual enum values in jobOptions with ph<val1|val2|...> placeholders.
 * Skips values already in placeholder notation (start with '<' or 'ph<').
 */
function convertJobOptionsToPlaceholders(bodyObj, enumPlaceholders) {
    if (!bodyObj || !bodyObj.jobOptions ||
        !enumPlaceholders || Object.keys(enumPlaceholders).length === 0) return;
    const jo = bodyObj.jobOptions;
    for (const [prop, placeholder] of Object.entries(enumPlaceholders)) {
        if (jo[prop] !== undefined && typeof jo[prop] === 'string' &&
            !jo[prop].startsWith('<') && !jo[prop].startsWith('ph<')) {
            jo[prop] = placeholder;
        }
    }
}

/**
 * Enforce x-valid-combinations rules on jobOptions.
 * When a triggering field value is present and the constrained field violates the rule,
 * reset the constrained field to the first allowed value.
 */
function fixCrossFieldConstraints(bodyObj, rules) {
    if (!bodyObj || !bodyObj.jobOptions || !rules || rules.length === 0) return;
    const jo = bodyObj.jobOptions;
    for (const rule of rules) {
        const { when_field, when_value, then_field, then_values } = rule;
        if (jo[when_field] === when_value && jo[then_field] !== undefined && !then_values.includes(jo[then_field])) {
            jo[then_field] = then_values[0];
        }
    }
}

/**
 * Process a raw body string (JSON in a string)
 */
function processRawBody(rawStr, oneOfFields, replacedFields, crossFieldRules, enumPlaceholders, jobArrayFields) {
    if (!rawStr || typeof rawStr !== 'string') {
        return rawStr;
    }

    try {
        // Parse the JSON
        const bodyObj = JSON.parse(rawStr);

        // Process the object
        const processed = processObject(bodyObj, oneOfFields, replacedFields);

        // Trim job arrays to 1 example item (faker generates 2 identical items by default)
        for (const field of (jobArrayFields || [])) {
            if (Array.isArray(processed[field]) && processed[field].length > 1) {
                processed[field] = processed[field].slice(0, 1);
            }
        }

        // Enforce cross-field jobOptions constraints (rules from spec x-valid-combinations)
        fixCrossFieldConstraints(processed, crossFieldRules);

        // Replace concrete enum values in jobOptions with ph<...> type placeholders
        convertJobOptionsToPlaceholders(processed, enumPlaceholders);

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
function processItem(item, oneOfFields, replacedFields, crossFieldRules, enumPlaceholders, jobArrayFields) {
    // Process request body
    if (item.request && item.request.body && item.request.body.raw) {
        item.request.body.raw = processRawBody(item.request.body.raw, oneOfFields, replacedFields, crossFieldRules, enumPlaceholders, jobArrayFields);
    }

    // Process response examples
    if (item.response && Array.isArray(item.response)) {
        item.response.forEach(response => {
            // Process response body
            if (response.body) {
                response.body = processRawBody(response.body, oneOfFields, replacedFields, crossFieldRules, enumPlaceholders, jobArrayFields);
            }

            // Process originalRequest in responses
            if (response.originalRequest && response.originalRequest.body && response.originalRequest.body.raw) {
                response.originalRequest.body.raw = processRawBody(response.originalRequest.body.raw, oneOfFields, replacedFields, crossFieldRules, enumPlaceholders, jobArrayFields);
            }
        });
    }

    // Recursively process sub-items (folders)
    if (item.item && Array.isArray(item.item)) {
        item.item.forEach(subItem => processItem(subItem, oneOfFields, replacedFields, crossFieldRules, enumPlaceholders, jobArrayFields));
    }
}

/**
 * Main execution
 */
function main() {
    const options = parseArgs();

    try {
        // Step 1: Discover oneOf fields, cross-field constraints, enum placeholders, and job array fields
        const { oneOfFields, crossFieldRules, enumPlaceholders, jobArrayFields } = discoverOneOfFields(options.spec);

        if (oneOfFields.size === 0) {
            console.warn('Warning: No oneOf fields discovered in OpenAPI spec');
        }

        // Step 2: Read the collection
        console.log(`\nReading collection from: ${options.input}`);
        const collectionData = fs.readFileSync(options.input, 'utf8');
        const collection = JSON.parse(collectionData);

        console.log(`Processing collection: ${collection.info ? collection.info.name : 'Unnamed'}`);

        // Step 3: Process all items in the collection, tracking actual replacements
        const replacedFields = new Set();
        if (collection.item && Array.isArray(collection.item)) {
            collection.item.forEach(item => processItem(item, oneOfFields, replacedFields, crossFieldRules, enumPlaceholders, jobArrayFields));
        }

        // Step 4: Write the output
        fs.writeFileSync(options.output, JSON.stringify(collection, null, 2));
        console.log(`\nProcessed collection written to: ${options.output}`);
        console.log(`Replaced ${replacedFields.size} oneOf field(s)`);

        // Show which fields were actually replaced
        if (replacedFields.size > 0) {
            console.log('\nOneOf fields replaced in the collection:');
            Array.from(replacedFields).sort().forEach(field => {
                console.log(`  - ${field}`);
            });
        }

    } catch (error) {
        console.error('Error processing collection:', error.message);
        process.exit(1);
    }
}

// Run the script
main();
