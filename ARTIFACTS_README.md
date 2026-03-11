# C2M API Artifacts

This repository contains automatically generated artifacts from the [c2m-api-v2-postman](https://github.com/faserrao/c2m-api-v2-postman).

## ⚠️ Do Not Edit These Files

All files in this repository are automatically generated. Any manual changes will be overwritten by the next build.

To make changes, please edit the source files in [c2m-api-v2-postman](https://github.com/faserrao/c2m-api-v2-postman).

## Repository Structure

- `openapi/` - Generated OpenAPI specifications
- `postman/` - Postman collections and metadata
- `docs/` - API documentation
- `sdks/` - Generated client SDKs

## Build Status

Latest build: See [GitHub Actions](https://github.com/faserrao/c2m-api-v2-postman/actions)

## Generated Files

### OpenAPI Specifications
- `openapi/c2mapiv2-openapi-spec-base.yaml` - Base spec generated from EBNF
- `openapi/c2mapiv2-openapi-spec-final.yaml` - Final spec with auth overlay applied
- `openapi/bundled.yaml` - Dereferenced version for tools that need inline schemas

### Postman Collections
- `postman/collections/` - Generated Postman collections
- `postman/metadata/` - Postman IDs, mock URLs, and configuration

### Documentation
- `docs/index.html` - Redocly ReDoc documentation (clean, responsive)
- `docs/elements.html` - Stoplight Elements documentation (best-in-class Try It)
- `docs/swagger.html` - Swagger UI documentation (traditional interactive)
- `docs/api.md` - Markdown API reference (offline viewing)

### SDKs
- `sdks/python/` - Python client library
- `sdks/javascript/` - JavaScript/Node.js client library
- `sdks/typescript/` - TypeScript client library
- Additional languages as configured

## Usage

### Accessing Documentation

**GitHub Pages (Live):**
- **Redocly ReDoc**: https://faserrao.github.io/c2m-api-v2-postman-artifacts/index.html
- **Stoplight Elements**: https://faserrao.github.io/c2m-api-v2-postman-artifacts/elements.html
- **Swagger UI**: https://faserrao.github.io/c2m-api-v2-postman-artifacts/swagger.html

**Local:**
Clone the repository and open any of the HTML files in `docs/`

### Using SDKs
Each SDK directory contains its own README with installation and usage instructions.

### Getting OpenAPI Spec
```bash
# Latest spec (from artifacts repo)
curl https://raw.githubusercontent.com/faserrao/c2m-api-v2-postman-artifacts/main/openapi/c2mapiv2-openapi-spec-final.yaml

# Or from main repo
curl https://raw.githubusercontent.com/faserrao/c2m-api-v2-postman/main/openapi/c2mapiv2-openapi-spec-final.yaml
```

## License

See [c2m-api-v2-postman](https://github.com/faserrao/c2m-api-v2-postman) for license information.
