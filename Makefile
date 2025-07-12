# Makefile for C2M API Testing Toolkit

# Environment variables
ENV_FILE = .env
SWAGGER_JSON = swagger.yaml
REDOC_HTML = redoc.html
TESTS_DIR = tests

# Tasks
.PHONY: install test build docs clean

# Install dependencies for all components
install:
	@echo "Installing dependencies..."
	@pip install -r tests/python-cli/requirements.txt
	@npm install --prefix tests/typescript-cli
	@echo "Dependencies installed!"

# Run tests using the Python CLI
test:
	@echo "Running Python CLI tests..."
	@python tests/python-cli/cli.py --env dev
	@echo "Python tests complete."

	@echo "Running TypeScript CLI tests..."
	@npm run start --prefix tests/typescript-cli -- --env dev
	@echo "TypeScript tests complete."

# Build documentation for Swagger UI and ReDoc
docs:
	@echo "Building Swagger UI docs..."
	@npm run build --prefix github-template
	@echo "Swagger docs built."

	@echo "Building ReDoc docs..."
	@cp github-template/dist/swagger.json $(REDOC_HTML)
	@echo "ReDoc docs built."

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -rf node_modules
	@rm -rf tests/python-cli/__pycache__
	@rm -rf tests/typescript-cli/node_modules
	@rm -f $(REDOC_HTML)
	@echo "Clean complete."

# SDK generation (requires openapi-generator-cli installed)
sdk-python:
	npx @openapitools/openapi-generator-cli generate -i ./docs/c2m_openapi_spec_final.yaml -g python -o sdk/python

sdk-typescript:
	npx @openapitools/openapi-generator-cli generate -i ./docs/c2m_openapi_spec_final.yaml -g typescript-axios -o sdk/typescript

sdk-all: sdk-python sdk-typescript

docs-deploy:
	git add ./docs
	git commit -m "Update docs"
	git push

deploy-all: sdk-all docs-deploy
