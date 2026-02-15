# C2M API V2 - Main Repository

**Data-Driven API Pipeline**: EBNF Data Dictionary → OpenAPI Spec → Postman Collections → Mock Servers → Documentation → SDKs

## Overview

The C2M API V2 project implements a unique architecture where an EBNF (Extended Backus-Naur Form) data dictionary serves as the **single source of truth** for the entire API ecosystem. All downstream artifacts (OpenAPI specs, Postman collections, documentation, SDKs) are automatically generated from this source.

### Key Features

- **Single Source of Truth**: EBNF data dictionary drives all generated artifacts
- **Automated Pipeline**: Changes to EBNF automatically propagate through entire system
- **Dual Workspace Publishing**: Supports both personal and team Postman workspaces
- **CI/CD Integration**: GitHub Actions automates build, test, and deployment
- **Mock Servers**: Both local (Prism) and cloud (Postman) mock servers for testing
- **Multi-Language SDKs**: Automatic generation for 11 programming languages
- **Comprehensive Documentation**: Auto-generated API docs with Redocly

## Quick Start

### Prerequisites

```bash
# Required tools
- Node.js 14+ with npm
- Python 3.8+ with pip
- jq (command-line JSON processor)
- yq (YAML processor)
```

### Initial Setup

```bash
# 1. Install dependencies
make install

# 2. Configure environment variables
cp .env.example .env
# Edit .env with your credentials (see Security Credentials section below)

# 3. Set workspace target (personal or team)
echo "team" > .postman-target
```

### Common Commands

```bash
# Build and test entire pipeline (recommended for local development)
make postman-instance-build-with-tests

# Build without local testing (CI/CD mode)
make postman-instance-build-without-tests

# Clean all Postman resources
make postman-cleanup-all

# Start local mock server
make prism-start

# Run tests against mock
make prism-mock-test

# Serve documentation locally
make docs-serve
```

## Architecture

### Pipeline Flow

```
EBNF Data Dictionary (data_dictionary/c2mapiv2-dd.ebnf)
    ↓ [ebnf_to_openapi_dynamic_v3.py]
OpenAPI 3.0.3 Spec (openapi/c2mapiv2-openapi-spec-base.yaml)
    ↓ [openapi-to-postmanv2 + fixes]
Postman Collections
    ├─ Linked Collection (placeholders: <string>, <oneOf>)
    ├─ Test Collection (realistic faker data)
    ├─ Use Case Collection (real-world scenarios)
    └─ Getting Started Collection (educational patterns)
    ↓
Mock Servers (local Prism + cloud Postman)
    ↓
Documentation (Redocly HTML)
    ↓
SDKs (11 languages via openapi-generator)
```

### Repository Structure

```
c2m-api-v2-postman/
├── data_dictionary/          # EBNF source of truth
│   └── c2mapiv2-dd.ebnf     # 972 lines, 98 productions
├── openapi/                  # Generated OpenAPI specs
│   ├── c2mapiv2-openapi-spec-base.yaml
│   └── c2mapiv2-openapi-spec-final.yaml
├── postman/                  # Postman resources
│   ├── generated/           # Auto-generated collections
│   ├── scripts/             # JWT auth, test scripts
│   └── *.txt                # UID tracking files
├── scripts/                  # Pipeline scripts
│   ├── active/              # Core generators
│   ├── validation/          # Testing scripts
│   └── utilities/           # Support tools
├── docs/                     # Generated documentation
├── .github/workflows/        # CI/CD automation
├── Makefile                  # Main orchestrator
└── README.md                 # This file
```

## Security Credentials

### Environment Variables

The project requires several environment variables for authentication and API access. These variables are stored in a `.env` file (gitignored).

**IMPORTANT**: See `~/.c2msecure/C2M_API_V2_CREDENTIALS_REFERENCE.md` for:
- Complete list of required environment variables
- Where to obtain credentials
- Credential rotation schedules
- Access control matrix
- Security best practices

**Common Environment Variables**:
- `POSTMAN_C2M_API_KEY` - Team Postman workspace API key
- `GITHUB_PAT` - GitHub personal access token (cross-repo access)
- `OPENAI_API_KEY` - OpenAI API key (if using AI features)
- Additional variables documented in credentials reference

### Credential Storage

- **Actual credentials**: Stored in `~/.c2msecure/` (secure directory, never committed)
- **Documentation**: Credentials reference document with rotation schedules
- **This repository**: No credentials committed to git (all via .env file)

