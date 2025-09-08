# Documentation Directory

This directory contains the generated API documentation, templates, and assets for the C2M API. The documentation is auto-generated from the OpenAPI specification and served using multiple documentation tools.

## Directory Structure

```
docs/
├── index.html                      # Main documentation landing page
├── redoc.html                      # Redocly ReDoc documentation
├── swagger.html                    # Swagger UI documentation
├── api.md                          # Markdown API reference
├── swagger-initializer.js          # Swagger UI configuration
├── swagger.yaml                    # Local copy of OpenAPI spec
├── templates/                      # Documentation templates
│   ├── swagger-initializer.js.template
│   └── swagger.html.template
├── custom-redoc-template.hbs       # Custom Redoc template
├── template-endpoints-banner.html  # Banner for template endpoints
├── template-endpoints-quickstart.html # Quick start guide
├── swagger-ui-*.js                 # Swagger UI assets
├── swagger-ui.css                  # Swagger UI styles
├── index.css                       # Custom styles
├── index.js                        # Custom JavaScript
├── oauth2-redirect.html            # OAuth redirect handler
├── favicon-*.png                   # Favicons
└── various support files           # Additional assets
```

## Documentation Tools

### 1. Redocly ReDoc (`redoc.html`)

Interactive API documentation with a clean, responsive design.

**Features:**
- Three-panel responsive layout
- Code samples in multiple languages
- Search functionality
- Nested schema visualization
- Try-it-out functionality (configurable)

**Access:** http://localhost:8080/redoc.html

**Generation:**
```bash
make docs-build
```

### 2. Swagger UI (`swagger.html`)

Interactive API explorer with built-in testing capabilities.

**Features:**
- Try-it-out functionality
- Real-time request/response testing
- Authentication support
- Schema visualization
- Multiple server support

**Access:** http://localhost:8080/swagger.html

**Configuration:** Edit `swagger-initializer.js` to customize behavior

### 3. Markdown Documentation (`api.md`)

Plain text API reference for offline viewing or integration with other tools.

**Features:**
- Complete endpoint documentation
- Schema definitions
- Authentication details
- Examples in curl format

**Generation:**
```bash
# Generated automatically during docs-build
```

## Key Files

### `index.html`
Main landing page that provides:
- Links to different documentation formats
- API overview
- Quick start guide
- Authentication instructions

### `custom-redoc-template.hbs`
Handlebars template for customizing Redoc output:
- Custom branding
- Additional sections
- Modified layouts

### `swagger-initializer.js`
Configuration for Swagger UI:
```javascript
window.onload = function() {
  window.ui = SwaggerUIBundle({
    url: "./swagger.yaml",
    dom_id: '#swagger-ui',
    deepLinking: true,
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIStandalonePreset
    ],
    plugins: [
      SwaggerUIBundle.plugins.DownloadUrl
    ],
    layout: "StandaloneLayout"
  });
};
```

### Template Files

#### `template-endpoints-banner.html`
HTML banner emphasizing template endpoints as the recommended approach.

#### `template-endpoints-quickstart.html`
Quick start guide specifically for template endpoints with examples.

## Building Documentation

### Local Development
```bash
# Build all documentation formats
make docs-build

# Serve documentation locally
make docs-serve

# Access at http://localhost:8080
```

### Production Build
```bash
# Build for production
make docs-build-prod

# Deploy to GitHub Pages
make deploy-docs TARGET=github-pages

# Deploy to S3
make deploy-docs TARGET=s3
```

## Customization

### 1. Styling
Edit `index.css` for custom styles:
```css
/* Custom brand colors */
:root {
  --primary-color: #0066cc;
  --text-color: #333;
}
```

### 2. Redoc Theme
Configure in build command:
```bash
npx @redocly/cli build-docs openapi/spec.yaml \
  --theme.openapi.theme.colors.primary.main="#0066cc" \
  --theme.openapi.theme.typography.fontSize="16px"
```

### 3. Swagger UI Theme
Modify `swagger-initializer.js`:
```javascript
window.ui = SwaggerUIBundle({
  // ... other config
  theme: 'material',
  syntaxHighlight: {
    theme: 'monokai'
  }
});
```

## Documentation Features

### API Grouping
Endpoints are organized by:
- Authentication
- Template Endpoints (Recommended)
- Non-Template Endpoints
- PDF Processing

### Code Examples
Each endpoint includes examples in:
- cURL
- JavaScript
- Python
- Java
- Go
- Ruby
- PHP

### Authentication Guide
Comprehensive JWT authentication documentation:
- Token flow diagrams
- Step-by-step implementation
- Security best practices

### Interactive Elements
- Try-it-out console
- Request/response playground
- Schema explorer
- Search functionality

## Deployment

### GitHub Pages
```bash
make deploy-docs TARGET=github-pages
```
Deploys to: https://[username].github.io/[repo]/

### AWS S3
```bash
make deploy-docs TARGET=s3 S3_BUCKET=my-docs-bucket
```

### Netlify
```bash
make deploy-docs TARGET=netlify
```

### Local Preview
```bash
make docs-serve
# OR
cd docs && python -m http.server 8080
```

## Maintenance

### Updating Documentation
1. Modify OpenAPI spec: `openapi/c2mapiv2-openapi-spec-final.yaml`
2. Rebuild docs: `make docs-build`
3. Test locally: `make docs-serve`
4. Deploy: `make deploy-docs`

### Adding Custom Content
1. Edit templates in `templates/` directory
2. Add content to `index.html`
3. Update styles in `index.css`

### Troubleshooting

**Issue: Docs not updating**
- Clear browser cache
- Run `make docs-clean` then `make docs-build`

**Issue: Swagger UI not loading**
- Check `swagger.yaml` exists
- Verify `swagger-initializer.js` paths

**Issue: Redoc errors**
- Validate OpenAPI spec: `make openapi-validate`
- Check for circular references

## Best Practices

1. **Version Documentation**: Tag releases for documentation versions
2. **Test Locally**: Always preview before deploying
3. **Optimize Assets**: Minimize JS/CSS for production
4. **Monitor Analytics**: Track documentation usage
5. **Update Examples**: Keep code samples current

## Related Resources

- [Redocly CLI Documentation](https://redocly.com/docs/cli/)
- [Swagger UI Documentation](https://swagger.io/tools/swagger-ui/)
- [OpenAPI Specification](../openapi/README.md)
- [Root README](../README.md#documentation)