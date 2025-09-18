# Two Repository Implementation Plan

## Overview
This document provides a step-by-step plan to migrate from the current single-repository structure to a two-repository architecture, separating source files from generated artifacts.

## Phase 1: Create Artifacts Repository

### Task 1.1: Create New GitHub Repository
**Owner**: Repository Admin
**Description**: Create the new artifacts repository on GitHub
**Steps**:
```bash
gh repo create faserrao/c2m-api-artifacts \
  --public \
  --description "Generated artifacts from c2m-api-repo builds" \
  --add-readme
```

### Task 1.2: Initialize Artifacts Repository Structure
**Owner**: Developer
**Description**: Create the initial directory structure
**Steps**:
```bash
git clone https://github.com/faserrao/c2m-api-artifacts.git
cd c2m-api-artifacts

# Create directory structure
mkdir -p openapi
mkdir -p postman/collections
mkdir -p postman/metadata
mkdir -p docs/redoc
mkdir -p docs/swagger
mkdir -p sdks

# Create README
cat > README.md << 'EOF'
# C2M API Artifacts

This repository contains automatically generated artifacts from the [c2m-api-repo](https://github.com/faserrao/c2m-api-repo).

## ⚠️ Do Not Edit These Files

All files in this repository are automatically generated. Any manual changes will be overwritten by the next build.

To make changes, please edit the source files in [c2m-api-repo](https://github.com/faserrao/c2m-api-repo).

## Repository Structure

- `openapi/` - Generated OpenAPI specifications
- `postman/` - Postman collections and metadata
- `docs/` - API documentation
- `sdks/` - Generated client SDKs

## Build Status

Latest build: See [GitHub Actions](https://github.com/faserrao/c2m-api-repo/actions)
EOF

# Initial commit
git add .
git commit -m "Initial repository structure"
git push origin main
```

### Task 1.3: Configure GitHub Pages (Optional)
**Owner**: Repository Admin
**Description**: Enable GitHub Pages for documentation hosting
**Steps**:
1. Go to Settings → Pages
2. Source: Deploy from branch
3. Branch: main
4. Folder: /docs
5. Save

## Phase 2: Update Source Repository

### Task 2.1: Create/Update .gitignore
**Owner**: Developer
**Description**: Add generated files to .gitignore
**File**: `.gitignore`
```gitignore
# Generated OpenAPI specifications
/openapi/c2mapiv2-openapi-spec-base.yaml
/openapi/c2mapiv2-openapi-spec-final.yaml
/openapi/bundled.yaml
/openapi/c2mapiv2-openapi-spec-final-with-examples.yaml

# Generated Postman files
/postman/generated/
/postman/*.json
/postman/*.txt
/postman/env-upload-debug.json
/postman/import-api-debug.json
/postman/import-api-response.json
/postman/link-debug.json
/postman/link-payload.json
/postman/mock-env.json
/postman/postman_*.txt
/postman/spec-standalone-*.json
/postman/upload-test-debug.json

# Generated documentation
/docs/index.html
/docs/site/
/docs/swagger/
/docs/redoc/

# Generated SDKs
/sdk/
/sdks/

# Build artifacts
*.pyc
__pycache__/
.venv/
venv/
node_modules/
.DS_Store
```

### Task 2.2: Update GitHub Actions Workflow
**Owner**: DevOps/Developer
**Description**: Modify CI/CD to use two repositories
**File**: `.github/workflows/api-ci-cd.yml`

Key changes needed:
```yaml
jobs:
  build:
    steps:
      # Add after existing checkout
      - name: Checkout artifacts repository
        uses: actions/checkout@v4
        with:
          repository: faserrao/c2m-api-artifacts
          path: artifacts-repo
          token: ${{ secrets.SECURITY_REPO_TOKEN }}
      
      # Replace the commit step with:
      - name: Copy artifacts to artifacts repo
        run: |
          # Copy generated files
          cp -r openapi/*.yaml artifacts-repo/openapi/
          cp -r postman/generated/* artifacts-repo/postman/collections/
          cp -r postman/*.txt artifacts-repo/postman/metadata/
          cp -r postman/*.json artifacts-repo/postman/metadata/
          cp -r docs/* artifacts-repo/docs/
          if [ -d "sdk" ]; then cp -r sdk/* artifacts-repo/sdks/; fi
          
      - name: Commit and push artifacts
        working-directory: artifacts-repo
        run: |
          git config user.name "c2m-api-bot"
          git config user.email "c2m-api-bot@users.noreply.github.com"
          git add .
          git commit -m "Build #${{ github.run_number }}: Update from ${{ github.sha }}" || echo "No changes"
          git push
```

