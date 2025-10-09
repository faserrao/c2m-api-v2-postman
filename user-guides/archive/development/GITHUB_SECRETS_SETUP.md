# GitHub Secrets Setup for Postman Integration

This guide explains how to configure GitHub secrets to enable automatic Postman updates from the CI/CD pipeline.

## How It Works

When you run a local publish command, it automatically saves your choice to `.postman-target` file:
- `make postman-publish-personal` → Saves "personal" to file
- `make postman-publish-team` → Saves "team" to file  
- `make postman-publish-both` → Saves "both" to file

When you commit and push, GitHub Actions reads this file and publishes to the same target(s)!

## Publishing Options

You can publish to:
1. **Personal workspace only** - Your development workspace
2. **Team workspace only** - The C2M team workspace  
3. **Both workspaces** - Updates both in sequence

## Setting Up GitHub Secrets

### Step 1: Navigate to Repository Settings
1. Go to your repository on GitHub
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**

### Step 2: Add Required Secrets

You need to add BOTH API keys to support automatic switching:

1. **POSTMAN_SERRAO_API_KEY**
   - Click "New repository secret"
   - Name: `POSTMAN_SERRAO_API_KEY`
   - Value: Your personal Postman API key
   - Click "Add secret"

2. **POSTMAN_C2M_API_KEY**
   - Click "New repository secret"
   - Name: `POSTMAN_C2M_API_KEY`
   - Value: The C2M team Postman API key
   - Click "Add secret"

### Step 3: Configure Publishing Target Override (Optional)

The `.postman-target` file in your repo controls where CI/CD publishes. However, you can override this with a secret:
- Name: `POSTMAN_TARGET`
- Value: One of:
  - `personal` - Only update your workspace
  - `team` - Only update team workspace
  - `both` - Update both workspaces

**Priority order:**
1. `.postman-target` file (set by your last local publish)
2. `POSTMAN_TARGET` secret (if file doesn't exist)
3. Default: "personal" (if neither exists)

### Step 4: Verify Setup

After adding the secrets, pushes to `main` will:
- Publish to the target saved in `.postman-target` file
- Or to the target in `POSTMAN_TARGET` secret (if file missing)
- Or to personal workspace (default)

## Testing Your Configuration

### Check Current Workspace (Local)
```bash
make workspace-info
```

### Local Publishing Options
```bash
# Publish to personal workspace only
make postman-publish-personal

# Publish to team workspace only  
make postman-publish-team

# Publish to both workspaces
make postman-publish-both

# Or use environment variable
POSTMAN_TARGET=both make postman-publish
POSTMAN_TARGET=team make postman-publish
POSTMAN_TARGET=personal make postman-publish
```

### Test GitHub Actions
1. Push to main → Updates workspace(s) based on POSTMAN_TARGET secret
2. Default behavior → Updates personal workspace only

## Workflow Summary

1. **Local Development**:
   - Run `make postman-publish-personal/team/both`
   - This updates Postman AND saves your choice to `.postman-target`
   
2. **Commit & Push**:
   - Include the `.postman-target` file in your commit
   - GitHub Actions will publish to the same target(s)

3. **No Manual Configuration**:
   - Your local choice automatically becomes the CI/CD choice
   - No need to update secrets or environment variables

4. **Override if Needed**:
   - Set `POSTMAN_TARGET` secret to force a specific target
   - Useful for ensuring production always goes to team workspace

## Troubleshooting

### Workflow Not Publishing to Postman
Check the workflow logs for:
- "⚠️ Skipping Postman publish: POSTMAN_API_KEY not set"
- This means the secrets aren't configured

### Wrong Workspace Being Updated
Run `make workspace-info` to see which workspace is active and why.

### Need to Use Different Workspace Temporarily
Use the override environment variables:
```bash
POSTMAN_WORKSPACE_OVERRIDE=<workspace-id> \
POSTMAN_API_KEY_OVERRIDE=<api-key> \
make postman-publish
```