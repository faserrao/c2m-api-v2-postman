#!/bin/bash

# Create directory structure
mkdir -p \
  .github/workflows \
  docs \
  openapi \
  postman \
  resources/example_requests \
  resources/example_responses \
  scripts \
  sdk-clients/javascript \
  sdk-clients/python \
  tests/contract \
  tests/integration

# Touch placeholder files
touch \
  .github/template.yml \
  .github/workflows/deploy-docs.yml \
  .github/workflows/preview-docs.yml \
  .spectral.yml \
  .redocly.yaml \
  openapi/lob_openapi_spec_final.yaml \
  docs/index.html \
  docs/logo.png \
  docs/banner.png \
  docs/favicon.ico \
  postman/README.md \
  resources/example_requests/example_request.json \
  resources/example_responses/example_response.json \
  scripts/deploy-docs.sh \
  scripts/generate-postman.sh \
  scripts/generate-sdk.sh \
  sdk-clients/README.md \
  sdk-clients/javascript/README.md \
  sdk-clients/python/README.md \
  tests/README.md \
  tests/contract/validate_against_spec.js \
  tests/integration/postman_tests.json

# Create main documentation and config files
cat <<EOF > README.md
# Click2Mail API

This repo contains the OpenAPI spec, Postman tests, SDKs, and documentation
for the Click2Mail API — modeled in the style of Lob's public API.
EOF

cat <<EOF > CONTRIBUTING.md
# Contributing

Thanks for helping improve this repo! Please follow standard pull request flow
and run all checks locally before submitting.
EOF

cat <<EOF > LICENSE
MIT License
...
EOF

cat <<EOF > my-commands.sh
#!/bin/bash
# Helper script for common tasks
npx spectral lint openapi/lob_openapi_spec_final.yaml
npm run build-docs
EOF

chmod +x my-commands.sh

echo "✅ Directory structure and placeholder files created."
