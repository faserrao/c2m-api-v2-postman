# C2M API Quick Reference Card

## 🚀 Most Used Commands
```bash
make postman-instance-build-and-test    # Full pipeline test
make postman-cleanup-all                # Clean slate
make prism-mock-test                    # Test locally
make postman-workspace-debug            # See what's in Postman
```

## 📁 Key Files
- **Source of Truth**: `data_dictionary/c2mapiv2-dd.ebnf`
- **Main Orchestrator**: `Makefile`
- **Project Memory**: `user-guides/PROJECT_MEMORY.md`
- **Auth Hook**: `postman/scripts/jwt-pre-request.js`

## 🔄 Pipeline Flow
```
EBNF → OpenAPI → Postman → Mock → Tests → Docs
```

## ⚠️ Common Issues & Fixes

### Tests Failing with Status Codes
```bash
# Check allowed codes in Makefile
POSTMAN_ALLOWED_CODES = 200,201,204,400,401,403,404,429
```

### OpenAPI Spec Not Showing in Postman
```bash
# ❌ WRONG (double encodes)
CONTENT=$(jq -Rs . < "$(SPEC_FILE)")

# ✅ CORRECT
CONTENT=$(cat "$(SPEC_FILE)")
```

### Workspace Publishing Issues
```bash
# Set target workspace
echo "personal" > .postman-target
make postman-publish
```

## 🏗️ Architecture
- **Main Repo**: Core API functionality (this repo)
- **Security Repo**: JWT authentication (separate)
- **Integration**: Minimal hooks only, not full merge

## 🧪 Testing Strategy
1. Local: `make prism-mock-test`
2. Cloud: `make postman-mock`
3. Full: `make postman-instance-build-and-test`

## 📝 Documentation
- **User Guides**: `/user-guides/`
- **API Docs**: `make docs-serve` (port 8080)
- **Mock Server**: `make prism-start` (port 4010)

## 🔧 Restoration Lessons
1. Keep auth separate from main API
2. Use orchestrator patterns, not duplicate targets
3. Document everything in CLAUDE.md
4. Test before merging to main
5. Makefile should be <2000 lines

---
*Last Updated: 2025-09-08*
*Restoration Complete ✅*