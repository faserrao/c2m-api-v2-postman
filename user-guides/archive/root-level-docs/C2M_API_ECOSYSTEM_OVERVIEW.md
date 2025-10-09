# C2M API Ecosystem Overview

This document provides a comprehensive overview of the C2M API ecosystem, including all repositories, local development setup, and the complete build/deployment pipeline.

## Table of Contents
1. [Repository Architecture](#repository-architecture)
2. [Local Development Setup](#local-development-setup)
3. [Build Triggers and Workflows](#build-triggers-and-workflows)
4. [Build Effects and Outputs](#build-effects-and-outputs)
5. [Manual vs CI/CD Workflows](#manual-vs-cicd-workflows)

---

## Repository Architecture

The C2M API ecosystem consists of three GitHub repositories, each serving a specific purpose:

### 1. c2m-api-repo (Main Source Repository)
**URL**: https://github.com/faserrao/c2m-api-repo  
**Purpose**: Contains all source files and configuration for the C2M API
**Key Contents**:
- `data_dictionary/c2mapiv2-dd.ebnf` - EBNF data dictionary (source of truth)
- `openapi/overlays/` - OpenAPI overlay files for customization
- `postman/custom/` - Custom Postman test files
- `postman/environments/` - Postman environment configurations
- `scripts/` - Build and utility scripts
- `Makefile` - Orchestrates all build processes
- `.github/workflows/` - GitHub Actions CI/CD workflows

**What it does NOT contain** (as of two-repo migration):
- Generated OpenAPI specifications
- Generated Postman collections
- Built documentation
- Generated SDKs

### 2. c2m-api-artifacts (Generated Artifacts Repository)
**URL**: https://github.com/faserrao/c2m-api-artifacts  
**Purpose**: Stores all generated/built artifacts from the main repository
**Key Contents**:
- `openapi/` - Generated OpenAPI specifications
  - `c2mapiv2-openapi-spec-base.yaml` - Base spec from EBNF
  - `c2mapiv2-openapi-spec-final.yaml` - Final spec with overlays
  - `bundled.yaml` - Bundled specification
- `postman/collections/` - Generated Postman collections
- `postman/metadata/` - Postman API metadata and IDs
- `docs/` - Generated API documentation
- `sdks/` - Generated SDKs in multiple languages

**Updated by**: CI/CD workflow on every push to main branch of c2m-api-repo

### 3. c2m-api-v2-security (Security/Authentication Repository)
**URL**: https://github.com/faserrao/c2m-api-v2-security  
**Purpose**: Contains the authentication system implementation
**Key Contents**:
- `cognito-auth-app/` - CDK application for AWS Cognito setup
- Authentication endpoints implementation
- JWT token management
- Security documentation

**Deployment**: Separate AWS CDK stack (C2MCognitoAuthStack-dev)

---

## Local Development Setup

### Prerequisites
1. **Required Software**:
   - Node.js (v20+) and npm
   - Python 3.11+
   - Git
   - Make
   - jq (JSON processor)
   - curl

2. **API Keys**:
   - Postman API key (personal and/or team)
   - GitHub personal access token (for security repo access)

### Local Installation

1. **Clone the main repository**:
   ```bash
   git clone https://github.com/faserrao/c2m-api-repo.git
   cd c2m-api-repo
   ```

2. **Create .env file** with your credentials:
   ```bash
   POSTMAN_SERRAO_API_KEY=your-personal-api-key
   POSTMAN_C2M_API_KEY=your-team-api-key
   ```

3. **Install dependencies**:
   ```bash
   npm install
   pip install -r scripts/python_env/requirements.txt
   ```

4. **Clone artifacts repository** (optional, for local sync):
   ```bash
   cd ..
   git clone https://github.com/faserrao/c2m-api-artifacts.git
   cd c2m-api-repo
   ```

### Local Repository Structure
```
~/your-workspace/
├── c2m-api-repo/          # Main source repository (your working directory)
├── c2m-api-artifacts/     # Generated artifacts (optional for local sync)
└── c2m-api-v2-security/   # Security implementation (if needed)
```

---

## Build Triggers and Workflows

### Manual Triggers (Local Development)

1. **Full Build Pipeline**:
   ```bash
   make postman-instance-build-and-test
   ```
   This runs the complete pipeline: EBNF → OpenAPI → Postman → Tests

2. **Individual Build Steps**:
   ```bash
   make openapi-build              # Generate OpenAPI spec from EBNF
   make postman-collection-build   # Generate Postman collections
   make docs                       # Generate documentation
   make generate-sdk-all          # Generate SDKs
   ```

3. **Local Sync to Artifacts Repo**:
   ```bash
   make local-sync                 # Sync generated files to ../c2m-api-artifacts
   make local-full-build          # Build everything and sync
   ```

4. **Postman Publishing**:
   ```bash
   make postman-publish-personal   # Publish to personal workspace only
   make postman-publish-team      # Publish to team workspace only
   make postman-publish-both      # Publish to BOTH workspaces
   ```

### CI/CD Triggers (GitHub Actions)

1. **Pull Request Triggers**:
   - **Triggered by**: Opening or updating a PR
   - **Workflows**: 
     - `pr-drift-check.yml` - Validates builds work correctly
     - `api-ci-cd.yml` - Builds but doesn't deploy
   - **What happens**: 
     - Builds all artifacts
     - Runs tests
     - Does NOT update Postman
     - Does NOT push to artifacts repo

2. **Main Branch Triggers**:
   - **Triggered by**: Push or merge to main branch
   - **Workflow**: `api-ci-cd.yml`
   - **What happens**:
     - Builds all artifacts
     - Pushes to c2m-api-artifacts repository
     - Updates Postman workspaces (based on .postman-target)
     - Deploys documentation

---

## Build Effects and Outputs

### EBNF to OpenAPI Conversion
**Input**: `data_dictionary/c2mapiv2-dd.ebnf`
**Process**: 
1. Python script converts EBNF to base OpenAPI spec
2. Overlays are merged for customizations
3. Spec is validated and linted

**Output**: 
- `openapi/c2mapiv2-openapi-spec-base.yaml`
- `openapi/c2mapiv2-openapi-spec-final.yaml`

### OpenAPI to Postman Conversion
**Input**: Final OpenAPI specification
**Process**:
1. Generate base Postman collection
2. Merge with custom test files
3. Fix URLs and add examples
4. Generate multiple collection variants

**Output**:
- 7 different Postman collection files
- Mock server configuration
- Environment files

### Documentation Generation
**Input**: Final OpenAPI specification
**Process**: 
1. Generate Redoc static documentation
2. Generate Swagger UI documentation
3. Create custom API guides

**Output**:
- `docs/index.html` - Main documentation
- `docs/redoc.html` - Redoc version
- `docs/swagger.html` - Swagger UI version

### SDK Generation
**Input**: Final OpenAPI specification
**Process**: OpenAPI Generator creates client libraries
**Output**: SDKs in multiple languages:
- C# (.NET)
- Go
- Java
- JavaScript/TypeScript
- Python
- Ruby
- And more...

### Postman Workspace Updates
**Process**:
1. Clean existing resources in workspace
2. Import new API definition
3. Create/update collections
4. Create/update mock servers
5. Set up environment variables

**Result**: 
- Updated collections in Postman workspace(s)
- New mock server URL
- Synchronized API definition

---

## Manual vs CI/CD Workflows

### Manual (Local) Workflow

**When to use**: Development, testing, debugging

**Advantages**:
- Full control over each step
- Can run individual targets
- Immediate feedback
- Can test without committing

**Key Commands**:
```bash
# Development workflow
make openapi-build              # Just build OpenAPI
make postman-test-local        # Test with local Prism mock
make postman-publish-personal  # Publish to your workspace only

# Full rebuild
make postman-cleanup-all       # Clean everything
make postman-instance-build-and-test  # Full rebuild
```

### CI/CD Workflow

**When to use**: Production deployments, team updates

**Advantages**:
- Automated and consistent
- Updates artifacts repository
- Can update both workspaces
- Maintains build history
- No manual intervention needed

**Process Flow**:
1. Developer pushes changes to branch
2. Creates PR → PR checks run
3. PR merged to main → Full deployment triggered
4. Artifacts pushed to artifacts repo
5. Postman workspaces updated
6. Documentation deployed

### Workspace Target Configuration

The `.postman-target` file controls which workspace(s) get updated:
- `personal` - Updates personal workspace only
- `team` - Updates team workspace only  
- `both` - Updates both workspaces

This file is read by both manual and CI/CD workflows.

---

## Key Configuration Files

### Makefile Variables
Key variables that control the build:
```makefile
POSTMAN_API_NAME := C2mApiV2
C2MAPIV2_EBNF_DD := data_dictionary/c2mapiv2-dd.ebnf
C2MAPIV2_OPENAPI_SPEC := openapi/c2mapiv2-openapi-spec-final.yaml
ARTIFACTS_REPO := ../c2m-api-artifacts
```

### GitHub Secrets Required
For CI/CD to work, these secrets must be set:
- `POSTMAN_SERRAO_API_KEY` - Personal workspace API key
- `POSTMAN_C2M_API_KEY` - Team workspace API key
- `SECURITY_REPO_TOKEN` - PAT for artifacts repo access

### Environment Variables
Set in `.env` for local development:
```bash
POSTMAN_SERRAO_API_KEY=pmak_xxx
POSTMAN_C2M_API_KEY=pmak_yyy
```

---

## Troubleshooting

### Common Issues

1. **Build fails with "Missing file" error**:
   - Run `make clean` to remove old generated files
   - Ensure you're in the c2m-api-repo directory

2. **Postman publish fails**:
   - Check API keys in .env file
   - Verify workspace IDs in Makefile
   - Run `make postman-cleanup-all` to reset

3. **CI/CD fails on main branch**:
   - Check GitHub secrets are set correctly
   - Verify .postman-target file exists
   - Check artifacts repo is accessible

### Useful Debug Commands
```bash
make show-vars          # Display all Makefile variables
make postman-auth-test  # Test Postman authentication
make artifacts-status   # Check artifacts repo status
```

---

## Summary

The C2M API ecosystem implements a clean separation of concerns:
- **Source code** lives in c2m-api-repo
- **Generated artifacts** are stored in c2m-api-artifacts  
- **Security implementation** is isolated in c2m-api-v2-security

This architecture prevents git conflicts, maintains clean history, and enables both manual and automated workflows. The Makefile serves as the orchestration layer, providing consistent commands for both local development and CI/CD pipelines.