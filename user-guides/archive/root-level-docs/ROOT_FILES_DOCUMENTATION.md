# Root Directory Files Documentation

This document describes the purpose of each non-directory file in the root of the C2M API v2 repository.

## Configuration Files

### Environment Configuration
- **.env** - Contains actual API keys and environment-specific configurations (Postman API keys). Never committed to version control.
- **.env.example** - Template showing required environment variables without exposing sensitive data. Helps developers set up their local environment.

### Git Configuration
- **.gitattributes** - Defines Git merge strategy for .gitignore file (merge=union) to prevent conflicts.
- **.gitignore** - Lists files/patterns Git should ignore. Includes environment files, dependencies, Python artifacts, OS files, editor files, logs, build artifacts, and sensitive data.
- **.gitignore-updated** - Improved version of .gitignore with better organization and structure.

### Tool Configuration
- **.postman-target** - Specifies which Postman workspace to target ("team" vs personal). Used by Makefile.
- **.redocly.yaml** - Configuration for Redocly documentation tool. Specifies OpenAPI file location, theme settings, and linting rules.
- **.spectral.yml** - Configuration for Spectral OpenAPI linter. Defines style rules for API paths and requires operation descriptions/summaries.
- **openapitools.json** - Configuration for OpenAPI Generator CLI. Specifies generator version (7.15.0).
- **sdk-config.yaml** - Defines SDK generation settings for multiple languages (Python, JavaScript, TypeScript, Java, Go, Ruby, PHP).

## Documentation

- **EXECUTIVE_SUMMARY.md** - High-level project overview for stakeholders. Details key deliverables, business value, technical innovation, and next steps.
- **LICENSE** - MIT License defining project licensing terms.
- **README.md** - Main project documentation index. Organized links to categorized documentation serving as primary navigation hub.

## Build and Development

- **Makefile** - Central automation hub for the entire project. 100+ lines defining targets for EBNF→OpenAPI conversion, Postman integration, testing, and deployment.
- **package.json** - Node.js project configuration. Contains scripts for linting/docs and dependencies for API tooling.
- **package-lock.json** - Locks exact versions of Node.js dependencies for reproducible builds.

## Testing and Mocking

- **prism_test_body.json** - Test data for Prism mock server (currently empty placeholder).
- **test-output.yaml** - Sample/test OpenAPI specification output used for testing EBNF to OpenAPI conversion.

## Assets

- **click2mail-header-logo.webp** - Company logo for documentation and branding purposes.

## Version Control and Patches

- **minimal-auth-patch.diff** - Git patch file for minimal authentication integration. Shows modifications to Makefile for adding auth provider scripts.

## Utilities

- **verify-restoration.sh** - Shell script to verify project restoration after major changes. Checks Makefile size, presence of required scripts, and absence of misplaced files.

## System Files

- **.DS_Store** - macOS system file storing folder display preferences (not project-specific, should remain in .gitignore).

## Project Architecture Summary

The root directory files form a comprehensive build and deployment system that:
- Automates the workflow: **EBNF → OpenAPI → Postman → Mock Server → Tests → Documentation**
- Provides extensive configuration for multiple tools
- Ensures security through proper environment variable handling
- Maintains code quality through linting and validation
- Enables multi-language SDK generation
- Supports both local development and CI/CD pipelines

The Makefile serves as the central orchestration point for the entire system.