# GitHub Actions Security Repository Integration Guide

## Overview

This guide documents the complete process of integrating the private c2m-api-v2-security repository into the GitHub Actions CI/CD workflow to ensure JWT authentication scripts are properly added to Postman collections during automated builds.

## Problem Summary

The CI/CD workflow was failing to add JWT authentication scripts to Postman collections because:

1. The security repository (containing the auth scripts) was private
2. GitHub Actions couldn't access the private repo with default permissions
3. A jq command syntax error prevented the script from being added even when found
4. Symlinks in the repository caused GitHub Pages build failures

## Solution Implementation

### 1. Security Repository GitHub Setup

**Problem**: The JWT auth provider script lives in a separate private repository for security isolation.

**Solution**:
- Pushed the security repo to GitHub: https://github.com/faserrao/c2m-api-v2-security
- Kept it private to maintain security

### 2. Cross-Repository Access in CI

**Problem**: GitHub's default `GITHUB_TOKEN` cannot access other private repositories.

**Initial Attempt**: 
- Tried using `GITHUB_TOKEN` but got "Bad credentials" error

**Solution**:
- Created a Personal Access Token (PAT) with `repo` scope
- Added PAT as repository secret: `SECURITY_REPO_TOKEN`
- Updated workflow to checkout security repo:

```yaml
- name: Checkout security repository
  uses: actions/checkout@v4
  with:
    repository: faserrao/c2m-api-v2-security
    path: c2m-api-v2-security
    token: ${{ secrets.SECURITY_REPO_TOKEN }}
```

### 3. Workspace Path Issues

**Problem**: Initial checkout path `../c2m-api-v2-security` was outside GitHub Actions workspace.

**Error**: "Repository path is not under /home/runner/work/c2m-api-repo/c2m-api-repo"

**Solution**:
- Changed path to `c2m-api-v2-security` (relative to workspace)
- Updated Makefile to handle different paths for CI vs local:

```makefile
# Check if running in CI (GitHub Actions sets CI environment variable)
ifdef CI
SECURITY_POSTMAN_SCRIPTS_DIR := c2m-api-v2-security/postman/scripts
else
SECURITY_POSTMAN_SCRIPTS_DIR := ../c2m-api-v2-security/postman/scripts
endif
```

### 4. JQ Command Syntax Error in CI

**Problem**: Complex jq command with line continuations failed in CI environment.

**Error**: 
```
jq: error: syntax error, unexpected INVALID_CHARACTER (Unix shell quoting issues?) at <top-level>, line 1:
.event = (.event // []) | \
```

**Solution**:
Replaced jq approach with Node.js script that was already working for linked collections:

```makefile
postman-auth-setup: ## Configure authentication for Postman collection
	@echo "🔐 Setting up authentication configuration..."
	@if [ -f "$(SECURITY_POSTMAN_SCRIPTS_DIR)/jwt-auth-provider.js" ]; then \
		echo "📋 Using JWT auth provider script from security repo..."; \
		node scripts/active/add_pre_request_script.js "$(POSTMAN_TEST_COLLECTION_WITH_TESTS)" "$(SECURITY_POSTMAN_SCRIPTS_DIR)/jwt-auth-provider.js" "$(POSTMAN_TEST_COLLECTION_WITH_TESTS)" && \
		echo "✅ Auth provider script added to test collection" || \
		echo "❌ Failed to add auth provider script"; \
	else \
		echo "📋 Auth provider script not found in security repo, using local script..."; \
		if [ -f "$(POSTMAN_DIR)/scripts/jwt-pre-request.js" ]; then \
			node scripts/active/add_pre_request_script.js "$(POSTMAN_TEST_COLLECTION_WITH_TESTS)" "$(POSTMAN_DIR)/scripts/jwt-pre-request.js" "$(POSTMAN_TEST_COLLECTION_WITH_TESTS)" && \
			echo "✅ Local auth provider script added to test collection" || \
			echo "❌ Failed to add local auth provider script"; \
		else \
			echo "⚠️  No auth provider script found"; \
		fi; \
	fi
```

### 5. GitHub Pages Symlink Issues

**Problem**: Jekyll (GitHub Pages) cannot follow symlinks for security reasons.

**Solution**:
- Replaced all symlinked README.md files with actual file copies
- Created scripts to manage this process:
  - `fix-symlinks-simple.sh` - Replaces symlinks with actual files

## CI/CD Workflow Process

The fixed workflow now:

1. **Checks out main repository**
2. **Checks out security repository** using PAT
3. **Builds OpenAPI spec** from EBNF data dictionary
4. **Generates Postman collections**
5. **Adds JWT auth script** from security repo using Node.js script
6. **Uploads to Postman** with auth scripts properly included
7. **Deploys documentation** to GitHub Pages

## Key Files Modified

1. **`.github/workflows/api-ci-cd.yml`**
   - Added security repo checkout step
   - Configured to use `SECURITY_REPO_TOKEN`

2. **`Makefile`**
   - Added CI environment detection for paths
   - Replaced jq command with Node.js script call

3. **Repository Structure**
   - Replaced symlinks with actual files for GitHub Pages compatibility

## Verification Steps

To verify the auth scripts are properly added:

1. Check CI logs for:
   ```
   📋 Using JWT auth provider script from security repo...
   ✅ Auth provider script added to test collection
   ```

2. In Postman, check collection pre-request scripts for:
   - JWT authentication logic
   - Token refresh functions
   - NOT just the basic `Bearer {{token}}` script

## Troubleshooting

### Issue: "Bad credentials" error
**Solution**: Ensure PAT is correctly added as `SECURITY_REPO_TOKEN` secret

### Issue: Auth script not added despite success message
**Solution**: Check for jq syntax errors in logs, ensure Node.js script is used

### Issue: Security repo not found
**Solution**: Verify checkout step succeeded and path is correct for CI environment

## Security Considerations

1. **Private Repository**: Security repo remains private
2. **PAT Scope**: Only `repo` scope needed for read access
3. **Token Rotation**: PAT should be rotated periodically
4. **No Secrets in Code**: Auth logic is separate from credentials

## Benefits of This Approach

1. **Provider Flexibility**: Can switch auth providers (e.g., to CloudFlare) by updating security repo
2. **Security Isolation**: Auth infrastructure separate from main API code
3. **CI/CD Reliability**: Node.js script more reliable than complex shell commands
4. **Maintainability**: Single source of truth for auth scripts

## Future Improvements

1. Consider using GitHub's fine-grained PATs for more restricted access
2. Implement automated PAT rotation
3. Add monitoring for auth script inclusion in collections
4. Consider making security repo public if no sensitive data exists

## Related Documentation

- [SECURITY_REPO_GITHUB_SETUP.md](../SECURITY_REPO_GITHUB_SETUP.md) - Initial setup instructions
- [POSTMAN_COMPLETE_GUIDE.md](./POSTMAN_COMPLETE_GUIDE.md) - Full Postman integration guide
- [github-workflows-README.md](./github-workflows-README.md) - GitHub Actions overview