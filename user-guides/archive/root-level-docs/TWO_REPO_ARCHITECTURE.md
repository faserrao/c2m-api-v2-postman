# Two Repository Architecture for C2M API

## 1. The Issue We're Solving

### Current Problems:
- **Race Conditions**: Multiple automated processes (CI/CD, Redoc updater) create git conflicts when trying to commit generated files
- **Repository Bloat**: Generated files mixed with source files makes the repo large and noisy
- **Unclear Ownership**: Hard to distinguish human-authored files from machine-generated ones
- **Version Control Noise**: Every build creates commits with hundreds of generated file changes
- **CI/CD Failures**: Builds succeed but fail to commit artifacts due to branch divergence

### Root Cause:
The single repository serves two conflicting purposes:
1. **Source Control**: Managing human-authored source files
2. **Artifact Storage**: Storing machine-generated build outputs

## 2. How We're Solving It

### Solution: Two-Repository Pattern
Separate source files and generated artifacts into two distinct repositories:
- **Source Repository**: Contains only human-authored files (EBNF, scripts, configs)
- **Artifacts Repository**: Contains only machine-generated files (OpenAPI specs, SDKs, docs)

### Benefits:
- No more git conflicts between automated processes
- Clear separation of concerns
- Smaller, focused repositories
- Clean commit history in source repo
- CI/CD can always push to artifacts repo without conflicts

## 3. Repository Descriptions

### Source Repository: `c2m-api-repo`
**Purpose**: Source of truth for API definitions and build logic

**Contents**:
```
c2m-api-repo/
├── data_dictionary/
│   ├── c2mapiv2-dd.ebnf              # EBNF data dictionary (source of truth)
│   └── examples/                      # Example requests/responses
│
├── scripts/
│   ├── active/                        # Current conversion scripts
│   │   ├── ebnf_to_openapi_dynamic_v3.py
│   │   ├── merge_openapi_overlays.py
│   │   └── ...
│   └── utilities/                     # Helper scripts
│
├── openapi/
│   └── overlays/                      # Only overlay files (human-authored)
│       └── auth.tokens.yaml           # Auth endpoint additions
│
├── postman/
│   ├── templates/                     # Postman collection templates
│   └── scripts/                       # Pre-request scripts, tests
│
├── .github/
│   └── workflows/                     # GitHub Actions workflows
│       └── api-ci-cd.yml             # Main CI/CD pipeline
│
├── Makefile                          # Build orchestration
├── requirements.txt                  # Python dependencies
├── package.json                      # Node dependencies
└── user-guides/                      # Documentation
```

### Artifacts Repository: `c2m-api-artifacts`
**Purpose**: Storage for all generated build outputs

**Contents**:
```
c2m-api-artifacts/
├── openapi/
│   ├── c2mapiv2-openapi-spec-base.yaml    # Generated from EBNF
│   ├── c2mapiv2-openapi-spec-final.yaml   # With overlays applied
│   └── bundled.yaml                        # Dereferenced version
│
├── postman/
│   ├── collections/
│   │   ├── c2mapiv2-collection.json
│   │   ├── c2mapiv2-linked-collection-flat.json
│   │   ├── c2mapiv2-test-collection.json
│   │   └── ...
│   │
│   └── metadata/                           # Postman IDs, URLs
│       ├── postman_mock_url.txt
│       ├── postman_api_uid.txt
│       ├── postman_env_uid.txt
│       └── ...
│
├── docs/
│   ├── redoc/
│   │   └── index.html                      # Redoc API documentation
│   ├── swagger/
│   │   └── index.html                      # Swagger UI
│   └── site/                               # GitHub Pages content
│
├── sdks/                                   # Generated SDKs
│   ├── python/
│   │   └── c2m_api_client/
│   ├── javascript/
│   │   └── c2m-api-client/
│   ├── typescript/
│   │   └── c2m-api-client/
│   ├── java/
│   │   └── com.c2m.api/
│   ├── go/
│   │   └── c2mapiclient/
│   ├── csharp/
│   │   └── C2M.Api.Client/
│   └── ...
│
├── schemas/                                # JSON schemas (future)
│   └── ...
│
└── README.md                               # Explains this is auto-generated
```

## 4. Key Differences Between Repositories

