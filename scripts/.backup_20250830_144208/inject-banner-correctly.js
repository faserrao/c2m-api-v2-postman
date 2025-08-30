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

// Inject styles into head - find existing style tag and append
const styleEndTag = '</style>';
const lastStyleIndex = indexContent.lastIndexOf(styleEndTag);
if (lastStyleIndex !== -1) {
    indexContent = indexContent.substring(0, lastStyleIndex) + '\n' + bannerStyles + '\n' + indexContent.substring(lastStyleIndex);
}

// Now we need to inject the banner content AFTER Redoc renders
// We'll add a script that waits for Redoc to load and then inserts our content
const injectionScript = `
<script>
// Wait for Redoc to fully render
let attempts = 0;
const maxAttempts = 50;

function injectBanner() {
    attempts++;
    
    // Look for the API content area where we want to inject our banner
    const apiContent = document.querySelector('.api-content');
    const sectionContent = document.querySelector('[data-section-id="section/Authentication"]');
    const apiInfo = document.querySelector('.api-info');
    
    // Find the right container - Redoc uses different structures
    let targetContainer = null;
    
    if (apiContent) {
        targetContainer = apiContent;
    } else if (sectionContent && sectionContent.parentElement) {
        targetContainer = sectionContent.parentElement;
    } else if (apiInfo && apiInfo.parentElement) {
        targetContainer = apiInfo.parentElement;
    }
    
    if (targetContainer) {
        // Check if we already injected
        if (document.querySelector('.template-banner-wrapper')) {
            return;
        }
        
        // Create a container div for our content
        const bannerContainer = document.createElement('div');
        bannerContainer.innerHTML = \`${bannerBody.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`;
        
        // Find the API description or first section
        let insertBeforeElement = null;
        
        // Try to find the first operation or section
        const firstOperation = targetContainer.querySelector('[id^="operation/"]');
        const firstSection = targetContainer.querySelector('[data-section-id*="section/"]');
        
        if (firstOperation) {
            insertBeforeElement = firstOperation;
        } else if (firstSection) {
            insertBeforeElement = firstSection;
        }
        
        // Insert our banner content
        if (insertBeforeElement) {
            // Insert the wrapper
            const wrapper = bannerContainer.querySelector('.template-banner-wrapper');
            if (wrapper) {
                insertBeforeElement.parentElement.insertBefore(wrapper, insertBeforeElement);
            }
            
            // Insert the endpoints section
            const endpointsSection = bannerContainer.querySelector('.template-endpoints-section');
            if (endpointsSection) {
                insertBeforeElement.parentElement.insertBefore(endpointsSection, insertBeforeElement);
            }
        } else {
            // Fallback: append to the container
            const wrapper = bannerContainer.querySelector('.template-banner-wrapper');
            if (wrapper) {
                targetContainer.appendChild(wrapper);
            }
            
            const endpointsSection = bannerContainer.querySelector('.template-endpoints-section');
            if (endpointsSection) {
                targetContainer.appendChild(endpointsSection);
            }
        }
        
        console.log('Banner injected successfully!');
    } else if (attempts < maxAttempts) {
        // Try again in 100ms
        setTimeout(injectBanner, 100);
    } else {
        console.error('Could not find suitable container for banner after ' + maxAttempts + ' attempts');
    }
}

// Start injection when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(injectBanner, 500);
    });
} else {
    setTimeout(injectBanner, 500);
}
</script>
`;

// Inject the script before closing body tag
indexContent = indexContent.replace('</body>', injectionScript + '\n</body>');

// Write the modified index.html
fs.writeFileSync(indexPath, indexContent);
console.log('✅ Banner injection script added!');