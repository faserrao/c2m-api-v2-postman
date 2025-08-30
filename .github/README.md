# GitHub Configuration Directory

This directory contains GitHub-specific configuration files and workflows for the C2M API project.

## Directory Structure

```
.github/
├── workflows/              # GitHub Actions workflow definitions
│   ├── api-ci-cd.yml      # Main CI/CD pipeline
│   ├── pr-drift-check.yml # PR validation workflow
│   ├── deploy-docs.yml    # Documentation deployment
│   ├── lint-openapi.yaml  # OpenAPI specification linting
│   ├── openapi-ci.yml     # OpenAPI CI workflow
│   └── OtherActions/      # Alternative/experimental workflows
└── README.md              # This file
```

## Key Components

### Workflows Directory
Contains all GitHub Actions workflow definitions. See [workflows/README.md](workflows/README.md) for detailed documentation.

### Issue Templates (Coming Soon)
Standardized templates for bug reports and feature requests.

### Pull Request Templates (Coming Soon)
Templates to ensure consistent PR descriptions.

## Configuration Best Practices

1. **Workflow Security**: Use environment secrets for sensitive data
2. **Permissions**: Grant minimal required permissions to workflows
3. **Reusability**: Use composite actions for common tasks
4. **Testing**: Test workflows in feature branches before merging

## Related Documentation

- [Workflows Documentation](workflows/README.md)
- [Root README](../README.md)
- [CI/CD Pipeline Guide](../README.md#cicd-pipeline-github-actions)