| Aspect | Source Repo | Artifacts Repo |
|--------|-------------|----------------|
| **Authors** | Humans | CI/CD only |
| **Edit Frequency** | When requirements change | Every build |
| **File Types** | .ebnf, .py, .yml, .md | .yaml, .json, .html |
| **Version Control** | Meaningful commits | Auto-commits |
| **Size** | Small (~1-5 MB) | Large (~50+ MB) |
| **Dependencies** | Yes (Python, Node) | No |
| **CI/CD Role** | Trigger builds | Receive outputs |
| **Permissions** | Team write access | CI write, team read |

## 5. GitHub Actions Workflow

### Trigger Events:
1. Push to `main` branch in source repo
2. Pull request to `main` branch  
3. Manual workflow dispatch
4. Scheduled runs (optional)

### Workflow Steps:

```yaml
name: API Build and Deploy

on:
  push:
    branches: [main]
    paths:
      - 'data_dictionary/**'
      - 'scripts/**'
      - 'openapi/overlays/**'
      - 'Makefile'

jobs:
  build-and-deploy:
    steps:
      1. Checkout source repo (c2m-api-repo)
      2. Checkout artifacts repo (c2m-api-artifacts)
      3. Setup Python/Node environments
      4. Install dependencies
      
      5. Generate artifacts:
         - Run EBNF → OpenAPI converter
         - Apply overlays
         - Generate Postman collections
         - Build documentation
         - Generate SDKs (all languages)
         
      6. Copy artifacts to artifacts repo:
         - openapi/* → artifacts-repo/openapi/
         - postman/generated/* → artifacts-repo/postman/collections/
         - docs/* → artifacts-repo/docs/
         - sdk/* → artifacts-repo/sdks/
         
      7. Publish to Postman (both workspaces):
         - Delete existing APIs/collections
         - Import new OpenAPI spec
         - Create linked collections
         - Update mock servers
         
      8. Commit to artifacts repo:
         - git add all changes
         - Commit with build metadata
         - Push to main branch
         
      9. Deploy GitHub Pages (from artifacts repo)
```

### Key Improvements:
- No conflicts: CI is the only writer to artifacts repo
- Atomic updates: All artifacts updated together
- Clear audit trail: Each build creates one commit in artifacts repo
- Parallel operations: Can update Postman while committing artifacts

## 6. Steady State After a Successful Run

### Source Repository State:
- **No changes**: Source files remain unchanged
- **Clean working tree**: No generated files to commit
- **Build logs**: Available in GitHub Actions

### Artifacts Repository State:
- **Latest commit**: "Build #123: Update from EBNF changes"
- **All artifacts synchronized**:
  - OpenAPI specs match current EBNF
  - Postman collections match OpenAPI specs
  - Documentation reflects latest API
- **Consistent timestamps**: All files updated together
- **Tagged releases**: Optional versioning (v1.2.3)

### Postman Workspaces State:
- **Personal Workspace**: Updated with latest API/collections
- **Team Workspace**: Updated with latest API/collections
- **Mock Servers**: Running with latest specifications
- **Environment Variables**: Updated with new mock URLs

### GitHub Pages State:
- **Deployed from artifacts repo**
- **Latest documentation live**
- **Accessible at**: https://faserrao.github.io/c2m-api-artifacts/

## 7. Additional Considerations

### Security:
- **Secrets Required**:
  - `SECURITY_REPO_TOKEN` (or new PAT) for artifacts repo access
  - `POSTMAN_SERRAO_API_KEY` for personal workspace
  - `POSTMAN_C2M_API_KEY` for team workspace
- **Permissions**: 
  - Source repo: Team has write access
  - Artifacts repo: Team has read access, CI has write

### Local Development: Detailed Workflows

#### Current vs New Behavior

| Action | Current (Single Repo) | New (Two Repo) |
|--------|----------------------|----------------|
| `make openapi-build` | Creates files, stages for commit | Creates files, they're gitignored |
| `make postman-publish` | Updates Postman + commits files | Updates Postman only |
| `git commit` | Includes generated files | Only source files |
| View artifacts | In same repo | Need to check artifacts repo |

#### Workflow 1: Quick Local Development (Most Common)
For testing changes locally without publishing:

```bash
cd c2m-api-repo

# Edit your EBNF file
vim data_dictionary/c2mapiv2-dd.ebnf

# Build and test locally
make openapi-build              # Generates openapi/*.yaml
make postman-collection-build   # Generates postman/generated/*
make docs-build                 # Generates docs/*
make generate-sdk-python        # Generates sdk/python/*

# View your generated files
cat openapi/c2mapiv2-openapi-spec-final.yaml
open docs/index.html

# IMPORTANT: These files are .gitignored
# They exist locally but won't be committed to source repo
```

