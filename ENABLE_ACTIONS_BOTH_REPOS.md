# Enable GitHub Actions on Both Repositories

## Status: Repositories Are Now In Sync ✅

Both repositories now have the complete post-build validation system:
- ✅ faserrao/c2m-api-v2-postman (personal)
- ✅ click2mail/c2m-api-v2-postman (corporate)

## Enable Actions - Two Steps (2 minutes)

### Step 1: Enable on faserrao (Personal/Development)

**Direct link**: https://github.com/faserrao/c2m-api-v2-postman/settings/actions

1. Click the link above
2. Click **"Enable Actions on this repository"**
3. Done!

**Purpose**: Development and testing CI/CD
**Postman Target**: Personal workspace (POSTMAN_SERRAO_API_KEY)

---

### Step 2: Enable on click2mail (Corporate/Production)

**Direct link**: https://github.com/click2mail/c2m-api-v2-postman/settings/actions

1. Click the link above
2. Click **"Enable Actions on this repository"**
3. Done!

**Purpose**: Production CI/CD
**Postman Target**: Corporate workspace (POSTMAN_C2M_API_KEY)

---

## What Happens Next

### Both Workflows Will Run Independently

**faserrao repository**:
```
Trigger: git push origin main
├── Reads .postman-target file
├── Uses POSTMAN_SERRAO_API_KEY secret
├── Publishes to Personal Postman workspace
└── Runs post-build validation
```

**click2mail repository**:
```
Trigger: git push click2mail main
├── Reads .postman-target file
├── Uses POSTMAN_C2M_API_KEY secret
├── Publishes to Corporate Postman workspace
└── Runs post-build validation
```

### Immediate Workflow Triggers

Since the push to click2mail just happened, enabling Actions should trigger the workflow automatically.

**Monitor workflows**:

**faserrao**:
```bash
gh run list --repo faserrao/c2m-api-v2-postman --limit 5
```
Or visit: https://github.com/faserrao/c2m-api-v2-postman/actions

**click2mail**:
```bash
gh run list --repo click2mail/c2m-api-v2-postman --limit 5
```
Or visit: https://github.com/click2mail/c2m-api-v2-postman/actions

## Dual Repository Workflow

From now on, when you push code:

### Development (Personal)
```bash
# Your .git-context is already set to "personal"
git push origin main
# → Triggers faserrao workflow
# → Publishes to Personal Postman workspace
```

### Production (Corporate)
```bash
git push click2mail main
# → Triggers click2mail workflow
# → Publishes to Corporate Postman workspace
```

### Both at Once
```bash
git push origin main && git push click2mail main
# → Triggers BOTH workflows independently
# → Each publishes to its respective workspace
```

Or use the alias:
```bash
git ctx-push-both main
# → Pushes to both remotes
# → Triggers both CI/CD pipelines
```

## Validation Reports

After workflows complete, download validation reports from each:

**faserrao artifacts**:
```bash
gh run list --repo faserrao/c2m-api-v2-postman --limit 1 --json databaseId --jq '.[0].databaseId' | \
  xargs -I {} gh run download {} --repo faserrao/c2m-api-v2-postman --name validation-reports
```

**click2mail artifacts**:
```bash
gh run list --repo click2mail/c2m-api-v2-postman --limit 1 --json databaseId --jq '.[0].databaseId' | \
  xargs -I {} gh run download {} --repo click2mail/c2m-api-v2-postman --name validation-reports
```

## Expected Results

Both workflows should complete in 5-8 minutes with:

- ✅ **Build**: OpenAPI spec, Postman collections, docs generated
- ✅ **Publish**: Collections published to respective workspace
- ✅ **Validate**: Post-build validation runs
- ✅ **Artifacts**: Validation reports uploaded (30-day retention)

## Security Note

There's a Dependabot alert on click2mail repository:
```
39 vulnerabilities (6 critical, 16 high, 16 moderate, 1 low)
View: https://github.com/click2mail/c2m-api-v2-postman/security/dependabot
```

This is unrelated to the validation system - it's about npm dependencies. You may want to review and update dependencies separately.

## Quick Reference

| Action | faserrao | click2mail |
|--------|----------|------------|
| Enable Actions | https://github.com/faserrao/c2m-api-v2-postman/settings/actions | https://github.com/click2mail/c2m-api-v2-postman/settings/actions |
| View workflows | https://github.com/faserrao/c2m-api-v2-postman/actions | https://github.com/click2mail/c2m-api-v2-postman/actions |
| Postman workspace | Personal (SERRAO key) | Corporate (C2M key) |
| Use case | Development/testing | Production/team |

---

**Next Steps**:
1. Click "Enable Actions" on both repositories (2 clicks total)
2. Wait 5-8 minutes for workflows to complete
3. Review validation reports from both pipelines
