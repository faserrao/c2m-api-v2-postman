# Security Repository Documentation Migration Plan

## Overview

Many documents currently in the c2m-api-v2-security repo are user-facing guides that belong in the main c2m-api-repo. This plan outlines which docs to move, which to keep, and how to consolidate redundant information.

## Documents to Move to Main Repo

### 1. Postman Setup & Usage
**Move these:**
- `POSTMAN_SETUP_INSTRUCTIONS.md` → Merge into a comprehensive `POSTMAN_USER_GUIDE.md`
- `POSTMAN_REBUILD_SUMMARY.md` → Merge into `POSTMAN_USER_GUIDE.md`
- `COMPLETE_REBUILD_SUMMARY.md` → Extract Postman-specific parts

**Rationale:** Users need Postman instructions in the main repo where they're working with the API.

### 2. Authentication Guides
**Move these:**
- `API_AUTH_ENDPOINTS_GUIDE.md` → Main repo as `AUTH_ENDPOINTS_GUIDE.md`
- `C2M_AUTH_API_TESTING_GUIDE.md` → Main repo as `AUTH_TESTING_GUIDE.md`
- `C2M_AUTH_FLOW_COMPLETE_GUIDE.md` → Main repo as `AUTH_FLOW_GUIDE.md`
- `CUSTOMER_ONBOARDING_GUIDE.md` → Main repo (users need this for integration)

**Rationale:** API consumers need auth documentation where they're implementing.

### 3. General Documentation
**Move these:**
- `JWT-Security-Deep-Dive.md` → Useful for API consumers understanding security
- `V1_TO_V2_MIGRATION_STRATEGY.md` → Users migrating need this in main repo

## Documents to Keep in Security Repo

### 1. Implementation Details
**Keep these:**
- `COGNITO_INTEGRATION_GUIDE.md` - AWS-specific implementation
- `cognito-auth-app-README.md` - CDK app details
- `ARCHITECTURE_SUMMARY.md` - Internal architecture
- `IMPLEMENTATION_SUMMARY.md` - Implementation specifics

### 2. Security Analysis
**Keep these:**
- `C2M-API-V2-Security-Analysis.md` - Internal security assessment
- `Endpoint-Security-Analysis.md` - Security team reference
- `Payment-Security-Analysis.md` - Sensitive payment security details
- `Security-Implementation-Guide.md` - Implementation details

### 3. Test Results & Internal Docs
**Keep these:**
- All `*_TEST_RESULTS.md` files - Internal testing records
- `DUAL_URL_SOLUTION.md` - Implementation decision record
- `REBUILD_PROCESS.md` - Internal process documentation

## Consolidation Plan

### 1. Create Unified Postman Guide
Combine into `user-guides/POSTMAN_COMPLETE_GUIDE.md`:
- Setup instructions (from security repo)
- Workspace management (from main repo guides)
- Collection testing procedures
- Troubleshooting (updated with today's CI/CD fixes)
- JWT authentication setup

### 2. Create Unified Authentication Guide
Combine into `user-guides/AUTHENTICATION_GUIDE.md`:
- JWT overview and flow
- Endpoint documentation
- Testing procedures
- Customer onboarding
- Migration from V1

### 3. Update Existing Guides
- Remove redundant information
- Add cross-references
- Update with latest fixes (CI/CD, openapi-diff, etc.)

## Migration Steps

1. **Review & Extract**: Go through each security repo doc, extract user-facing content
2. **Consolidate**: Merge related content into comprehensive guides
3. **Update References**: Update all links and references
4. **Clean Up**: Remove migrated content from security repo
5. **Update READMEs**: Both repos' READMEs should clearly indicate what's where

## Benefits

1. **Single Source**: Users find everything in the main API repo
2. **Reduced Duplication**: No more maintaining similar docs in two places
3. **Better Organization**: Clear separation of user docs vs implementation docs
4. **Easier Maintenance**: Updates only needed in one place

## Timeline

This migration should be done incrementally:
1. Start with Postman guides (high user impact)
2. Move auth guides next
3. Clean up and consolidate
4. Update all cross-references

---

*Created: 2025-09-08*
*Purpose: Plan documentation reorganization between repositories*