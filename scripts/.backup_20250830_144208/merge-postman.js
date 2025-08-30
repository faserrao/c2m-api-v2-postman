const fs = require('fs');

// Read the input files
const collectionPath = process.argv[2];
const overridesPath = process.argv[3];

const collection = JSON.parse(fs.readFileSync(collectionPath, 'utf8'));
const overrides = JSON.parse(fs.readFileSync(overridesPath, 'utf8'));

// Deep merge function
function deepMerge(target, source) {
  // If the target is an array and the source is also an array, concatenate them
  if (Array.isArray(target) && Array.isArray(source)) {
    return [...target, ...source];
  }

  // If both are objects, perform a deep merge
  if (typeof target === 'object' && typeof source === 'object') {
    let merged = { ...target };

    for (const key in source) {
      if (source.hasOwnProperty(key)) {
        // If the target doesn't exist or is not an object, use the source value
        if (!merged[key] || typeof merged[key] !== 'object') {
          merged[key] = source[key];
        } else {
          // Otherwise, recursively merge the objects
          merged[key] = deepMerge(merged[key], source[key]);
        }
      }
    }
    return merged;
  }

  // Otherwise, just return the source value (default overwrite behavior)
  return source;
}

// Deeply merge the collection and overrides
const merged = deepMerge(collection, overrides);

// Output the merged result
console.log(JSON.stringify(merged, null, 2));
