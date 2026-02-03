# Context System - Build & Publish Configuration

## Overview

This repository uses a **context system** to enforce strict 1:1 relationships between GitHub repositories and Postman workspaces:

```
faserrao/c2m-api-v2-postman   → Personal Postman workspace ONLY
click2mail/c2m-api-v2-postman → Corporate Postman workspace ONLY
```

**No cross-publishing is allowed** - this prevents accidental updates to the wrong workspace.

## Quick Start

### Check Current Context

```bash
make context-show
```

### Switch Context (Local Development)

```bash
# Switch to personal context (faserrao repo → personal Postman)
make context-set-personal

# Switch to click2mail context (click2mail repo → corporate Postman)
make context-set-click2mail
```

### Build & Publish

```bash
# Build and publish to current context workspace
make postman-instance-build-with-tests

# Just publish (no rebuild)
make postman-publish
```

## How It Works

### Local Development

1. **Context File**: `.git-context` file stores current context (`personal` or `click2mail`)
2. **Auto-Detection**: Makefile reads `.git-context` and selects:
   - Workspace ID (personal or corporate)
   - API key (POSTMAN_SERRAO_API_KEY or POSTMAN_C2M_API_KEY)
3. **Manual Switching**: Use `make context-set-*` to change context

### GitHub Actions (CI/CD)

1. **Auto-Detection**: Workflow detects repository owner:
   - `faserrao` → writes "personal" to `.git-context`
   - `click2mail` → writes "click2mail" to `.git-context`
2. **Enforcement**: No manual override possible - strictly enforced 1:1
3. **Result**: Each repo can ONLY publish to its designated workspace

## Context File

**Location**: `.git-context` (in repository root)

**Content**: Single line with either:
- `personal` - faserrao repo, personal Postman workspace
- `click2mail` - click2mail repo, corporate Postman workspace

**Git Tracking**: File is gitignored (local only, not committed)

## Migration from Old System

### Old Way (.postman-target file)
```bash
# Manual workspace switching (deprecated)
echo "personal" > .postman-target
make postman-publish-personal

echo "corporate" > .postman-target
make postman-publish-team
```

### New Way (.git-context file)
```bash
# Context-based workspace selection
make context-set-personal
make postman-publish

make context-set-click2mail
make postman-publish
```

## Available Commands

### Context Management
- `make context-show` - Display current context and affected settings
- `make context-set-personal` - Switch to personal context
- `make context-set-click2mail` - Switch to click2mail context

### Workspace Information
- `make workspace-info` - Show workspace configuration

### Publishing
- `make postman-publish` - Publish to current context workspace

### Deprecated (Still Work, Show Warnings)
- `make postman-publish-personal` - Use `context-set-personal` instead
- `make postman-publish-team` - Use `context-set-click2mail` instead
- `make use-personal-workspace` - Use `context-set-personal` instead
- `make use-team-workspace` - Use `context-set-click2mail` instead

### Removed
- `make postman-publish-both` - Cross-publishing not allowed

## Environment Variables

Required in `.env` file:

```bash
POSTMAN_SERRAO_API_KEY=your-personal-api-key
POSTMAN_C2M_API_KEY=your-corporate-api-key
```

Both keys must be configured. The context system selects which key to use.

## Benefits

### 1. Safety
- **No accidental cross-publishing** - can't update wrong workspace
- **GitHub Actions enforcement** - repo owner determines workspace automatically
- **Clear separation** - personal work stays personal, corporate stays corporate

### 2. Simplicity
- **Single command** - `make postman-publish` (context-aware)
- **Automatic selection** - no manual workspace specification needed
- **Visual feedback** - context shown in all build outputs

### 3. Consistency
- **Local matches CI/CD** - same rules everywhere
- **One source of truth** - `.git-context` file
- **No confusion** - clear error messages if wrong context

## Troubleshooting

### "ERROR: Current context is 'X', not 'Y'"

**Cause**: Trying to use deprecated target with wrong context

**Solution**: Switch context first:
```bash
make context-set-personal  # or context-set-click2mail
make postman-publish
```

### Publishing to Wrong Workspace

**Cause**: Context not set correctly

**Solution**: Check and fix context:
```bash
make context-show
make context-set-[correct-context]
```

### GitHub Actions Publishing to Wrong Workspace

**Cause**: Workflow uses repository owner to determine workspace (automatic)

**Solution**: Push to correct repository:
- Personal changes → push to `faserrao/c2m-api-v2-postman`
- Corporate changes → push to `click2mail/c2m-api-v2-postman`

## Examples

### Scenario: Local Development for Personal Use

```bash
# Set context to personal
make context-set-personal

# Verify
make context-show

# Build and test locally
make postman-instance-build-with-tests

# Push to faserrao repo (triggers personal Postman via GitHub Actions)
git push origin main
```

### Scenario: Corporate Changes

```bash
# Set context to click2mail
make context-set-click2mail

# Verify
make context-show

# Build and test locally
make postman-instance-build-with-tests

# Push to click2mail repo (triggers corporate Postman via GitHub Actions)
git push click2mail main
```

### Scenario: Quick Context Switch

```bash
# Currently in personal context, need to switch to click2mail
make context-show  # Shows: personal
make context-set-click2mail
make context-show  # Shows: click2mail

# Now all builds use corporate workspace
make postman-publish
```

## Architecture

### Files
- `.git-context` - Current context (personal or click2mail)
- `scripts/utilities/set-context.sh` - Context switching script
- `Makefile` - Reads context, selects workspace/key
- `.github/workflows/api-ci-cd.yml` - Auto-detects and creates context

### Flow
```
Developer runs: make context-set-personal
    ↓
Script writes: echo "personal" > .git-context
    ↓
Makefile reads: GIT_CONTEXT := $(shell cat .git-context)
    ↓
Makefile selects:
  POSTMAN_WS := $(SERRAO_WS)
  POSTMAN_API_KEY := $(POSTMAN_SERRAO_API_KEY)
    ↓
Build publishes to: Personal Postman workspace
```

## Support

For issues or questions about the context system:
1. Check `.git-context` file contents
2. Run `make context-show` to see current state
3. Run `make workspace-info` for detailed configuration
4. Check build logs for context information
