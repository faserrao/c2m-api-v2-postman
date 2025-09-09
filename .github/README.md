# GitHub Configuration Directory

This directory contains GitHub-specific configuration files and workflows for the C2M API project.

## Directory Structure

```
.github/
├── workflows/              # GitHub Actions workflow definitions
│   ├── api-ci-cd.yml      # Main CI/CD pipeline (primary workflow)
│   ├── pr-drift-check.yml # PR validation workflow
│   └── OtherActions/      # Alternative/experimental workflows
│       ├── deploy-docs.yml    # Documentation deployment
│       ├── lint-openapi.yaml  # OpenAPI specification linting
│       └── openapi-ci.yml     # OpenAPI CI workflow
└── README.md              # This file
```

## Key Components

### Primary Workflows

#### 1. **api-ci-cd.yml** - Main CI/CD Pipeline
The primary workflow that handles the complete build, test, and deployment pipeline.

**Triggers:**
- Push to `main` branch
- Pull requests to `main`
- Manual workflow dispatch

**Key Features:**
- Builds OpenAPI spec from EBNF data dictionary
- Generates and validates Postman collections
- Auto-commits generated files (main branch only)
- Publishes to Postman workspaces (based on `.postman-target` file)
- Deploys documentation to GitHub Pages
- Cleans up existing Postman resources before publishing

**Required Secrets:**
- `POSTMAN_API_KEY` - Your Postman API key
- `POSTMAN_WORKSPACE_ID` - Target workspace UUID (optional, uses default from .env)

#### 2. **pr-drift-check.yml** - Pull Request Validation
Ensures all generated files are up-to-date in pull requests.

**Features:**
- Runs on all PRs
- Regenerates all artifacts
- Compares with committed versions
- Comments on PR with specific fix instructions if drift detected
- Prevents "works on my machine" issues

### Workflows Directory
Contains all GitHub Actions workflow definitions. The main workflows are in the root, with experimental ones in `OtherActions/`.

### Workspace Publishing

The CI/CD pipeline supports publishing to different Postman workspaces:

1. **Personal Workspace** (default)
   - Create `.postman-target` with content: `personal`
   - Uses workspace from `.env` file

2. **Corporate Workspace**
   - Create `.postman-target` with content: `corporate`
   - Requires corporate workspace configuration

**How it works:**
- GitHub Actions reads `.postman-target` file
- Runs appropriate publish command: `make postman-publish-{target}`
- Cleans up existing resources before publishing

### Issue Templates (Coming Soon)
Standardized templates for bug reports and feature requests.

### Pull Request Templates (Coming Soon)
Templates to ensure consistent PR descriptions.

## Configuration Best Practices

1. **Workflow Security**: Use environment secrets for sensitive data
2. **Permissions**: Grant minimal required permissions to workflows
3. **Reusability**: Use composite actions for common tasks
4. **Testing**: Test workflows in feature branches before merging
5. **Workspace Target**: Always check `.postman-target` file before pushing
6. **Local Testing**: Run `make openapi-build postman-collection-build docs` before pushing

## Common GitHub Actions Commands

```bash
# View workflow runs
gh run list

# Watch a workflow run
gh run watch

# View workflow run details
gh run view [run-id]

# Trigger manual workflow
gh workflow run api-ci-cd.yml

# Debug failed workflow
gh run view [run-id] --log-failed
```

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|  
| Workflow fails with "jq error" | Fixed in latest version - uses portable jq syntax |
| Wrong workspace published | Check `.postman-target` file content |
| Postman resources not cleaned | Ensure API key has delete permissions |
| Documentation not deploying | Enable GitHub Pages in repository settings |
| PR shows "files out of sync" | Run commands shown in PR comment |

### Debugging Workflow Failures

1. **Check the Actions tab** for detailed logs
2. **Expand failed steps** to see exact error messages
3. **Look for the "Publish to Postman" step** - it shows which workspace is targeted
4. **Verify secrets** are properly configured
5. **Test locally first** with the same commands

## Related Documentation

- [Root README](../README.md)
- [CI/CD Pipeline Guide](../README.md#cicd-pipeline-github-actions)
- [BUILD-GUIDE.md](../BUILD-GUIDE.md) - Step-by-step build instructions
- [Makefile](../Makefile) - All available build commands
