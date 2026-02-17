# Workflow Diagrams

Visual flowcharts for all C2M API V2 workflows.

## Table of Contents

1. [Complete System Pipeline](#complete-system-pipeline)
2. [Developer Editing Workflow](#developer-editing-workflow)
3. [Safe Push Workflow](#safe-push-workflow)
4. [CI/CD Automation Workflow](#cicd-automation-workflow)
5. [Local Testing Workflow](#local-testing-workflow)
6. [Emergency Rollback Workflow](#emergency-rollback-workflow)
7. [Decision Trees](#decision-trees)

---

## Complete System Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EBNF Data Dictionary                             │
│                  (Single Source of Truth)                           │
│                                                                     │
│  data_dictionary/c2mapiv2-dd.ebnf                                  │
│  - 904 lines of API structure definitions                          │
│  - Defines: endpoints, fields, types, validation rules            │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │  Python Translator  │
        │                     │
        │  ebnf_to_openapi_   │
        │  dynamic_v3.py      │
        └──────────┬──────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OpenAPI Specification                            │
│                                                                     │
│  openapi/c2mapiv2-openapi-spec-base.yaml                          │
│  - 719 lines of API documentation                                  │
│  - Defines: paths, schemas, responses, security                    │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
                   ├───────────────┬────────────────┬────────────────┐
                   │               │                │                │
                   ▼               ▼                ▼                ▼
         ┌─────────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
         │  Postman    │   │   Docs   │   │   SDKs   │   │  Mock    │
         │ Collections │   │          │   │          │   │  Server  │
         └─────────────┘   └──────────┘   └──────────┘   └──────────┘
               │                 │              │              │
               ▼                 ▼              ▼              ▼
         3 Collections     GitHub Pages   11 Languages  Postman Mock
         - Linked          - Redocly      - Python      - 9 Endpoints
         - Test            - Interactive  - JavaScript  - Test Data
         - Use Cases       - Searchable   - Go, etc.    - Examples
```

---

## Developer Editing Workflow

```
START
  │
  ▼
┌────────────────────┐
│ Edit EBNF File     │
│                    │
│ c2mapiv2-dd.ebnf   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────────────────┐
│ Run Validation                 │
│                                │
│ ./scripts/validate-before-     │
│ commit.sh                      │
└─────────┬──────────────────────┘
          │
          ├─── NO ─────┐
          │            ▼
          │     ┌────────────┐
          │     │ Fix Errors │
          │     └──────┬─────┘
          │            │
          │            └──────┐
          │                   │
          YES                 │
          │                   │
          ▼                   │
┌────────────────────────┐    │
│ Preview Changes        │◄───┘
│                        │
│ ./scripts/preview-     │
│ ebnf-changes.sh        │
└─────────┬──────────────┘
          │
          ▼
    ┌──────────┐
    │ Review   │
    │ Diff     │
    └────┬─────┘
         │
         ▼
    ┌──────────────┐
    │ Changes OK?  │
    └────┬────┬────┘
         │    │
         NO   YES
         │    │
         │    ▼
         │  ┌────────────────┐
         │  │ Safe Push      │
         │  │                │
         │  │ ./scripts/     │
         │  │ safe-push.sh   │
         │  └────┬───────────┘
         │       │
         │       ▼
         │  ┌─────────────────┐
         │  │ Git Commit      │
         │  │ & Push          │
         │  └────┬────────────┘
         │       │
         │       ▼
         │  ┌─────────────────┐
         │  │ CI/CD Triggers  │
         │  │ Automatically   │
         │  └────┬────────────┘
         │       │
         │       ▼
         │     END
         │
         └────► Revise Changes
```

---

## Safe Push Workflow

Detailed breakdown of `./scripts/safe-push.sh`

```
START
  │
  ▼
┌──────────────────────┐
│ STEP 1: Validate     │
│                      │
│ Check EBNF syntax    │
│ Check duplicates     │
│ Check common issues  │
└─────────┬────────────┘
          │
          ├─── FAIL ───► EXIT
          │
          YES
          │
          ▼
┌──────────────────────┐
│ STEP 2: Generate     │
│                      │
│ Run EBNF → OpenAPI   │
│ translator           │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ STEP 3: Preview      │
│                      │
│ Show diffs           │
│ Show stats           │
│ Check breaking       │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ STEP 4: Local Build? │
│                      │
│ Optional 8-min test  │
└─────────┬───┬────────┘
          │   │
          NO  YES
          │   │
          │   ▼
          │ ┌────────────────┐
          │ │ Full Pipeline  │
          │ │ - Collections  │
          │ │ - Mock Server  │
          │ │ - Tests        │
          │ └────┬───────────┘
          │      │
          │      ├─── FAIL ───► EXIT
          │      │
          │      YES
          │      │
          └──────┘
                 │
                 ▼
┌──────────────────────┐
│ STEP 5: Show Files   │
│                      │
│ git status --short   │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ STEP 6: Confirm?     │
│                      │
│ Ready to push? (y/n) │
└─────────┬───┬────────┘
          │   │
          NO  YES
          │   │
          │   ▼
          │ ┌────────────────┐
          │ │ STEP 7: Push   │
          │ │                │
          │ │ git commit     │
          │ │ git push       │
          │ └────┬───────────┘
          │      │
          │      ▼
          │    END
          │
          └───► ABORT
```

---

## CI/CD Automation Workflow

GitHub Actions workflow when pushing to main.

```
┌────────────────────┐
│ Developer Pushes   │
│ to Main Branch     │
└─────────┬──────────┘
          │
          ▼
┌───────────────────────────────────────┐
│ GitHub Actions Workflow Triggered    │
│                                       │
│ .github/workflows/api-ci-cd.yml       │
└─────────┬─────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────┐
│ JOB: Build API Spec, Collections, Docs│
└─────────┬──────────────────────────────┘
          │
          ├──────────┬──────────┬──────────┬──────────┐
          │          │          │          │          │
          ▼          ▼          ▼          ▼          ▼
     ┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐ ┌──────┐
     │ Setup  │ │ EBNF │ │ OpenAPI│ │ Post │ │ Docs │
     │        │ │  →   │ │   →    │ │  →   │ │      │
     │        │ │ Open │ │ Postman│ │ Coll │ │      │
     │        │ │  API │ │        │ │      │ │      │
     └────────┘ └──────┘ └────────┘ └──────┘ └──────┘
          │
          ▼
┌────────────────────────────────────────┐
│ Auto-commit Generated Files            │
│                                        │
│ IF branch == main:                     │
│   - openapi/*.yaml                     │
│   - postman/generated/*.json           │
│   - docs/*                             │
└─────────┬──────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────┐
│ Publish to Postman Workspace           │
│                                        │
│ Target: .postman-target file          │
│ - "personal" OR "team"                │
│                                        │
│ Publishes:                             │
│ - 3 Collections                        │
│ - 1 API Definition                     │
│ - 1 Mock Server                        │
│ - 2 Environments                       │
└─────────┬──────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────┐
│ Copy to Artifacts Repository           │
│                                        │
│ c2m-api-v2-postman-artifacts           │
│ - OpenAPI specs                        │
│ - Postman collections                  │
│ - SDKs (11 languages)                  │
│ - Documentation                        │
└─────────┬──────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────┐
│ Deploy to GitHub Pages                 │
│                                        │
│ https://click2mail.github.io/          │
│ c2m-api-v2-postman-artifacts/          │
└─────────┬──────────────────────────────┘
          │
          ▼
        END
      (3-4 min)
```

---

## Local Testing Workflow

```
START
  │
  ▼
┌────────────────────────────────┐
│ Run Build Command              │
│                                │
│ make postman-instance-build-   │
│ with-tests                     │
└─────────┬──────────────────────┘
          │
          ├──────────┬──────────┬──────────┬──────────┐
          │          │          │          │          │
          ▼          ▼          ▼          ▼          ▼
     ┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐ ┌──────┐
     │ EBNF   │ │ Open │ │ Postman│ │ Mock │ │ Docs │
     │   →    │ │  API │ │        │ │      │ │      │
     │ OpenAPI│ │   →  │ │   →    │ │      │ │      │
     │        │ │ Post │ │  Mock  │ │      │ │      │
     │        │ │  man │ │        │ │      │ │      │
     └────────┘ └──────┘ └────────┘ └──────┘ └──────┘
                                         │
                                         ▼
                              ┌────────────────────┐
                              │ Start Prism Server │
                              │                    │
                              │ localhost:4010     │
                              └─────────┬──────────┘
                                        │
                                        ▼
                              ┌────────────────────┐
                              │ Run Tests          │
                              │                    │
                              │ Newman + Prism     │
                              │ 24 tests           │
                              └─────────┬──────────┘
                                        │
                                        ├─── FAIL ───► Review Logs
                                        │
                                        YES
                                        │
                                        ▼
                              ┌────────────────────┐
                              │ Start Docs Server  │
                              │                    │
                              │ localhost:8080     │
                              └─────────┬──────────┘
                                        │
                                        ▼
                                      END
                                  (15 minutes)
```

---

## Emergency Rollback Workflow

```
PROBLEM
  │
  ▼
┌────────────────────────┐
│ Identify Issue         │
│                        │
│ - Pipeline failed?     │
│ - Invalid spec?        │
│ - Breaking change?     │
└─────────┬──────────────┘
          │
          ▼
    ┌──────────┐
    │ Severity?│
    └────┬─────┘
         │
         ├─── LOW ───────────────┐
         │                       │
         ├─── MEDIUM ────────┐   │
         │                   │   │
         └─── HIGH ──┐       │   │
                     │       │   │
                     ▼       ▼   ▼
              ┌──────────────────────┐
              │ OPTION 1: Revert     │
              │                      │
              │ git revert HEAD      │
              │ git push             │
              └──────────┬───────────┘
                         │
                         ▼
                       END

              ┌──────────────────────┐
              │ OPTION 2: Fix Forward│
              │                      │
              │ Fix EBNF issue       │
              │ git commit && push   │
              └──────────┬───────────┘
                         │
                         ▼
                       END

              ┌──────────────────────┐
              │ OPTION 3: Reset      │
              │                      │
              │ git reset --hard     │
              │ git push --force     │
              └──────────┬───────────┘
                         │
                         ▼
                    ┌────────┐
                    │WARNING │
                    │        │
                    │Rewrites│
                    │History │
                    └────────┘
```

---

## Decision Trees

### When to Use Which Workflow

```
START
  │
  ▼
┌──────────────────┐
│ What are you     │
│ trying to do?    │
└────┬────┬────┬───┘
     │    │    │
     ▼    ▼    ▼
   EDIT TEST PUSH
     │    │    │
     │    │    │
     ▼    │    │
┌─────────────┐│    │
│Quick Edit?  ││    │
└────┬────┬───┘│    │
     │    │    │    │
     NO   YES  │    │
     │    │    │    │
     │    ▼    │    │
     │  ┌──────────────┐
     │  │ Safe Push    │
     │  │ ./scripts/   │
     │  │ safe-push.sh │
     │  └──────────────┘
     │         │    │
     ▼         │    │
┌─────────────┐│    │
│Local Build? ││    │
└────┬────┬───┘│    │
     │    │    │    │
     NO   YES  │    │
     │    │    │    │
     │    ▼    │    │
     │  ┌──────────────┐
     │  │ make postman-│
     │  │ instance-    │
     │  │ build-with-  │
     │  │ tests        │
     │  └──────────────┘
     │         │    │
     └─────────┘    │
                    │
                    ▼
              ┌──────────────┐
              │ git push     │
              │              │
              │ Triggers     │
              │ CI/CD        │
              └──────────────┘
```

### Validation Decision Tree

```
┌────────────────────┐
│ Run Validation     │
│                    │
│ ./scripts/validate-│
│ before-commit.sh   │
└─────────┬──────────┘
          │
          ▼
    ┌──────────┐
    │ Result?  │
    └────┬─────┘
         │
         ├─── "0 productions parsed" ───────┐
         │                                   ▼
         │                            ┌────────────┐
         │                            │ CRITICAL   │
         │                            │ Syntax     │
         │                            │ Error      │
         │                            └──────┬─────┘
         │                                   │
         │                                   ▼
         │                            Check for:
         │                            - Missing ;
         │                            - { string : string }
         │                            - Unmatched ( )
         │
         ├─── "Duplicate definition" ────────┐
         │                                    ▼
         │                             ┌────────────┐
         │                             │ Find & Fix │
         │                             │            │
         │                             │ grep ^name │
         │                             │ = file     │
         │                             └────────────┘
         │
         └─── "Valid" ──────────────────────┐
                                             ▼
                                      ┌────────────┐
                                      │ PROCEED    │
                                      │            │
                                      │ Continue   │
                                      │ to preview │
                                      └────────────┘
```

### CI/CD Trigger Decision

```
┌────────────────────┐
│ Push to Repository │
└─────────┬──────────┘
          │
          ▼
    ┌──────────┐
    │ Branch?  │
    └────┬─────┘
         │
         ├─── main ───────────────────┐
         │                            │
         ├─── PR ─────────────┐       │
         │                    │       │
         └─── Other Branch ───┘       │
                 │            │       │
                 ▼            ▼       ▼
            ┌──────────┐ ┌────────┐ ┌────────┐
            │ No CI/CD │ │PR Drift│ │Full    │
            │          │ │Check   │ │CI/CD   │
            │          │ │        │ │        │
            │          │ │Verify  │ │Build   │
            │          │ │commits │ │Publish │
            │          │ │match   │ │Deploy  │
            └──────────┘ └────────┘ └────────┘
```

### Breaking Change Decision

```
┌────────────────────┐
│ Preview Changes    │
│                    │
│ Check for:         │
│ - Removed paths    │
│ - Required fields  │
│ - Removed schemas  │
└─────────┬──────────┘
          │
          ▼
    ┌──────────────┐
    │ Breaking     │
    │ Changes?     │
    └────┬─────────┘
         │
         ├─── YES ────────────────────┐
         │                            │
         └─── NO ─────────────┐       │
                              │       │
                              ▼       ▼
                        ┌─────────┐ ┌─────────┐
                        │ Safe to │ │DECISION │
                        │ Deploy  │ │         │
                        │         │ │ Deploy? │
                        │ Push    │ │ Version?│
                        │ to main │ │ Notify? │
                        └─────────┘ └─────────┘
                                         │
                                         ├─── Abort ───► Fix
                                         │
                                         ├─── Version ─► Deploy with
                                         │                new major
                                         │                version
                                         │
                                         └─── Notify ──► Deploy with
                                                          migration
                                                          guide
```

---

## Time Estimates

| Workflow | Duration | When to Use |
|----------|----------|-------------|
| Validate EBNF | 10 sec | After every edit |
| Preview Changes | 20 sec | Before committing |
| Safe Push (no build) | 2 min | Quick iterations |
| Safe Push (with build) | 10 min | Before major push |
| Local Build (without tests) | 8 min | Quick validation |
| Local Build (with tests) | 15 min | Complete validation |
| CI/CD Pipeline | 3-4 min | Automatic on push |
| Emergency Rollback | 2 min | When pipeline fails |

---

## Quick Reference Commands

```bash
# Validation only
./scripts/validate-before-commit.sh

# Preview what will change
./scripts/preview-ebnf-changes.sh

# Complete workflow (recommended)
./scripts/safe-push.sh "Your commit message"

# Local build without tests (faster)
make postman-instance-build-without-tests

# Local build with tests (complete)
make postman-instance-build-with-tests

# Emergency rollback
git revert HEAD
git push origin main
```

---

## Next Steps

- Read [ROLLBACK.md](ROLLBACK.md) for detailed emergency procedures
- Read [NEW_DEVELOPER_QUICKSTART.md](NEW_DEVELOPER_QUICKSTART.md) for getting started
- Read [COMMON_EBNF_TASKS.md](COMMON_EBNF_TASKS.md) for specific editing tasks

---

**Remember**: The workflows are designed to catch errors early. Validate often, preview always, test when possible.
