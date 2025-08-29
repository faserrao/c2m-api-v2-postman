const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

// Read the OpenAPI spec
const specPath = path.join(__dirname, '../openapi/c2mapiv2-openapi-spec-final.yaml');
const spec = yaml.load(fs.readFileSync(specPath, 'utf8'));

// Read the banner HTML
const bannerPath = path.join(__dirname, '../docs/template-endpoints-banner.html');
const bannerContent = fs.readFileSync(bannerPath, 'utf8');

// Extract just the body content from banner (without DOCTYPE, html, head tags)
const bodyMatch = bannerContent.match(/<body>([\s\S]*?)<\/body>/);
if (!bodyMatch) {
    console.error('Could not extract body from banner HTML');
    process.exit(1);
}

const bannerBody = bodyMatch[1];

// Create the enhanced description with the banner HTML
const enhancedDescription = `
${bannerBody}

---

API for submitting documents with various routing options
`;

// Update the spec
spec.info.description = enhancedDescription;

// Write the modified spec to a temporary file
const tempSpecPath = path.join(__dirname, '../openapi/c2mapiv2-openapi-spec-with-banner.yaml');
fs.writeFileSync(tempSpecPath, yaml.dump(spec, { lineWidth: -1 }));

console.log('✅ Banner added to OpenAPI spec!');