# C2M API Ecosystem Architecture Diagram

## High-Level Architecture

```mermaid
graph TB
    subgraph "GitHub Repositories"
        A[c2m-api-repo<br/>Source Code] 
        B[c2m-api-artifacts<br/>Generated Files]
        C[c2m-api-v2-security<br/>Auth System]
    end
    
    subgraph "Local Development"
        D[Local Clone<br/>of c2m-api-repo]
        E[Local Artifacts<br/>../c2m-api-artifacts]
    end
    
    subgraph "CI/CD Pipeline"
        F[GitHub Actions<br/>Workflows]
    end
    
    subgraph "External Services"
        G[Postman<br/>Personal Workspace]
        H[Postman<br/>Team Workspace]
        I[AWS<br/>Cognito Stack]
    end
    
    D -->|git push| A
    A -->|triggers| F
    F -->|builds & pushes| B
    F -->|updates| G
    F -->|updates| H
    C -->|deployed to| I
    D -->|make local-sync| E
    E -->|git pull| B
```

## Build Pipeline Flow

```mermaid
graph LR
    subgraph "Source Files"
        A1[EBNF Data Dictionary<br/>c2mapiv2-dd.ebnf]
        A2[OpenAPI Overlays<br/>overlays/*.yaml]
        A3[Custom Tests<br/>custom/*.json]
        A4[Environments<br/>environments/*.json]
    end
    
    subgraph "Build Process"
        B1[EBNF to OpenAPI<br/>Converter]
        B2[Overlay Merger]
        B3[OpenAPI to Postman<br/>Converter]
        B4[Test Merger]
        B5[SDK Generator]
        B6[Doc Generator]
    end
    
    subgraph "Generated Artifacts"
        C1[OpenAPI Specs<br/>base & final]
        C2[Postman Collections<br/>7 variants]
        C3[SDKs<br/>Multiple Languages]
        C4[Documentation<br/>Redoc/Swagger]
    end
    
    A1 --> B1
    B1 --> C1
    A2 --> B2
    B2 --> C1
    C1 --> B3
    B3 --> C2
    A3 --> B4
    B4 --> C2
    C1 --> B5
    B5 --> C3
    C1 --> B6
    B6 --> C4
```

## Workflow Triggers

```mermaid
graph TD
    subgraph "Development Actions"
        DEV1[Edit EBNF File]
        DEV2[Edit Overlay]
        DEV3[Edit Custom Tests]
        DEV4[Create Branch]
        DEV5[Create PR]
        DEV6[Merge to Main]
    end
    
    subgraph "Local Triggers"
        LOCAL1[make openapi-build]
        LOCAL2[make postman-publish-*]
        LOCAL3[make local-sync]
    end
    
    subgraph "CI/CD Triggers"
        CI1[PR Checks<br/>Build & Validate]
        CI2[Main Deploy<br/>Full Pipeline]
    end
    
    subgraph "Effects"
        EFF1[Local Generated Files]
        EFF2[Postman Updated]
        EFF3[Artifacts Repo Updated]
        EFF4[Both Workspaces Updated]
    end
    
    DEV1 --> LOCAL1
    DEV2 --> LOCAL1
    DEV3 --> LOCAL2
    LOCAL1 --> EFF1
    LOCAL2 --> EFF2
    LOCAL3 --> EFF3
    
    DEV4 --> DEV5
    DEV5 --> CI1
    DEV6 --> CI2
    CI2 --> EFF3
    CI2 --> EFF4
```

## Local vs CI/CD Execution

```mermaid
graph TB
    subgraph "Local Execution"
        L1[Developer Machine]
        L2[make commands]
        L3[Direct Postman API calls]
        L4[Manual git operations]
        L5[Can target specific workspace]
    end
    
    subgraph "CI/CD Execution"
        C1[GitHub Actions Runner]
        C2[Automated workflows]
        C3[Uses GitHub Secrets]
        C4[Automatic git push]
        C5[Reads .postman-target file]
    end
    
    subgraph "Common Elements"
        M1[Same Makefile targets]
        M2[Same build scripts]
        M3[Same validation rules]
    end
    
    L1 --> L2
    L2 --> M1
    L3 --> L5
    L4 --> L1
    
    C1 --> C2
    C2 --> M1
    C3 --> C1
    C4 --> C1
    C5 --> C1
    
    M1 --> M2
    M2 --> M3
```

## Repository Relationships

```mermaid
graph LR
    subgraph "c2m-api-repo"
        direction TB
        SR1[Source EBNF]
        SR2[Overlays]
        SR3[Custom Tests]
        SR4[Makefile]
        SR5[CI/CD Workflows]
    end
    
    subgraph "c2m-api-artifacts"
        direction TB
        AR1[OpenAPI Specs]
        AR2[Postman Collections]
        AR3[Documentation]
        AR4[SDKs]
        AR5[Metadata]
    end
    
    subgraph "c2m-api-v2-security"
        direction TB
        SEC1[CDK App]
        SEC2[Lambda Functions]
        SEC3[Auth Endpoints]
    end
    
    SR4 -->|builds| AR1
    SR4 -->|generates| AR2
    SR4 -->|creates| AR3
    SR4 -->|produces| AR4
    AR1 -->|references| SEC3
    
    SR5 -->|pushes to| AR5
```

## Key File Paths

```
Local Development:
├── c2m-api-repo/                    [Main working directory]
│   ├── data_dictionary/
│   │   └── c2mapiv2-dd.ebnf       [Source of truth]
│   ├── openapi/
│   │   └── overlays/              [Customizations]
│   ├── postman/
│   │   ├── custom/                [Test files]
│   │   └── environments/          [Env configs]
│   ├── scripts/                   [Build tools]
│   ├── Makefile                   [Orchestration]
│   └── .postman-target           [Workspace selector]
│
├── c2m-api-artifacts/             [Generated files]
│   ├── openapi/                   [Built specs]
│   ├── postman/                   [Built collections]
│   ├── docs/                      [Built docs]
│   └── sdks/                      [Built SDKs]
│
└── c2m-api-v2-security/          [Auth system]
    └── cognito-auth-app/         [CDK application]
```

## Environment Variables & Secrets

```yaml
Local (.env file):
  POSTMAN_SERRAO_API_KEY: Personal workspace key
  POSTMAN_C2M_API_KEY: Team workspace key

GitHub Secrets:
  POSTMAN_SERRAO_API_KEY: Personal workspace key
  POSTMAN_C2M_API_KEY: Team workspace key
  SECURITY_REPO_TOKEN: PAT for artifacts repo

Workspace IDs (in Makefile):
  Personal: d8a1f479-a2aa-4471-869e-b12feea0a98c
  Team: c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1
```

## Common Commands Reference

```bash
# Local Development
make help                            # Show all targets
make openapi-build                   # Build OpenAPI only
make postman-collection-build        # Build Postman only
make postman-test-local             # Test with Prism
make postman-publish-personal       # Publish to personal
make postman-publish-team          # Publish to team
make postman-publish-both          # Publish to both
make local-sync                     # Sync to artifacts

# Full Pipeline
make postman-cleanup-all            # Clean everything
make postman-instance-build-and-test # Complete rebuild

# Debugging
make show-vars                      # Show variables
make postman-auth-test             # Test API keys
make artifacts-status              # Check sync status
```