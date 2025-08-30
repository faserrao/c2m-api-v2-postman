const fs = require('fs');
const path = require('path');

// Read the generated index.html
const indexPath = path.join(__dirname, '../docs/index.html');
let indexContent = fs.readFileSync(indexPath, 'utf8');

// Read the banner HTML
const bannerPath = path.join(__dirname, '../docs/template-endpoints-banner.html');
const bannerContent = fs.readFileSync(bannerPath, 'utf8');

// Extract just the styles and body content from banner
const styleMatch = bannerContent.match(/<style>([\s\S]*?)<\/style>/);
const bodyMatch = bannerContent.match(/<body>([\s\S]*?)<\/body>/);

if (!styleMatch || !bodyMatch) {
    console.error('Could not extract styles or body from banner HTML');
    process.exit(1);
}

const bannerStyles = styleMatch[1];
const bannerBody = bodyMatch[1];

// Inject styles into head
indexContent = indexContent.replace('</style>', `${bannerStyles}\n</style>`);

// Find where Redoc content starts - look for the opening of the redoc app
// Redoc usually has a pattern like <div id="redoc">
let injectionPoint = indexContent.indexOf('<div id="redoc">');
if (injectionPoint === -1) {
    // Try another pattern
    injectionPoint = indexContent.indexOf('<redoc');
}

if (injectionPoint !== -1) {
    // Insert the banner content right after the body tag opens
    const bodyTagEnd = indexContent.indexOf('<body>') + '<body>'.length;
    const beforeBody = indexContent.substring(0, bodyTagEnd);
    const afterBody = indexContent.substring(bodyTagEnd);
    
    // Insert banner at the very beginning of body
    indexContent = beforeBody + '\n' + bannerBody + '\n' + afterBody;
} else {
    console.error('Could not find suitable injection point');
    process.exit(1);
}

// Write the modified index.html
fs.writeFileSync(indexPath, indexContent);
console.log('✅ Banner injected successfully!');