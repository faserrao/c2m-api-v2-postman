# Next Steps for C2M API Restoration

## Current State
- ✅ Created clean branch from Aug 30 snapshot
- ✅ Analyzed differences between clean and broken versions
- ✅ Created RESTORE_REPORT.md documenting all findings
- ✅ Created minimal-auth-patch.diff showing essential changes only
- ✅ Added auth-pre-request-abstract.js as the minimal hook

## Recommended Actions

### 1. Apply Minimal Auth Support (Optional)
If you want to add auth support to the main repo, apply only the minimal patch:

```bash
# Review the patch first
cat minimal-auth-patch.diff

# Apply the patch
git apply minimal-auth-patch.diff

# The patch adds:
# - Reference to security scripts directory
# - Single postman-auth-setup target
# - Integration into postman-create-test-collection
```

### 2. Move Auth Components to Security Repo
All auth-specific scripts from the broken backup should be moved to the security repo:

```bash
# These belong in c2m-api-v2-security/postman/scripts/:
- jwt-auth-provider.js
- cognito-pre-request.js (if needed)
- add_auth_examples.js

# These belong in c2m-api-v2-security/scripts/:
- fetch_aws_credentials.sh
```

### 3. Test the Clean State
Before making any changes:

```bash
# Test that everything works in the clean state
make postman-cleanup-all
make postman-instance-build-and-test
```

### 4. Create PR
Once satisfied with the restoration:

```bash
# Push the branch
git push origin chore/restore-pre-auth-state

# Create PR with:
# - Title: "Restore c2m-api-repo to clean state with minimal auth hooks"
# - Description: Reference the RESTORE_REPORT.md
# - Reviewers: Team members who understand the original architecture
```

## What NOT to Do

1. **Don't** apply the entire broken Makefile - it has 1000+ lines of redundancy
2. **Don't** copy over the scripts that overwrote originals (addInfo.js, flattenCollection.js)
3. **Don't** add auth-specific endpoints to the main repo's EBNF
4. **Don't** create duplicate environment management targets

## Key Principle

The main repo should remain focused on the core C2M API functionality. Authentication should be:
- Developed in the security repo
- Integrated via minimal hooks
- Tested separately before integration

## Questions to Consider

1. Do we even need auth in the main repo right now?
2. Should auth be tested fully in the security repo first?
3. Can the mock server testing work without auth for now?

Remember: It's easier to add features incrementally than to untangle a complex integration.