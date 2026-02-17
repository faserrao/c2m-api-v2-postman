# Getting Started with EBNF Data Dictionary Editing

Welcome to the C2M API V2 data dictionary! This guide will walk you through your first EBNF edits with confidence.

## Table of Contents

- [What You'll Learn](#what-youll-learn)
- [Prerequisites](#prerequisites)
- [Your First Day: The 5-Minute Primer](#your-first-day-the-5-minute-primer)
- [Essential Workflow: Edit → Validate → Preview → Push](#essential-workflow-edit--validate--preview--push)
- [Three Ways to Work](#three-ways-to-work)
- [Your First Edit: Adding an Optional Field](#your-first-edit-adding-an-optional-field)
- [Understanding the Pipeline](#understanding-the-pipeline)
- [Quick Reference](#quick-reference)
- [What's Next](#whats-next)
- [Getting Help](#getting-help)

---

## What You'll Learn

By the end of this guide, you'll be able to:

1. Edit the EBNF data dictionary safely
2. Validate your changes before committing
3. Preview what will change in the OpenAPI spec
4. Push changes with confidence
5. Recover if something goes wrong

**Time Required**: 30 minutes for complete walkthrough

---

## Prerequisites

Before you start, make sure you've completed the initial setup from [NEW_DEVELOPER_QUICKSTART.md](NEW_DEVELOPER_QUICKSTART.md).

**Quick Check** (run these commands):
```bash
# Check you're in the right directory
pwd
# Should show: .../c2m-api-v2-postman

# Check scripts are executable
ls -la scripts/*.sh
# Should show: -rwxr-xr-x (executable)

# Test validation
./scripts/validate-before-commit.sh
# Should show: "EBNF validated successfully"
```

If any of these fail, go back to [NEW_DEVELOPER_QUICKSTART.md](NEW_DEVELOPER_QUICKSTART.md) first.

---

## Your First Day: The 5-Minute Primer

### What is the EBNF Data Dictionary?

The EBNF data dictionary (`data_dictionary/c2mapiv2-dd.ebnf`) is the **single source of truth** for the entire API.

**Everything flows from this file**:
```
EBNF Data Dictionary
    ↓
OpenAPI Specification
    ↓
Postman Collections
    ↓
Documentation + Mock Servers + SDKs
```

When you edit the EBNF, you're defining:
- What fields exist in the API
- What types they have (string, integer, enum)
- Which fields are required vs optional
- How objects are structured

### The Golden Rule

**ALWAYS run validation before committing**

The pipeline is fragile. One syntax error breaks everything downstream.

That's why we created helper tools to make validation automatic.

---

## Essential Workflow: Edit → Validate → Preview → Push

Every EBNF change follows this 4-step workflow:

```
1. EDIT the EBNF file
   ↓
2. VALIDATE syntax and structure
   ↓
3. PREVIEW what will change in OpenAPI
   ↓
4. PUSH to repository (triggers CI/CD)
```

### The Scripts That Make This Easy

We've created 3 helper scripts to automate this workflow:

1. **`validate-before-commit.sh`** - Checks EBNF syntax
2. **`preview-ebnf-changes.sh`** - Shows what will change
3. **`safe-push.sh`** - Complete workflow with interactive prompts

**You'll use safe-push.sh for 95% of your work.**

---

## Three Ways to Work

Choose the method that fits your workflow:

### Method 1: Interactive Safe Push (Recommended)

**Best for**: New developers, important changes, when you want guidance

```bash
./scripts/safe-push.sh "Add priority field to submitSingleDocParams"
```

**What happens**:
1. Validates EBNF syntax
2. Previews OpenAPI changes
3. Asks if you want to build locally (test everything)
4. Commits with your message
5. Pushes to GitHub

**Time**: 5-8 minutes (with local build), 30 seconds (without)

---

### Method 2: Manual Steps

**Best for**: When you want fine control, debugging, or understanding the process

```bash
# Step 1: Edit EBNF
vim data_dictionary/c2mapiv2-dd.ebnf

# Step 2: Validate
./scripts/validate-before-commit.sh

# Step 3: Preview changes
./scripts/preview-ebnf-changes.sh

# Step 4: Commit and push
git add data_dictionary/
git commit -m "Add priority field to submitSingleDocParams"
git push origin main
```

**Time**: 2-3 minutes (you control each step)

---

### Method 3: Makefile Targets

**Best for**: Integration with build systems, scripting, automation

```bash
# Validate only
make validate-ebnf

# Preview only
make preview-changes

# Safe push
make safe-push MSG="Add priority field"
```

**Time**: Same as scripts, but shorter commands

---

### Method 4: VS Code Tasks (Bonus)

**Best for**: Developers who live in VS Code

**Access**: `Terminal → Run Task...` or `Cmd/Ctrl + Shift + P` → "Tasks: Run Task"

**Available Tasks**:
- EBNF: Validate Data Dictionary
- EBNF: Preview Changes
- EBNF: Safe Push (Interactive)
- Build: Generate OpenAPI Spec
- Build: Complete Pipeline (With Tests)
- Test: Local Mock Server (Prism)
- Cleanup: All Postman Resources

**Time**: Click and run, same speed as scripts

---

## Your First Edit: Adding an Optional Field

Let's walk through a real example: adding a `priority` field to the `submitSingleDocParams` endpoint.

### Step 1: Open the EBNF File

```bash
# Open in your editor
vim data_dictionary/c2mapiv2-dd.ebnf
# or
code data_dictionary/c2mapiv2-dd.ebnf
```

### Step 2: Find the Endpoint Definition

Search for `submitSingleDocParams`:

```ebnf
submitSingleDocParams =
      [ jobTemplate ]
    + docSourceAll
    + recipientAddressSource
    + [ paymentDetails ]
    + [ returnAddress ]
    + [ jobOptions ]
    + [ tags ] ;
```

### Step 3: Add Your New Field

Add `priority` after `returnAddress`:

```ebnf
submitSingleDocParams =
      [ jobTemplate ]
    + docSourceAll
    + recipientAddressSource
    + [ paymentDetails ]
    + [ returnAddress ]
    + [ priority ]         (* NEW: Priority level for processing *)
    + [ jobOptions ]
    + [ tags ] ;
```

**Key Points**:
- Square brackets `[ ]` = optional field
- Plus sign `+` = separator between fields
- Comment `(* *)` = explains what the field does
- Semicolon `;` = ends the definition

### Step 4: Define the Field Type

Scroll down and add the field definition:

```ebnf
priority = "standard" | "rush" | "overnight" ;
```

This defines `priority` as an enum with 3 possible values.

**Save the file.**

### Step 5: Validate Your Changes

```bash
./scripts/validate-before-commit.sh
```

**Expected Output**:
```
Validating EBNF data dictionary...
Running EBNF to OpenAPI translator with validation...
SUCCESS: EBNF validated successfully
  Productions parsed: 98
  Schemas generated: 143
  Paths created: 8
  Parse errors: 0
```

**If you see errors**: Read the error message carefully. Common issues:
- Missing semicolon (`;`)
- Typo in field name
- Forgot to define the field type

Fix the error and validate again.

### Step 6: Preview What Will Change

```bash
./scripts/preview-ebnf-changes.sh
```

**Expected Output**:
```
Previewing OpenAPI spec changes...

Changes detected in OpenAPI spec:

  Added schema: priority
    type: string
    enum: [standard, rush, overnight]

  Modified schema: submitSingleDocParams
    properties:
      priority:
        $ref: '#/components/schemas/priority'

Preview complete. Changes look correct.
```

This shows you exactly what will change in the OpenAPI specification.

### Step 7: Use Safe Push

```bash
./scripts/safe-push.sh "Add priority field to submitSingleDocParams"
```

**Interactive Prompts**:
```
Step 1: Validation
SUCCESS: EBNF validated successfully

Step 2: Preview Changes
Changes detected in OpenAPI spec...

Step 3: Run local build? (y/n)
```

**Choose**:
- **`y`** (yes) = Full local build (8 min) - Tests everything before pushing
- **`n`** (no) = Skip to commit and push (30 sec) - Rely on CI/CD

**Recommendation for first edit**: Choose `y` to see the full pipeline run.

**After choosing `n`**:
```
Step 4: Commit and Push
Committing changes...
Pushing to GitHub...

Complete! GitHub Actions CI/CD will now:
  1. Regenerate OpenAPI spec
  2. Update Postman collections
  3. Deploy documentation
  4. Publish to Postman workspace

Monitor progress:
https://github.com/click2mail/c2m-api-v2-postman/actions
```

### Step 8: Verify on GitHub

1. Open the GitHub Actions URL
2. Wait for workflow to complete (~3 minutes)
3. Check for green checkmark (success) or red X (failure)

**If successful**: Your changes are live in Postman and documentation!

**If failed**: See [ROLLBACK.md](ROLLBACK.md) for recovery procedures.

---

## Understanding the Pipeline

### What Happens After You Push

```
GitHub Push
    ↓
GitHub Actions Triggered
    ↓
├─ Build OpenAPI Spec (from EBNF)
├─ Validate OpenAPI Spec
├─ Generate Postman Collections
├─ Build Documentation
├─ Generate SDKs (11 languages)
└─ Publish to Postman Workspace
    ↓
Done (3-4 minutes)
```

### What Gets Updated Automatically

When you push EBNF changes:

1. **OpenAPI Specification** - Regenerated from EBNF
2. **Postman Collections** - 3 collections updated:
   - Linked Collection (placeholder values)
   - Test Collection (realistic examples)
   - Real World Use Cases
3. **Mock Server** - Updated to serve new fields
4. **Documentation** - Redocly docs rebuilt
5. **SDKs** - Code samples regenerated (Python, JavaScript, etc.)

**You only edit EBNF. Everything else is automatic.**

---

## Quick Reference

### Daily Commands

```bash
# Validate before every commit
./scripts/validate-before-commit.sh

# Preview what will change
./scripts/preview-ebnf-changes.sh

# Complete safe workflow
./scripts/safe-push.sh "Your commit message"
```

### Makefile Shortcuts

```bash
make validate-ebnf          # Validate EBNF
make preview-changes        # Preview OpenAPI changes
make safe-push MSG="..."    # Safe push workflow
```

### When Things Go Wrong

```bash
# Revert last commit
git revert HEAD
git push origin main

# See ROLLBACK.md for more recovery options
```

### File Locations

| File | Purpose |
|------|---------|
| `data_dictionary/c2mapiv2-dd.ebnf` | EBNF source (you edit this) |
| `openapi/c2mapiv2-openapi-spec-base.yaml` | Generated OpenAPI spec |
| `scripts/validate-before-commit.sh` | Validation script |
| `scripts/preview-ebnf-changes.sh` | Preview script |
| `scripts/safe-push.sh` | Safe push workflow |

---

## What's Next

Now that you've completed your first edit, explore these resources:

### Learn More About EBNF Syntax

**[EBNF_QUICK_REFERENCE.md](EBNF_QUICK_REFERENCE.md)** - Complete syntax guide
- All EBNF constructs explained
- Syntax rules and examples
- Common patterns

### Learn Common Editing Tasks

**[COMMON_EBNF_TASKS.md](COMMON_EBNF_TASKS.md)** - Task-based tutorials
- Add optional field
- Add required field
- Change field type
- Add array field
- Add nested object
- 10 tasks total with step-by-step instructions

### Understand the Workflow

**[WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md)** - Visual flowcharts
- Complete system pipeline
- Developer editing workflow
- CI/CD automation
- Decision trees

### Emergency Procedures

**[ROLLBACK.md](ROLLBACK.md)** - When things go wrong
- 3 rollback strategies
- CI/CD failure recovery
- Complete disaster recovery
- Prevention checklist

---

## Getting Help

### Common Questions

**Q: How long does the pipeline take?**
A: 3-4 minutes in CI/CD, 8-15 minutes for local builds (with tests)

**Q: Can I test locally before pushing?**
A: Yes! Use `./scripts/safe-push.sh` and choose `y` when asked about local build

**Q: What if validation fails?**
A: Read the error message carefully. Check for:
- Missing semicolon (`;`)
- Typo in identifier
- Missing field definition
- Duplicate definition

**Q: What if I push broken EBNF?**
A: CI/CD will catch it and fail. See [ROLLBACK.md](ROLLBACK.md) for recovery

**Q: Can I preview changes without committing?**
A: Yes! Run `./scripts/preview-ebnf-changes.sh` anytime

### Validation Error Examples

**Error: "0 productions parsed"**
```
Cause: Critical syntax error (missing semicolon, unclosed comment)
Fix: Check the line number in error message, fix syntax
```

**Error: "Duplicate definition for: fieldName"**
```
Cause: Same identifier defined twice
Fix: Search for duplicate, keep one, delete other
```

**Error: "Undefined reference: fieldName"**
```
Cause: Field used in endpoint but never defined
Fix: Add field definition below the endpoint
```

### Getting Unstuck

1. **Read error messages carefully** - They tell you exactly what's wrong
2. **Check recent changes** - What did you change right before it broke?
3. **Use preview script** - See what's different without committing
4. **Revert if needed** - `git revert HEAD` undoes last commit
5. **Ask for help** - Share the error message with the team

### Useful Links

- **GitHub Actions**: https://github.com/click2mail/c2m-api-v2-postman/actions
- **Postman Workspace**: https://www.postman.com/c2m-workspace/c2m-api-v2
- **Documentation**: https://click2mail.github.io/c2m-api-v2-postman-artifacts/

---

## Tips for Success

### Before Every Edit

1. Pull latest changes: `git pull origin main`
2. Validate current state: `./scripts/validate-before-commit.sh`
3. Make small, focused changes (one field at a time)

### After Every Edit

1. Validate: `./scripts/validate-before-commit.sh`
2. Preview: `./scripts/preview-ebnf-changes.sh`
3. Review changes carefully before pushing
4. Monitor CI/CD after pushing

### Best Practices

- **Comment your intent**: Use `(* Comments *)` to explain WHY
- **Small commits**: One logical change per commit
- **Descriptive messages**: "Add priority field" not "Update EBNF"
- **Test thoroughly**: Use local build before pushing major changes
- **Learn from CI/CD**: If it fails, understand why before retrying

---

## Remember

1. **EBNF is the source of truth** - Everything flows from this file
2. **Validation is required** - Never commit without validating
3. **Preview saves time** - See what will change before pushing
4. **CI/CD has your back** - It catches errors before production
5. **Rollback is easy** - Don't be afraid to revert and try again

**Most importantly**: Take your time, ask questions, and make small changes until you're comfortable.

---

## Summary: Your Daily Workflow

```bash
# 1. Start fresh
git pull origin main
./scripts/validate-before-commit.sh

# 2. Edit EBNF
vim data_dictionary/c2mapiv2-dd.ebnf

# 3. Safe push
./scripts/safe-push.sh "Add your changes"

# 4. Monitor CI/CD
# Check GitHub Actions for green checkmark
```

That's it! You're ready to edit the EBNF data dictionary with confidence.

**Happy editing!**