#### Workflow 2: Test Full Pipeline Locally
Simulate the complete CI/CD process:

```bash
# Have both repos side by side
~/projects/
  ├── c2m-api-repo/        # Source files
  └── c2m-api-artifacts/   # Generated files

# Build in source repo
cd ~/projects/c2m-api-repo
make openapi-build
make generate-sdk-all

# Manually sync to artifacts repo
cp -r openapi/*.yaml ../c2m-api-artifacts/openapi/
cp -r sdk/* ../c2m-api-artifacts/sdks/

# Commit to artifacts repo (simulating CI)
cd ../c2m-api-artifacts
git add .
git commit -m "Local build test"
```

#### Workflow 3: Local Postman Updates
Update Postman from local build without git:

```bash
cd c2m-api-repo

# Build locally
make openapi-build

# Publish to Postman directly (without git commits)
make postman-publish

# This updates Postman but doesn't touch git at all
# Perfect for testing before pushing to GitHub
```

#### New Make Targets for Local Development
Add these targets to simplify local workflows:

```makefile
# Variables
ARTIFACTS_REPO ?= ../c2m-api-artifacts

# Sync local build to artifacts repo
local-sync:
    @echo "Syncing to local artifacts repo..."
    @mkdir -p $(ARTIFACTS_REPO)/openapi
    @mkdir -p $(ARTIFACTS_REPO)/postman/collections
    @mkdir -p $(ARTIFACTS_REPO)/docs
    @mkdir -p $(ARTIFACTS_REPO)/sdks
    cp -r openapi/*.yaml $(ARTIFACTS_REPO)/openapi/
    cp -r postman/generated/* $(ARTIFACTS_REPO)/postman/collections/
    cp -r docs/* $(ARTIFACTS_REPO)/docs/
    cp -r sdk/* $(ARTIFACTS_REPO)/sdks/

# Build everything and sync
local-full-build: openapi-build docs-build generate-sdk-all local-sync
    @echo "Full build complete and synced!"

# Test the complete pipeline locally
local-test-pipeline:
    make local-full-build
    cd $(ARTIFACTS_REPO) && git add . && git commit -m "Local test"
    @echo "Pipeline test complete!"
```

#### Benefits for Local Development

1. **Faster commits** - No huge generated files in your commits
2. **Cleaner diffs** - Only see actual source changes  
3. **Flexible testing** - Can test locally without affecting git
4. **Parallel work** - Can work on source while CI handles artifacts
5. **Quick iteration** - Test changes without waiting for CI/CD

#### Required .gitignore Updates

```gitignore
# Generated OpenAPI specs
/openapi/c2mapiv2-openapi-spec-base.yaml
/openapi/c2mapiv2-openapi-spec-final.yaml
/openapi/bundled.yaml

# Generated Postman files
/postman/generated/
/postman/*.json
/postman/*.txt

# Generated documentation
/docs/index.html
/docs/site/
/docs/swagger/

# Generated SDKs
/sdk/
```

This ensures generated files stay local and don't clutter the repository.

### Rollback Strategy:
- Source repo: Revert commit and rebuild
- Artifacts repo: Check out previous commit or use GitHub releases
- Postman: Keep previous version as backup collection

### Monitoring:
- GitHub Actions notifications for build failures
- Postman monitors for API health
- Optional: Webhook notifications for artifact updates

### Future Enhancements:
1. **Semantic Versioning**: Tag releases in artifacts repo
2. **SDK Publishing**: Publish SDKs to package managers (PyPI, npm, Maven)
3. **Change Detection**: Only rebuild changed components
4. **Multi-environment**: Support dev/staging/prod artifacts
5. **Artifact Retention**: Automated cleanup of old builds
6. **SDK Documentation**: Generate SDK-specific docs and examples

## 8. Migration Plan

1. Create artifacts repository
2. Update CI/CD workflow
3. Test with a small change
4. Remove generated files from source repo
5. Update documentation and team processes

## Conclusion

This two-repository architecture provides a clean separation between source and generated files, eliminates CI/CD conflicts, and creates a more maintainable system. The source repository remains focused on human-authored content while the artifacts repository serves as a reliable distribution point for all generated assets.