## Key Documentation

### Architecture Documents

- **[TRANSLATOR_ARCHITECTURE.md](../c2m-api-v2-manuals/top-level-documents/TRANSLATOR_ARCHITECTURE.md)** - Complete guide to EBNF → OpenAPI translator
- **[ERROR_SCHEMA_CHANGES_LOG.md](ERROR_SCHEMA_CHANGES_LOG.md)** - Error schema implementation tracking
- **[CLAUDE.md](CLAUDE.md)** - Project guidance for AI assistants

### User Guides

Located in sibling directory `c2m-api-v2-manuals/`:
- Complete Build Guide
- Operations and Administration Manual
- CI/CD Operations Guide
- Testing Guide
- Authentication Implementation Guide

## Development Workflow

### Making Changes to the API

1. **Edit EBNF Data Dictionary**:
   ```bash
   vim data_dictionary/c2mapiv2-dd.ebnf
   ```

2. **Generate OpenAPI Spec**:
   ```bash
   make generate-openapi-spec-from-ebnf-dd
   ```

3. **Verify Changes**:
   ```bash
   make openapi-spec-lint
   ```

4. **Build Collections and Test**:
   ```bash
   make postman-instance-build-with-tests
   ```

5. **Commit and Push** (CI/CD auto-publishes):
   ```bash
   git add data_dictionary/c2mapiv2-dd.ebnf openapi/*.yaml
   git commit -m "feat: add new endpoint/schema"
   git push
   ```

### Testing

```bash
# Local mock server testing
make prism-start
make prism-mock-test

# Cloud mock server testing
make postman-mock

# Test specific endpoint
PRISM_TEST_ENDPOINT=/jobs/submit/single/doc make prism-test-select
```

### Publishing to Postman Workspaces

```bash
# Set target workspace
echo "team" > .postman-target  # or "personal"

# Publish (reads .postman-target)
make postman-publish

# Or explicit targets
make postman-publish-personal
make postman-publish-team
```

## CI/CD Pipeline

### GitHub Actions Workflow

**Triggers**: Push to main, pull requests, manual dispatch

**Steps**:
1. Build OpenAPI spec from EBNF
2. Generate Postman collections (5 types)
3. Build documentation
4. Auto-commit generated files (main branch only)
5. Publish to Postman workspace (reads `.postman-target`)
6. Deploy docs to GitHub Pages

**Required GitHub Secrets**:
- `POSTMAN_C2M_API_KEY` - Team workspace API key
- `SECURITY_REPO_TOKEN` - PAT for cross-repo access (security and artifacts repos)

See `~/.c2msecure/C2M_API_V2_CREDENTIALS_REFERENCE.md` for obtaining these credentials.

## Makefile Targets

### Primary Build Targets

- `postman-instance-build-with-tests` - Full local build with testing (default)
- `postman-instance-build-without-tests` - CI/CD build (skips local infrastructure)
- `postman-cleanup-all` - Delete all Postman resources

### Pipeline Stage Targets

- `generate-openapi-spec-from-ebnf-dd` - EBNF → OpenAPI translation
- `openapi-spec-lint` - Validate OpenAPI spec
- `postman-collection-build` - Generate all collections
- `postman-publish` - Publish to workspace (reads .postman-target)
- `docs` - Build documentation
- `prism-start` / `prism-stop` - Local mock server

### Debug/Utility Targets

- `print-openapi-vars` - Show OpenAPI configuration
- `postman-workspace-debug` - Show workspace resources
- `verify-urls` - Verify collection URLs
- `prism-status` - Check mock server status

See Makefile for complete list of 150+ targets.

## Troubleshooting

### Common Issues

**Issue: OpenAPI spec generation fails**
```bash
# Check EBNF syntax
scripts/python_env/e2o.venv/bin/python scripts/active/ebnf_to_openapi_dynamic_v3.py \
  --report data_dictionary/c2mapiv2-dd.ebnf
```

**Issue: Collections not publishing**
```bash
# Verify API key
source .env
curl -H "X-API-Key: $POSTMAN_C2M_API_KEY" https://api.getpostman.com/me

# Check workspace target
cat .postman-target
```

**Issue: Mock server not responding**
```bash
# Check Prism status
make prism-status

# Restart Prism
make prism-stop
make prism-start
```

**Issue: Tests failing with 404**
```bash
# Verify mock created from TEST collection, not USE CASE collection
# Check Makefile lines 1520-1523 use POSTMAN_TEST_COLLECTION_UID_FILE
```

