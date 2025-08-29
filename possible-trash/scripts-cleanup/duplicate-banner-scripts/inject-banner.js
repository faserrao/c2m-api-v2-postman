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
indexContent = indexContent.replace('</head>', `<style>${bannerStyles}</style>\n</head>`);

// Add a script to inject the banner after Redoc renders
const injectionScript = `
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Wait for Redoc to render
    const checkInterval = setInterval(function() {
        // Look for the API info section
        const apiInfo = document.querySelector('.api-info');
        const apiContent = document.querySelector('.api-content');
        
        if (apiInfo || apiContent) {
            clearInterval(checkInterval);
            
            // Create a container for our banner
            const bannerContainer = document.createElement('div');
            bannerContainer.innerHTML = \`${bannerBody.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`;
            
            // Find the right place to insert
            let insertTarget = apiInfo || apiContent;
            
            // If we have api-info, insert after it
            if (apiInfo && apiInfo.parentElement) {
                // Insert the wrapper div content
                const wrapper = bannerContainer.querySelector('.template-banner-wrapper');
                if (wrapper) {
                    apiInfo.parentElement.insertBefore(wrapper, apiInfo.nextSibling);
                }
                
                // Insert the endpoints section
                const endpointsSection = bannerContainer.querySelector('.template-endpoints-section');
                if (endpointsSection) {
                    apiInfo.parentElement.insertBefore(endpointsSection, wrapper.nextSibling);
                }
            }
        }
    }, 100);
    
    // Stop checking after 5 seconds
    setTimeout(function() {
        clearInterval(checkInterval);
    }, 5000);
});
</script>
`;

indexContent = indexContent.replace('</body>', injectionScript + '</body>');

// Write the modified index.html
fs.writeFileSync(indexPath, indexContent);
console.log('✅ Banner injected successfully!');