### Task 2.3: Add Local Development Make Targets
**Owner**: Developer
**Description**: Add convenience targets for local development
**File**: `Makefile`

Add these targets:
```makefile
# Two-repo local development support
ARTIFACTS_REPO ?= ../c2m-api-artifacts

.PHONY: local-sync
local-sync: ## Sync generated files to local artifacts repo
	@echo "📦 Syncing artifacts to $(ARTIFACTS_REPO)..."
	@if [ ! -d "$(ARTIFACTS_REPO)" ]; then \
		echo "❌ Artifacts repo not found at $(ARTIFACTS_REPO)"; \
		echo "   Clone it with: git clone https://github.com/faserrao/c2m-api-artifacts.git $(ARTIFACTS_REPO)"; \
		exit 1; \
	fi
	@mkdir -p $(ARTIFACTS_REPO)/openapi
	@mkdir -p $(ARTIFACTS_REPO)/postman/collections
	@mkdir -p $(ARTIFACTS_REPO)/postman/metadata
	@mkdir -p $(ARTIFACTS_REPO)/docs
	@mkdir -p $(ARTIFACTS_REPO)/sdks
	@cp -v openapi/*.yaml $(ARTIFACTS_REPO)/openapi/ 2>/dev/null || true
	@cp -v postman/generated/* $(ARTIFACTS_REPO)/postman/collections/ 2>/dev/null || true
	@cp -v postman/*.txt postman/*.json $(ARTIFACTS_REPO)/postman/metadata/ 2>/dev/null || true
	@cp -rv docs/* $(ARTIFACTS_REPO)/docs/ 2>/dev/null || true
	@cp -rv sdk/* $(ARTIFACTS_REPO)/sdks/ 2>/dev/null || true
	@echo "✅ Sync complete!"

.PHONY: local-full-build
local-full-build: openapi-build postman-collection-build docs-build ## Full build with artifacts sync
	@$(MAKE) local-sync

.PHONY: local-test-pipeline
local-test-pipeline: ## Test the full two-repo pipeline locally
	@echo "🧪 Testing full pipeline locally..."
	@$(MAKE) clean
	@$(MAKE) local-full-build
	@cd $(ARTIFACTS_REPO) && \
		git add . && \
		git diff --staged --stat && \
		echo "✅ Pipeline test complete! (Changes not committed)"
```

## Phase 3: Test Migration

### Task 3.1: Test Local Builds
**Owner**: Developer
**Description**: Verify local development workflows
**Steps**:
```bash
# Clone both repos
git clone https://github.com/faserrao/c2m-api-repo.git
git clone https://github.com/faserrao/c2m-api-artifacts.git

# Test build and sync
cd c2m-api-repo
make local-full-build

# Verify artifacts
ls ../c2m-api-artifacts/openapi/
ls ../c2m-api-artifacts/postman/collections/
```

### Task 3.2: Test CI/CD with Test Branch
**Owner**: DevOps/Developer
**Description**: Test the new workflow before deploying to main
**Steps**:
1. Create test branch: `git checkout -b test/two-repo-setup`
2. Push changes and monitor GitHub Actions
3. Verify artifacts are pushed to artifacts repo
4. Verify Postman is still updated correctly

### Task 3.3: Verify Postman Integration
**Owner**: API Team
**Description**: Ensure Postman workspaces still update correctly
**Checklist**:
- [ ] Personal workspace receives updates
- [ ] Team workspace receives updates
- [ ] Mock servers are created/updated
- [ ] Collections are properly linked

## Phase 4: Clean Up Source Repository

