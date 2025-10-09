# C2M API Quick Reference Guide

## 🚀 Quick Start

### First Time Setup
```bash
# 1. Clone the repository
git clone https://github.com/faserrao/c2m-api-repo.git
cd c2m-api-repo

# 2. Create .env file
echo "POSTMAN_SERRAO_API_KEY=your-key-here" > .env
echo "POSTMAN_C2M_API_KEY=team-key-here" >> .env

# 3. Install dependencies
npm install
pip install -r scripts/python_env/requirements.txt

# 4. Test your setup
make postman-auth-test
```

## 📝 Common Development Tasks

### When you change the EBNF data dictionary:
```bash
# Option 1: Full rebuild and test locally
make postman-instance-build-and-test

# Option 2: Just build OpenAPI to see changes
make openapi-build
cat openapi/c2mapiv2-openapi-spec-final.yaml

# Option 3: Build and publish to your personal workspace
make postman-publish-personal
```

### When you want to test with Postman:
```bash
# Start local mock server (Prism)
make postman-test-local

# In another terminal, run tests
make postman-test-run

# Or use the real Postman mock
make postman-test-remote
```

### When you're ready to deploy:
```bash
# 1. Create a feature branch
git checkout -b feature/your-change

# 2. Make your changes and commit
git add .
git commit -m "feat: your change description"

# 3. Push and create PR
git push -u origin feature/your-change
gh pr create

# 4. After PR is merged, it auto-deploys to both workspaces
```

## 🎯 Workspace Management

### Control which workspace gets updated:
```bash
# Update personal workspace only
make postman-publish-personal

# Update team workspace only  
make postman-publish-team

# Update both workspaces
make postman-publish-both

# Check current target
cat .postman-target
```

### Clean up Postman workspace:
```bash
# Clean everything in current workspace
make postman-cleanup-all

# Then rebuild
make postman-instance-build-and-test
```

## 🔍 Debugging Commands

### When something isn't working:
```bash
# Check all variables
make show-vars

# Test Postman authentication
make postman-auth-test

# Check what files exist
ls -la openapi/
ls -la postman/generated/

# Clean and start fresh
make clean
make postman-cleanup-all
```

### Check build artifacts:
```bash
# See generated OpenAPI
cat openapi/c2mapiv2-openapi-spec-final.yaml

# Check if paymentDetails is required
grep -A10 "paymentDetails" openapi/c2mapiv2-openapi-spec-final.yaml

# See Postman collection
jq . postman/generated/c2mapiv2-collection.json
```

## 📊 Repository Status

### Check git status:
```bash
# Current branch and changes
git status

# Recent commits
git log --oneline -10

# Check CI/CD status
gh run list --limit 5
```

### Check artifacts repository:
```bash
# If you have artifacts repo cloned
cd ../c2m-api-artifacts
git pull
git log --oneline -5
ls -la openapi/
```

## 🚨 Emergency Procedures

### If CI/CD fails on main:
```bash
# 1. Check the error
gh run list --limit 1
gh run view [run-id]

# 2. Fix locally and test
make postman-instance-build-and-test

# 3. Create hotfix
git checkout -b hotfix/fix-description
# make fixes
git commit -m "fix: description"
git push -u origin hotfix/fix-description
gh pr create
```

### If Postman is in bad state:
```bash
# Nuclear option - clean everything
make postman-cleanup-all
make postman-instance-build-and-test
make postman-publish-both
```

## 📋 File Locations Cheat Sheet

**Source Files (you edit these):**
- EBNF: `data_dictionary/c2mapiv2-dd.ebnf`
- Overlays: `openapi/overlays/*.yaml`
- Custom tests: `postman/custom/*.json`
- Environments: `postman/environments/*.json`

**Generated Files (don't edit these):**
- OpenAPI specs: `openapi/c2mapiv2-openapi-spec-*.yaml`
- Postman collections: `postman/generated/*.json`
- Mock data: `postman/postman_*.txt`

**Configuration:**
- Local secrets: `.env`
- Workspace target: `.postman-target`
- Build rules: `Makefile`

## 🔄 Workflow Summary

1. **Local Development**: Edit EBNF → `make openapi-build` → Test
2. **Personal Testing**: `make postman-publish-personal` → Test in Postman
3. **Team Deployment**: Create PR → Merge → Auto-deploys to both workspaces
4. **Artifacts Sync**: Every main branch push → Updates artifacts repo

## 💡 Pro Tips

1. **Always test locally first**: `make postman-instance-build-and-test`
2. **Use personal workspace for testing**: Avoids disrupting team
3. **Check PR status before merging**: All checks should be green
4. **Keep .env file updated**: Required for local Postman operations
5. **Don't edit generated files**: They'll be overwritten on next build

## 🔗 Important URLs

- **Main Repo**: https://github.com/faserrao/c2m-api-repo
- **Artifacts**: https://github.com/faserrao/c2m-api-artifacts  
- **Security**: https://github.com/faserrao/c2m-api-v2-security
- **Personal Workspace**: Check Postman app
- **Team Workspace**: Check Postman app
- **Mock Server**: Check `postman/postman_mock_url.txt` after build