# Security Repository GitHub Setup Guide

## Overview

This guide explains how to integrate the C2M API v2 security repository into the build process. The security repository contains authentication components that are kept separate from the main API repository for security isolation.

## Repository Structure

The C2M API v2 system uses two repositories:
1. **Main Repository** (`c2m-api-repo`) - Contains API definitions, build system, and documentation
2. **Security Repository** (`c2m-api-v2-security`) - Contains authentication implementation and sensitive components

## Setup Instructions

### 1. Create Personal Access Token (PAT)

The GitHub Actions workflow needs access to both repositories. Create a PAT with appropriate permissions:

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic) with scopes:
   - `repo` (full control of private repositories)
   - `workflow` (update GitHub Action workflows)
3. Save the token securely

### 2. Add Repository Secret

Add the PAT to the main repository as a secret:

1. Navigate to main repository Settings → Secrets and variables → Actions
2. Create new repository secret:
   - Name: `SECURITY_REPO_TOKEN`
   - Value: Your PAT from step 1

### 3. Configure Workflow

The `api-ci-cd.yml` workflow automatically checks out both repositories:

```yaml
- name: Checkout security repository
  uses: actions/checkout@v3
  with:
    repository: ${{ github.repository_owner }}/c2m-api-v2-security
    token: ${{ secrets.SECURITY_REPO_TOKEN }}
    path: ../c2m-api-v2-security
```

## Local Development

For local development, clone both repositories as siblings:

```bash
parent-directory/
├── c2m-api-repo/
└── c2m-api-v2-security/
```

The build system automatically detects and uses the security repository when present.

## Security Considerations

1. **Separation of Concerns**: Authentication logic is isolated from API definitions
2. **Access Control**: Only authorized workflows can access the security repository
3. **Token Rotation**: Regularly rotate the PAT for security
4. **Audit Trail**: All cross-repository access is logged in GitHub

## Troubleshooting

### Workflow Cannot Access Security Repository

**Symptoms**: CI/CD fails with "repository not found" or authentication errors

**Solutions**:
1. Verify PAT has not expired
2. Ensure PAT has correct permissions
3. Check secret name matches exactly: `SECURITY_REPO_TOKEN`
4. Confirm repository path is correct

### Local Build Cannot Find Security Components

**Symptoms**: Build works in CI but fails locally

**Solutions**:
1. Clone security repository as sibling to main repository
2. Ensure directory names match exactly
3. Check file permissions on security repository

## Integration Points

The security repository integrates at these points:

1. **Authentication Overlay**: Provides auth configuration for OpenAPI
2. **Test Scripts**: Supplies JWT handling for Postman tests
3. **Documentation**: Contributes auth-specific documentation
4. **Mock Data**: Provides example tokens and credentials

## Maintenance

### Regular Tasks

1. **Update Dependencies**: Keep security components current
2. **Rotate Secrets**: Change PAT every 90 days
3. **Audit Access**: Review who has access to security repository
4. **Sync Versions**: Ensure compatibility between repositories

### Version Compatibility

Both repositories should use compatible versions:
- Check `package.json` for matching dependency versions
- Verify OpenAPI specification versions align
- Test integration after major updates

---

*Last Updated: 2025-09-15*