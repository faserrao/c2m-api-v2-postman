# C2M_API_V3

End-to-end workflow for generating an OpenAPI spec from a data dictionary, building a Postman collection, publishing a Postman Spec, spinning up a mock server (Prism + Postman), running Newman tests, and serving Redoc docs — all from a single Makefile.

---

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Project Layout](#project-layout)
- [Configuration](#configuration)
- [Quickstart](#quickstart)
  - [Built-in Debugging (Run These If Anything Fails)](#built-in-debugging-run-these-if-anything-fails)
- [Common Tasks](#common-tasks)
- [Targets Reference](#targets-reference)
- [Troubleshooting](#troubleshooting)
- [HTTP Call Diagram](#http-call-diagram)
- [Debugging Playbook](#debugging-playbook)

---

## Overview

This repo automates:

1. Convert EBNF **Data Dictionary → OpenAPI YAML**
2. Lint & diff OpenAPI (`@redocly/cli`, `@stoplight/spectral-cli`, `openapi-diff`)
3. Generate **Postman Collection** from the OpenAPI
4. Upload **linked collection** to Postman; optionally publish a **Postman Spec**
5. Produce a **testing collection** (examples + default tests), validate & upload
6. Create **Postman Mock Server** and **Environment**
7. Run tests locally against **Prism** and against **Postman Mock**
8. Build & serve **Redoc** docs

Everything is orchestrated by `make postman-collection-build-and-test`.

---

## Prerequisites

- macOS/Linux with **bash** and **make**
- **Node.js** and **npm/npx**
- **Homebrew** (for `openapi-diff`), or install `openapi-diff` another way
- **Postman API Key** (saved in `.env` as `POSTMAN_SERRAO_API_KEY` or `POSTMAN_C2M_API_KEY`)
- `jq`, `diff`, `curl`, `git`, `python3` (venv is auto-managed)

---

## Project Layout

```
postman/ # Generated artifacts, payloads, debug outputs
generated/ # Built collections (raw/test/fixed/etc.)
*.txt / *.json # IDs, payloads, debug, upload logs

openapi/ # Source OpenAPI spec(s)
data_dictionary/ # EBNF source
scripts/ # Generators, fixers, jq filters, add tests, etc.
docs/ # Redoc output & static server
```

---

## Configuration

Create a `.env` in repo root (loaded automatically by the Makefile):

```ini
# Postman
POSTMAN_SERRAO_API_KEY=REDACTED
# or
# POSTMAN_C2M_API_KEY=REDACTED

# Workspace
POSTMAN_WS=d8a1f479-a2aa-4471-869e-b12feea0a98c

# Optional: token used in requests/tests
TOKEN=dummy-token
```

The Makefile sets:

```
POSTMAN_Q_ID := ?workspaceId=$(POSTMAN_WS) for /apis and /specs
POSTMAN_Q := ?workspace=$(POSTMAN_WS) for /collections, /mocks, /environments
```

---

## Quickstart

Install toolchain and bootstrap venv (dependencies handled automatically later too):

```bash
make install
```

(If you’re starting from an EBNF data dictionary) Generate the OpenAPI and lint:

```bash
make postman-dd-to-openapi
# or, if the spec already exists:
make lint
```

Run the full pipeline (build collections, upload, create mock, run tests, build docs, serve docs):

```bash
make postman-collection-build-and-test
```

This will:

- Log in to Postman
- Import the OpenAPI into the workspace
- Generate & upload the linked collection
- (Optionally) publish a Postman Spec if RUN_FULL_PUBLISH=1
- Build the testing collection + examples + tests
- Auto-fix/validate and upload the testing collection
- Create a Postman Mock + Environment and wire them together
- Start Prism and run Newman tests against both Prism and the Postman Mock
- Build and serve Redoc docs at http://localhost:8080

---

## Built-in Debugging (Run These If Anything Fails)

If any step fails, run the debug bundle first:

```bash
make postman-api-debug-B
```

This saves:

- /me → postman/debug-me.json
- /apis?workspaceId=... → postman/debug-apis.json
- /specs?workspaceId=... → postman/debug-specs.json

Then, for quick manual checks:

```bash
# API key works?
curl -sL "https://api.getpostman.com/me"   -H "X-Api-Key: $POSTMAN_API_KEY" | jq .

# APIs in your workspace?
curl -sL "https://api.getpostman.com/apis?workspaceId=$POSTMAN_WS"   -H "X-Api-Key: $POSTMAN_API_KEY" | jq '.apis[] | {id,name}'

# Collections in your workspace?
curl -sL "https://api.getpostman.com/collections?workspace=$POSTMAN_WS"   -H "X-Api-Key: $POSTMAN_API_KEY" | jq '.collections[] | {uid,name}'

# Environments in your workspace?
curl -sL "https://api.getpostman.com/environments?workspace=$POSTMAN_WS"   -H "X-Api-Key: $POSTMAN_API_KEY" | jq '.environments[] | {uid,name}'

# Mocks in your workspace?
curl -sL "https://api.getpostman.com/mocks?workspace=$POSTMAN_WS"   -H "X-Api-Key: $POSTMAN_API_KEY" | jq '.mocks[] | {id,uid,name,mockUrl}'
```

If you see trailing spaces or blank URLs in logs, your shell may be introducing whitespace; re-run make in a clean shell session and ensure your .env has no trailing spaces.

---

## Common Tasks

```bash
# Build collection, upload, create mock, run tests, docs build & serve
make postman-collection-build-and-test

# Start just Prism (uses the spec with examples)
make prism-start
make prism-status
make prism-stop

# Run Newman tests vs Prism
make prism-mock-test

# Run Newman tests vs Postman Mock
make postman-mock

# Clean Postman resources in the workspace (careful!)
make postman-cleanup-all
```

---

## Targets Reference

### Core
- install — install CLI tools via npm/brew
- venv — create/update Python venv used by generators
- postman-dd-to-openapi — (EBNF → OpenAPI) + lint
- lint — lint OpenAPI via Redocly & Spectral
- diff — diff current spec vs origin/main

### Build & Publish
- postman-collection-build-and-test — main pipeline (login → import → collections → tests → mocks → docs)
- postman-api-full-publish — delete all specs in workspace, create a fresh spec

### Collections
- postman-api-linked-collection-generate — OpenAPI → collection
- postman-collection-upload — upload linked collection
- postman-testing-collection-generate — prepare testing collection
- postman-collection-add-examples — add random examples
- postman-collection-merge-overrides — merge custom/overrides.json
- postman-collection-add-tests — inject default tests (allowed codes)
- postman-collection-auto-fix / postman-collection-fix-v2 / postman-collection-validate
- postman-collection-upload-test — upload testing collection

### Mocks & Envs
- postman-mock-create — create Postman mock (workspace-scoped)
- postman-env-create → postman-env-upload — generate & upload env
- update-mock-env — point mock to collection+env

### Docs
- docs-build — build Redoc + bundled OpenAPI
- docs-serve / docs-serve-bg / docs-stop

### Debug
- postman-api-debug-B — verifies /me, lists APIs/specs for workspace
- postman-workspace-debug — prints current POSTMAN_WS

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| curl: (3) URL rejected: Malformed input to a URL function | Trailing spaces or CRLF in query (e.g. ?workspace=... ) | Ensure .env has no trailing spaces; re-open shell; rerun. |
| curl: (56) 400/404 when creating/updating mock/env | Using uid vs id wrong, or entity not in this workspace | Re-list entities (see Quickstart debug) and use the exact identifier expected by that endpoint. |
| Env upload fails | postman/mock-env.json missing or malformed | Regenerate with make postman-env-create, verify JSON. |
| Prism won’t start | Spec path wrong or in-use port | Confirm PRISM_SPEC file exists; make prism-stop then make prism-start. |
| Newman tests fail | Base URL or token not set | Confirm POSTMAN_MOCK_URL/PRISM_MOCK_URL and TOKEN are injected (Makefile does this). |

---

## HTTP Call Diagram

```
Data Dictionary (EBNF)
       │
       ├─(scripts/ebnf_to_openapi_*.py)──▶ OpenAPI YAML
       │                                    ├─ lint/diff (redocly/spectral/openapi-diff)
       │                                    └─ Postman import (/apis?workspaceId=...)
       │                                                 │
       │                        ┌────────── linked collection (COPY_COLLECTION)
       │                        ▼
       └────► openapi-to-postmanv2 ──▶ collection.json ──▶ upload (/collections?workspace=...)
                                      │
                                      ├─ make testing collection (+examples +tests +fix)
                                      └─ upload test collection

Postman Environment JSON ──▶ upload (/environments?workspace=...)
Postman Mock Server      ──▶ create (/mocks?workspace=...) → update with collection+env

Prism (local) ◀────────── run tests (Newman) ───────────▶ Postman Mock

Redoc build/serve → http://localhost:8080
```

---

## Debugging Playbook

These steps help isolate and fix issues with Postman API calls in this project.

1) Verify API key & workspace
```bash
# Check API key is valid and returns account info
curl -s --location "https://api.getpostman.com/me"   --header "X-Api-Key: $POSTMAN_API_KEY" | jq .

# List workspaces to confirm POSTMAN_WS is correct
curl -s --location "https://api.getpostman.com/workspaces"   --header "X-Api-Key: $POSTMAN_API_KEY" | jq '.workspaces[] | {id, name}'
```

2) Check APIs in workspace
```bash
curl -s --location "https://api.getpostman.com/apis?workspaceId=$POSTMAN_WS"   --header "X-Api-Key: $POSTMAN_API_KEY" | jq '.apis[] | {id, name}'
```

3) Check collections in workspace
```bash
curl -s --location "https://api.getpostman.com/collections?workspace=$POSTMAN_WS"   --header "X-Api-Key: $POSTMAN_API_KEY" | jq '.collections[] | {uid, name}'
```

4) Check environments in workspace
```bash
curl -s --location "https://api.getpostman.com/environments?workspace=$POSTMAN_WS"   --header "X-Api-Key: $POSTMAN_API_KEY" | jq '.environments[] | {uid, name}'
```

5) Check mocks in workspace
```bash
curl -s --location "https://api.getpostman.com/mocks?workspace=$POSTMAN_WS"   --header "X-Api-Key: $POSTMAN_API_KEY" | jq '.mocks[] | {id, uid, name, mockUrl}'
```

---

### Common Fix Patterns

- Malformed input to URL function → Check for trailing spaces in .env or echoed URLs.
- 404 Not Found → Ensure the id/uid you’re using exists and belongs to the same workspace.
- Empty jq output → That entity type may not exist in the workspace yet.
- Env upload fails → Ensure postman/mock-env.json exists (run make postman-env-create).
