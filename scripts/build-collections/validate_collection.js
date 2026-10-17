const { Collection } = require('postman-collection');
const fs = require('fs');

const filePath = process.argv[2];

if (!filePath) {
  console.error('❌ No collection file provided for validation.');
  process.exit(1);
}

try {
  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const collection = new Collection(data); // Validate the structure

  console.log(`✅ Collection ${filePath} is valid.`);

  // Diagnostic: Number of items
  console.log(`📦 Collection contains ${collection.items.count()} items.`);

  // Diagnostic: Warn if any item is missing a request
  collection.forEachItem(item => {
    if (!item.request) {
      console.warn(`⚠️  Item "${item.name}" has no request defined.`);
    }
  });
} catch (e) {
  console.error(`❌ Validation failed for ${filePath}:`, e.message);
  process.exit(1);
}

