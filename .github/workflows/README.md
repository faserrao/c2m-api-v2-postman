# GitHub Actions Workflows

This directory contains GitHub Actions workflow definitions for continuous integration, deployment, and automation of the C2M API project.

## Directory Contents

### Active Workflows

#### `api-ci-cd.yml`
Main CI/CD pipeline that orchestrates the complete build, test, and deployment process.
- **Triggers**: Push to main, pull requests, manual dispatch
- **Jobs**: Build OpenAPI spec, test with mock servers, publish to Postman, deploy documentation
- **Features**: Drift detection, auto-commit of generated files, artifact uploads

#### `pr-drift-check.yml`
Pull request validation workflow that ensures generated files are committed.
- **Triggers**: Pull requests only
- **Purpose**: Prevents drift between source files and generated artifacts
- **Actions**: Comments on PR with fix instructions if drift detected

#### `deploy-docs.yml`
Documentation deployment workflow for GitHub Pages.
- **Triggers**: Successful completion of api-ci-cd workflow
- **Deploys**: API documentation to GitHub Pages
- **Uses**: Git worktree for clean deployment

#### `lint-openapi.yaml`
OpenAPI specification linting workflow.
- **Triggers**: Changes to OpenAPI files
- **Tools**: Spectral linter with custom rules
- **Purpose**: Ensures API spec quality and consistency

#### `openapi-ci.yml`
OpenAPI-specific CI workflow for spec validation.
- **Triggers**: Changes to data dictionary or OpenAPI files
- **Actions**: Validates spec structure, checks for breaking changes

### Experimental Workflows (OtherActions/)

#### `OtherActions/CIToInstalll/spec-to-postman.yml`
Alternative Postman integration approach.
- **Status**: Experimental
- **Purpose**: Direct spec to Postman conversion

#### `OtherActions/WasWorking/`
Previously working workflows kept for reference.
- Contains older versions of deployment and linting workflows
- Useful for rollback or debugging

## Workflow Dependencies

### Required Secrets
- `POSTMAN_API_KEY` - For Postman API operations
- `GITHUB_TOKEN` - Automatically provided by GitHub

### Environment Variables
- `POSTMAN_WORKSPACE_ID` - Target Postman workspace
- `NODE_VERSION` - Node.js version for builds
- `PYTHON_VERSION` - Python version for scripts

## Common Workflow Patterns

### 1. Conditional Execution
```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

### 2. Artifact Sharing
```yaml
- uses: actions/upload-artifact@v3
  with:
    name: openapi-spec
    path: openapi/
```

### 3. Auto-commit Pattern
```yaml
- name: Commit changes
  run: |
    git config --local user.email "action@github.com"
    git config --local user.name "GitHub Action"
    git add .
    git diff --staged --quiet || git commit -m "Auto-update generated files"
```

## Troubleshooting

### Common Issues

1. **Postman API Errors**
   - Check API key is valid and has correct permissions
   - Verify workspace ID exists

2. **Build Failures**
   - Ensure all dependencies are installed
   - Check Node/Python versions match requirements

3. **Deployment Issues**
   - Verify GitHub Pages is enabled in repository settings
   - Check branch protection rules don't block deployments

### Debugging Workflows

1. Enable debug logging:
   ```yaml
   env:
     ACTIONS_STEP_DEBUG: true
   ```

2. Add debug steps:
   ```yaml
   - name: Debug Info
     run: |
       echo "Event: ${{ github.event_name }}"
       echo "Ref: ${{ github.ref }}"
   ```

## Best Practices

1. **Use Specific Versions**: Pin action versions (e.g., `actions/checkout@v4`)
2. **Minimize Permissions**: Use least privilege principle
3. **Cache Dependencies**: Speed up builds with caching
4. **Fail Fast**: Set `fail-fast: true` in matrix builds
5. **Timeout Limits**: Set reasonable timeouts to prevent hanging

## Adding New Workflows

1. Create workflow file in this directory
2. Follow naming convention: `purpose-action.yml`
3. Include clear documentation in workflow file
4. Test in feature branch before merging
5. Update this README with workflow details

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Project CI/CD Guide](../../README.md#cicd-pipeline-github-actions)
- [Makefile Targets](../../Makefile)