## Related Repositories

- **[c2m-api-v2-postman-security](https://github.com/click2mail/c2m-api-v2-postman-security)** - JWT authentication service
- **[c2m-api-v2-postman-artifacts](https://github.com/click2mail/c2m-api-v2-postman-artifacts)** - Generated SDKs and documentation
- **[c2m-api-v2-click2endpoint-developers](https://github.com/click2mail/c2m-api-v2-click2endpoint-developers)** - Interactive wizard for developers
- **[c2m-api-v2-click2endpoint-business](https://github.com/click2mail/c2m-api-v2-click2endpoint-business)** - AI-powered wizard for business users

## Key Learnings & Patterns

### Critical Patterns

1. **EBNF as Single Source of Truth**: All schema changes start here
2. **Hybrid Architecture**: Data-driven schemas + hardcoded REST conventions
3. **Mock Server Creation**: MUST use Test Collection (all endpoints), NOT Use Case Collection (examples only)
4. **JWT Mock Detection**: Check both `pm.request.url.host` AND `baseUrl` variable
5. **oneOf Handling**: Convert anonymous schemas to named schemas for proper placeholder replacement

### Common Gotchas

- **Double Encoding Bug**: Use `cat` not `jq -Rs .` for OpenAPI spec content
- **UID File Sync**: All targets must read from same UID file (e.g., `test_collection_uid.txt`)
- **Workspace Publishing**: `.postman-target` file controls destination
- **Parser Limitations**: Lark EBNF parser supports `{ element }` for arrays, NOT `{ key : value }` for dictionaries
- **Environment Variables**: Must `source .env` in same shell session for Make commands

## Support & Resources

### Internal Documentation

- **System-wide CLAUDE.md**: `/Users/frankserrao/CLAUDE.md` (session history)
- **Project-specific CLAUDE.md**: `CLAUDE.md` (this repo)
- **Session logs**: `c2m-api-v2-postman-claude.log` (append-only)

### External Resources

- **Postman API Docs**: https://www.postman.com/postman/workspace/postman-public-workspace/documentation/
- **OpenAPI 3.0.3 Spec**: https://spec.openapis.org/oas/v3.0.3
- **Lark Parser**: https://github.com/lark-parser/lark

## Contributing

### Development Guidelines

1. **Update EBNF First**: All API changes start with data dictionary
2. **Create Backups**: Before modifying core files (EBNF, translator)
3. **Test Locally**: Run `make postman-instance-build-with-tests` before pushing
4. **Document Changes**: Update CLAUDE.md session history for significant work
5. **Verify CI/CD**: Check GitHub Actions workflow passes after push

### Logging Protocol

**Update logs after each major feature OR every 30 minutes, whichever comes first**:
1. System-wide CLAUDE.md - Session history, architectural decisions
2. Project-specific CLAUDE.md - Project context, next steps
3. Session log - Chronological timeline with timestamps

## Version History

- **2026-02-13**: Error schema implementation complete (12 schemas, 48 error responses); Translator architecture documented
- **2026-02-12**: Getting Started collections refactored (read from linked/test collections)
- **2025-12-20**: Overall System Architecture documentation created
- **2025-12-19**: Configuration-driven Getting Started collections (YAML-based)
- **2025-12-18**: OpenAPI validation warnings fixed (34 → 5 warnings)
- **2025-11-09**: Apple Pay/Google Pay proposals + duplicate EBNF definitions fixed
- **2025-10-26**: V1 unimplemented endpoints specification (85 endpoints documented)
- **2025-10-25**: Migrated all 5 repositories to click2mail organization
- **2025-10-17**: Documentation cleanup (48 docs, emoji removal)
- **2025-10-13**: AWS infrastructure rebuild (unified authentication)
- **2025-09-30**: Click2Endpoint migrated from Streamlit to React
- **2025-09-08**: Repository restoration complete (pre-auth integration state)

## License

Proprietary - Click2Mail API V2 Project

## Contact

- **Project Team**: api-admin@click2mail.com
- **Documentation Issues**: https://github.com/click2mail/c2m-api-v2-postman/issues
- **Security Credentials**: See `~/.c2msecure/C2M_API_V2_CREDENTIALS_REFERENCE.md`

---

**Last Updated**: 2026-02-13
**Status**: Active Development
**Next Review**: When major architecture changes occur