### Task 4.1: Remove Generated Files
**Owner**: Developer
**Description**: Remove all generated files from source repo
**Steps**:
```bash
# Remove generated files (they're now in artifacts repo)
git rm -r openapi/c2mapiv2-openapi-spec-*.yaml
git rm -r openapi/bundled.yaml
git rm -r postman/generated/
git rm postman/*.json
git rm postman/*.txt
git rm -rf docs/index.html docs/site/ docs/swagger/
git rm -rf sdk/

# Commit the removal
git commit -m "chore: remove generated files (moved to artifacts repo)"
```

### Task 4.2: Update Documentation
**Owner**: Developer
**Description**: Update all documentation to reflect new structure
**Files to update**:
- [ ] README.md - Add links to artifacts repo
- [ ] CONTRIBUTING.md - Update build instructions
- [ ] user-guides/*.md - Update any build-related guides

### Task 4.3: Update CI/CD Badges
**Owner**: Developer
**Description**: Add status badges to both repos
**In source repo README**:
```markdown
[![Build Status](https://github.com/faserrao/c2m-api-repo/actions/workflows/api-ci-cd.yml/badge.svg)](https://github.com/faserrao/c2m-api-repo/actions)
[![Artifacts](https://img.shields.io/badge/artifacts-c2m--api--artifacts-blue)](https://github.com/faserrao/c2m-api-artifacts)
```

## Phase 5: Deploy to Production

### Task 5.1: Merge to Main Branch
**Owner**: Repository Admin
**Description**: Deploy the new workflow
**Steps**:
1. Create PR from test branch
2. Review all changes
3. Merge to main
4. Monitor first production build

### Task 5.2: Verify Production Build
**Owner**: DevOps Team
**Description**: Ensure everything works in production
**Checklist**:
- [ ] GitHub Actions completes successfully
- [ ] Artifacts repo receives updates
- [ ] Postman workspaces are updated
- [ ] No git conflicts or errors

### Task 5.3: Team Training
**Owner**: Team Lead
**Description**: Update team on new workflow
**Topics**:
- New repository structure
- Local development changes
- Where to find generated files
- How to debug build issues

## Phase 6: Post-Migration Tasks

### Task 6.1: Set Up Monitoring
**Owner**: DevOps
**Description**: Monitor both repositories
**Actions**:
- Set up notifications for build failures
- Monitor artifacts repo size
- Set up alerts for Postman API failures

### Task 6.2: Create Backup Strategy
**Owner**: DevOps
**Description**: Ensure artifacts are backed up
**Options**:
- GitHub releases for versioning
- External backup of artifacts
- Retention policy for old builds

### Task 6.3: Document Rollback Procedure
**Owner**: Developer
**Description**: Create rollback documentation
**Include**:
- How to revert to single-repo if needed
- How to restore from artifacts backup
- Emergency contact procedures

## Success Criteria

The migration is complete when:

1. ✅ Source repo contains only human-authored files
2. ✅ Artifacts repo contains all generated files
3. ✅ CI/CD builds without errors
4. ✅ Postman workspaces update correctly
5. ✅ Local development workflows are functional
6. ✅ Team is trained on new process
7. ✅ Documentation is updated
8. ✅ No generated files in source repo git history going forward

## Timeline Estimate

- Phase 1: 1 hour (create and setup repos)
- Phase 2: 2-3 hours (update workflows and test)
- Phase 3: 1-2 hours (testing)
- Phase 4: 1 hour (cleanup)
- Phase 5: 1 hour (deployment)
- Phase 6: 2 hours (monitoring and documentation)

**Total**: 8-10 hours of work

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| CI/CD fails | Test thoroughly on branch first |
| Postman stops updating | Keep existing workflow as fallback |
| Team confusion | Document clearly, train early |
| Lost artifacts | Implement backup strategy |
| Git conflicts | Ensure only CI writes to artifacts |

## Rollback Plan

If issues arise:
1. Revert GitHub Actions workflow
2. Restore generated files to source repo
3. Remove .gitignore entries
4. Archive artifacts repo (don't delete)
5. Document lessons learned

## Notes

- Keep the `SECURITY_REPO_TOKEN` secret (reuse for artifacts repo)
- Consider renaming to `CROSS_REPO_TOKEN` later
- The first build after migration will be large
- Subsequent builds will be incremental
- Consider setting up branch protection on artifacts repo (only CI can push to main)