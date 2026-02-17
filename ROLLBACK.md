# Emergency Rollback Procedures

What to do when things go wrong.

## Quick Decision Guide

| Situation | Severity | Action | Time |
|-----------|----------|--------|------|
| Validation fails locally | LOW | Fix & retry | 5 min |
| CI/CD workflow fails | MEDIUM | Revert commit | 2 min |
| Breaking change deployed | HIGH | Immediate revert | 2 min |
| Postman resources broken | HIGH | Rebuild resources | 10 min |
| Complete disaster | CRITICAL | Full restoration | 30 min |

---

## Table of Contents

1. [Before You Panic](#before-you-panic)
2. [Rollback Strategy 1: Git Revert](#rollback-strategy-1-git-revert)
3. [Rollback Strategy 2: Fix Forward](#rollback-strategy-2-fix-forward)
4. [Rollback Strategy 3: Hard Reset](#rollback-strategy-3-hard-reset)
5. [Postman Resource Recovery](#postman-resource-recovery)
6. [CI/CD Failure Recovery](#cicd-failure-recovery)
7. [Complete Disaster Recovery](#complete-disaster-recovery)
8. [Prevention Checklist](#prevention-checklist)

---

## Before You Panic

### Step 1: Assess the Situation

```bash
# Check git status
git status

# Check recent commits
git log --oneline -5

# Check GitHub Actions
# Visit: https://github.com/click2mail/c2m-api-v2-postman/actions
```

### Step 2: Identify the Problem

**Common Scenarios**:
- [ ] Validation error (caught locally)
- [ ] CI/CD workflow failed
- [ ] Postman resources broken
- [ ] Breaking change deployed
- [ ] OpenAPI spec invalid

### Step 3: Determine Severity

**LOW** (local only):
- Validation fails on your machine
- No commit made yet
- No one else affected

**MEDIUM** (committed but caught):
- CI/CD caught the error
- Not yet deployed to Postman
- Easy to revert

**HIGH** (deployed with issues):
- Changes pushed to Postman
- Clients may be affected
- Need immediate fix

**CRITICAL** (complete failure):
- Multiple systems broken
- Can't revert easily
- Need full restoration

---

## Rollback Strategy 1: Git Revert

**When to use**: You pushed a commit that breaks things, but want to keep git history clean.

### Advantages
- Preserves history (no force push)
- Safe for shared repositories
- Easy to understand what happened
- Reversible if needed

### Disadvantages
- Creates a new commit
- Doesn't truly "undo" (adds opposite change)

### Procedure

#### Step 1: Find the Bad Commit

```bash
# Show recent commits
git log --oneline -10

# Example output:
# a1b2c3d Add priority field to submitSingleDocParams
# e4f5g6h Fix duplicate definition
# i7j8k9l Update documentation
```

#### Step 2: Revert the Commit

```bash
# Revert the most recent commit
git revert HEAD

# Or revert specific commit by hash
git revert a1b2c3d
```

This opens your editor for the commit message:
```
Revert "Add priority field to submitSingleDocParams"

This reverts commit a1b2c3d because it introduced
validation errors in the OpenAPI spec.
```

#### Step 3: Push the Revert

```bash
git push origin main
```

#### Step 4: Verify

```bash
# CI/CD should trigger automatically
# Monitor: https://github.com/click2mail/c2m-api-v2-postman/actions

# After 3-4 minutes, check:
# - CI/CD workflow succeeded
# - Postman resources updated
# - Documentation deployed
```

### When Revert Fails

If the revert creates merge conflicts:

```bash
# Abort the revert
git revert --abort

# Use fix forward instead (Strategy 2)
# Or hard reset (Strategy 3)
```

---

## Rollback Strategy 2: Fix Forward

**When to use**: The problem is small and easy to fix. Faster than reverting.

### Advantages
- Quickest solution
- Keeps moving forward
- No extra commits
- Maintains clean history

### Disadvantages
- Requires you to know the fix
- Not appropriate for complex issues

### Procedure

#### Step 1: Identify the Issue

```bash
# Run validation
./scripts/validate-before-commit.sh

# Check the error message
# Example: "Duplicate definition for: priority"
```

#### Step 2: Fix the Issue

Edit `data_dictionary/c2mapiv2-dd.ebnf`:

```ebnf
(* BEFORE - Duplicate *)
priority = "standard" | "rush" ;
priority = "standard" | "rush" | "overnight" ;

(* AFTER - Fixed *)
priority = "standard" | "rush" | "overnight" ;
```

#### Step 3: Validate

```bash
./scripts/validate-before-commit.sh
./scripts/preview-ebnf-changes.sh
```

#### Step 4: Push Fix

```bash
git add data_dictionary/
git commit -m "fix: remove duplicate priority definition"
git push origin main
```

### When to Use Fix Forward

**GOOD scenarios**:
- Missing semicolon
- Typo in field name
- Duplicate definition
- Simple syntax error

**BAD scenarios**:
- Multiple interconnected changes
- Breaking changes affecting clients
- Unknown root cause
- Complex structural issues

---

## Rollback Strategy 3: Hard Reset

**When to use**: EMERGENCY ONLY. Last resort when nothing else works.

WARNING: Rewrites history. Dangerous for shared repositories. Coordinate with team first.

### Advantages
- Completely removes bad commits
- Clean slate
- As if bad commit never happened

### Disadvantages
- Rewrites history (breaks others' work)
- Requires force push
- Can't easily undo
- Loses commit information

### Procedure

#### Step 1: Find Last Good Commit

```bash
# Show commit history
git log --oneline -10

# Identify last working commit
# Example: e4f5g6h was the last good state
```

#### Step 2: Create Backup Branch (CRITICAL)

```bash
# Create backup before reset
git branch backup-before-reset
git push origin backup-before-reset
```

This saves your work in case you need to recover.

#### Step 3: Reset to Good Commit

```bash
# Hard reset (DESTRUCTIVE)
git reset --hard e4f5g6h

# Verify you're at correct commit
git log --oneline -3
```

#### Step 4: Force Push (DANGEROUS)

```bash
# WARNING: This rewrites history for everyone
git push --force origin main
```

#### Step 5: Notify Team

**IMMEDIATELY** notify all team members:
- Which commits were removed
- Why reset was necessary
- What they need to do (re-sync their repos)

#### Step 6: Team Recovery Steps

Everyone else needs to:

```bash
# Fetch latest
git fetch origin

# Hard reset their local main
git checkout main
git reset --hard origin/main

# If they have local changes, save them first:
git stash
git reset --hard origin/main
git stash pop
```

### When to Use Hard Reset

**ONLY when**:
- CI/CD completely broken
- Can't revert due to conflicts
- Multiple bad commits tangled together
- Emergency fix needed NOW
- Team coordinated and aware

**NEVER when**:
- You're the only one having issues
- Revert would work
- Fix forward is possible
- You haven't coordinated with team

---

## Postman Resource Recovery

**Problem**: Postman collections, mock server, or environments broken.

### Step 1: Assess Damage

Check Postman workspace:
- Personal: https://www.postman.com/serrao-workspace/c2m-api-v2
- Team: https://www.postman.com/c2m-workspace/c2m-api-v2

**Look for**:
- Missing collections
- Broken mock server
- Invalid environment variables
- Incorrect API definitions

### Step 2: Quick Fix - Delete and Rebuild

```bash
# Set target workspace
echo "personal" > .postman-target    # or "team"

# Delete all resources
make postman-cleanup-all

# Rebuild everything
make postman-instance-build-without-tests
```

Wait 8 minutes. This recreates:
- 3 Collections (Linked, Test, Use Cases)
- 1 Mock Server
- 2 Environments (Mock, AWS Dev)
- 1 API Definition

### Step 3: Verify Recovery

```bash
# Check Postman workspace
# All resources should be recreated

# Test mock server
curl https://<mock-server-url>.mock.pstmn.io/jobs/submit/single/doc

# Should return test data with 200 OK
```

### When Delete/Rebuild Doesn't Work

#### Issue: Validation Errors

```bash
# Check EBNF first
./scripts/validate-before-commit.sh

# If validation fails, fix EBNF before rebuilding
```

#### Issue: API Key Problems

```bash
# Check .env file
cat .env

# Should contain:
# POSTMAN_SERRAO_API_KEY=PMAK-...
# POSTMAN_C2M_API_KEY=PMAK-...

# Verify key works
curl -X GET "https://api.getpostman.com/me" \
  -H "X-API-Key: PMAK-..."
```

#### Issue: Stale UID Files

```bash
# Clear UID tracking files
rm postman/*.txt

# Rebuild (will create fresh UIDs)
make postman-instance-build-without-tests
```

---

## CI/CD Failure Recovery

**Problem**: GitHub Actions workflow failed.

### Step 1: Check Workflow Status

Visit: https://github.com/click2mail/c2m-api-v2-postman/actions

**Look for**:
- Red X (failed)
- Yellow dot (in progress)
- Green checkmark (success)

### Step 2: Read Failure Logs

Click failed workflow → Click failed job → Read error messages

**Common Errors**:

#### Error: "0 productions parsed"
**Cause**: EBNF syntax error
**Fix**: Revert commit or fix EBNF

#### Error: "Postman API returned 403"
**Cause**: Invalid API key
**Fix**: Update GitHub Secret POSTMAN_API_KEY

#### Error: "Newman tests failed"
**Cause**: API changes broke tests
**Fix**: Update tests or revert changes

#### Error: "openapi-diff failed"
**Cause**: Breaking API changes detected
**Fix**: Review changes, update version, or revert

### Step 3: Trigger Manual Workflow Run

If issue was transient (network glitch, etc.):

```bash
# Trigger workflow manually
gh workflow run api-ci-cd.yml --repo click2mail/c2m-api-v2-postman

# Or via UI:
# https://github.com/click2mail/c2m-api-v2-postman/actions
# Click "Run workflow"
```

### Step 4: Fix and Re-push

If workflow found real issue:

```bash
# Option 1: Revert
git revert HEAD
git push origin main

# Option 2: Fix forward
# (fix the issue)
git add .
git commit -m "fix: resolve CI/CD failure"
git push origin main
```

---

## Complete Disaster Recovery

**Problem**: Multiple systems broken, can't figure out what happened.

### Nuclear Option: Full Restoration

#### Step 1: Find Last Known Good State

```bash
# Check git history
git log --oneline --all

# Find a commit you KNOW worked
# Example: from yesterday, last week, etc.
```

#### Step 2: Create Recovery Branch

```bash
# Create branch from good commit
git checkout -b recovery-20250215 e4f5g6h
```

#### Step 3: Verify Good State

```bash
# Validate EBNF
./scripts/validate-before-commit.sh

# Build locally
make postman-instance-build-without-tests

# If everything works, this is your recovery point
```

#### Step 4: Restore Main Branch

**Option A: Merge Recovery (keeps history)**
```bash
git checkout main
git merge recovery-20250215 --strategy-option theirs
git push origin main
```

**Option B: Reset Main (rewrites history)**
```bash
# COORDINATE WITH TEAM FIRST
git checkout main
git reset --hard recovery-20250215
git push --force origin main
```

#### Step 5: Rebuild All Resources

```bash
# Personal workspace
echo "personal" > .postman-target
make postman-cleanup-all
make postman-instance-build-without-tests

# Team workspace
echo "team" > .postman-target
make postman-cleanup-all
make postman-instance-build-without-tests
```

#### Step 6: Verify Complete System

Check all systems:
- [ ] Git repository restored
- [ ] EBNF validates
- [ ] OpenAPI spec generates
- [ ] Postman collections exist
- [ ] Mock server responds
- [ ] Documentation deploys
- [ ] CI/CD workflow passes

---

## Prevention Checklist

### Before Every Commit

- [ ] Run `./scripts/validate-before-commit.sh`
- [ ] Run `./scripts/preview-ebnf-changes.sh`
- [ ] Review changes carefully
- [ ] Consider impact on clients

### Before Major Changes

- [ ] Create feature branch
- [ ] Test in personal workspace first
- [ ] Get team review
- [ ] Plan rollback strategy
- [ ] Test locally with full build

### After Every Push

- [ ] Monitor CI/CD workflow
- [ ] Verify Postman resources
- [ ] Check documentation deployed
- [ ] Test one endpoint manually

### Periodic Maintenance

- [ ] Review git history weekly
- [ ] Clean up stale branches
- [ ] Update documentation
- [ ] Practice recovery procedures
- [ ] Keep .env files updated

---

## Recovery Commands Quick Reference

```bash
# Quick revert
git revert HEAD && git push origin main

# Fix forward
# (fix issue)
git add . && git commit -m "fix: issue" && git push

# Hard reset (EMERGENCY ONLY)
git branch backup-before-reset
git reset --hard <commit-hash>
git push --force origin main

# Postman rebuild
echo "personal" > .postman-target
make postman-cleanup-all
make postman-instance-build-without-tests

# CI/CD manual trigger
gh workflow run api-ci-cd.yml --repo click2mail/c2m-api-v2-postman
```

---

## Getting Help

### When You're Stuck

1. **Read error messages carefully** - They usually tell you exactly what's wrong
2. **Check recent commits** - What changed right before it broke?
3. **Revert first, debug later** - Get system working, then investigate
4. **Ask team for help** - Don't struggle alone on critical issues

### Escalation Path

1. Try fix forward (5 minutes)
2. Try revert (2 minutes)
3. Ask team for help
4. Consider hard reset (coordinate first)
5. Full disaster recovery (last resort)

### Important Links

- GitHub Actions: https://github.com/click2mail/c2m-api-v2-postman/actions
- Postman Workspace (Personal): https://www.postman.com/serrao-workspace/c2m-api-v2
- Postman Workspace (Team): https://www.postman.com/c2m-workspace/c2m-api-v2
- Documentation: https://click2mail.github.io/c2m-api-v2-postman-artifacts/

---

## Remember

1. **Panic helps nobody** - Take a breath, assess calmly
2. **History is your friend** - git preserves everything
3. **Revert is usually enough** - Don't jump to hard reset
4. **Test in personal first** - Avoid breaking team workspace
5. **Communicate always** - Tell team what you're doing

**Most importantly**: It's just code. Everything can be fixed. Don't be afraid to ask for help.
