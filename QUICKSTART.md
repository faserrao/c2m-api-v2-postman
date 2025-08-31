# C2M API Quick Start Guide

Get up and running with the C2M API in under 15 minutes! This guide covers the essentials for both automated (GitHub) and local development workflows.

## 🚀 5-Minute Setup (GitHub)

### Prerequisites
- GitHub repository access
- [Postman account](https://www.postman.com) (free)

### Steps

1. **Get Postman API Key**
   - Log into Postman → Settings → API Keys → Generate
   - Copy the key (starts with `PMAK-`)

2. **Configure GitHub**
   - Go to repo Settings → Secrets → Actions
   - Add secret: `POSTMAN_API_KEY` = your key

3. **Set Build Target**
   - Create/edit `.postman-target` file
   - Add one line: `personal`
   - Commit the file

4. **Run Build**
   - Go to Actions tab
   - Click "Build API Spec, Collections, and Docs"
   - Click "Run workflow" → Run

5. **View Results**
   - Documentation: Check GitHub Pages URL
   - Testing: Check your Postman workspace

Done! The entire API is now built and deployed.

---

## 💻 10-Minute Local Setup

### Prerequisites
- Git, Node.js, Python 3.8+, Make
- [Installation guide for your OS](BUILD-GUIDE.md#prerequisites)

### Steps

1. **Clone & Configure**
   ```bash
   git clone https://github.com/[your-org]/c2m-api-repo.git
   cd c2m-api-repo
   cp .env.example .env
   # Edit .env and add your POSTMAN_SERRAO_API_KEY
   ```

2. **Install & Build**
   ```bash
   make install
   make postman-collection-build-and-test
   ```

3. **View Results**
   - Documentation: http://localhost:8080
   - Tests: Check terminal output
   - Postman: Check your workspace

---

## 🎯 Using Template Endpoints

The fastest way to integrate - use pre-configured templates!

### Send a Single Document
```bash
curl -X POST http://localhost:4010/jobs/single-doc-job-template \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "documentSourceIdentifier": "https://example.com/document.pdf",
    "jobTemplate": "standard-letter",
    "paymentDetails": {
      "paymentMethod": "purchase-order",
      "purchaseOrderNumber": "PO-12345"
    }
  }'
```

### Available Templates
- `standard-letter` - First-class mail, B&W
- `color-marketing` - Marketing mail, full color
- `certified-mail` - Certified with tracking
- `priority-express` - Express next-day

---

## 📋 Essential Commands

### Development Workflow
```bash
make install                          # First-time setup
make postman-collection-build-and-test # Full build & test
make docs-serve                       # View docs locally
make prism-start                      # Start mock server
```

### Testing
```bash
make test                            # Run all tests
make prism-mock-test                 # Test against local mock
make postman-mock                    # Test against cloud mock
```

### Cleanup & Maintenance
```bash
make clean                           # Remove generated files
make postman-cleanup-all             # Delete Postman resources
make smart-rebuild                   # Rebuild only changed files
```

### GitHub Actions
```bash
make openapi-build                   # Build spec (CI/CD alias)
make postman-publish                 # Publish to Postman
make docs                            # Build documentation
```

---

## 🔧 Common Tasks

### Update API from Data Dictionary
1. Edit EBNF files in `data_dictionary/`
2. Run `make postman-collection-build-and-test`
3. Changes automatically propagate through pipeline

### Add Custom Tests
1. Create `postman/custom/overrides.json`
2. Add your test scripts
3. Rebuild collections

### Switch Workspaces
```bash
echo "corporate" > .postman-target  # Switch to corporate
make postman-publish                # Publish to new workspace
```

### Debug Issues
```bash
make postman-api-debug-B            # Debug Postman connection
make print-openapi-vars             # Check configuration
make verify-urls                    # Verify collection URLs
```

---

## 📚 Next Steps

- **[Full README](README.md)** - Comprehensive documentation
- **[Build Guide](BUILD-GUIDE.md)** - Detailed setup instructions
- **[Template Guide](TEMPLATE_ENDPOINTS_QUICKSTART.md)** - Template endpoint details
- **[JWT Guide](JWT_AUTHENTICATION_README.md)** - Authentication setup

---

## 🆘 Quick Help

### Issue: "Command not found"
```bash
make install  # Installs all dependencies
```

### Issue: "Postman API error"
Check `.env` file - no spaces after API key!

### Issue: "Port in use"
```bash
make prism-stop  # Stop mock server
# Or change port in .env: PRISM_PORT=4011
```

### Issue: Build fails in GitHub
1. Check Actions tab for error details
2. Verify secrets are set correctly
3. Ensure `.postman-target` file exists

---

## 🎉 Success Checklist

- [ ] API documentation viewable
- [ ] Postman collections created
- [ ] Mock server running
- [ ] Tests passing
- [ ] Can send test requests

**Ready to build?** Choose GitHub (easiest) or local setup above and get started!