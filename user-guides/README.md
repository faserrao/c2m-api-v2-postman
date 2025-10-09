# C2M API V2 User Guides

**📖 For comprehensive documentation, see [REPOSITORY_GUIDE.md](./REPOSITORY_GUIDE.md)**

This directory contains documentation for understanding and working with the C2M API v2 build system and infrastructure.

---

## 🚀 Quick Start

**New to C2M API?** Start here:

1. **Read [REPOSITORY_GUIDE.md](./REPOSITORY_GUIDE.md)** - Comprehensive guide with Cliff Notes section for quick reference
2. **Run `make check-env`** - Verify your local setup
3. **Execute `make postman-instance-build-and-test`** - Run complete build pipeline
4. **Check generated artifacts** - Look in `dist/`, `docs/`, and `postman/` directories

---

## 📚 Primary Documentation

### [REPOSITORY_GUIDE.md](./REPOSITORY_GUIDE.md) ⭐ **START HERE**

**Comprehensive single-source guide that consolidates 50+ scattered documents:**
- 📖 **Cliff Notes** (2-page quick reference)
- Build pipeline (EBNF → OpenAPI → Postman → Tests → Docs)
- Makefile orchestration
- Smart rebuild system
- Testing strategies
- Deployment procedures
- Troubleshooting

---

## 📋 Additional Documentation

### For Management

- **[EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)** - High-level project overview
- **[PROJECT_ACCOMPLISHMENTS_SUMMARY.md](./PROJECT_ACCOMPLISHMENTS_SUMMARY.md)** - Key achievements and milestones

### Directory Organization

Documentation is organized into topic-based subdirectories:

- **getting-started/** - Onboarding, quick reference, build guide
- **authentication/** - JWT authentication, Cognito setup
- **development/** - SDK generation, Postman usage, CI/CD
- **api-reference/** - Template endpoints, job tracking
- **architecture/** - PROJECT_MEMORY.md, CLAUDE.md
- **project-reports/** - Status reports, analysis
- **archive/** - Historical docs (preserved for reference)

---

## 🔧 Essential Commands

```bash
# Complete build pipeline
make postman-instance-build-and-test

# Clean and rebuild
make postman-cleanup-all

# Test with local mock
make prism-mock-test

# Smart rebuild (only changed files)
make smart-rebuild

# View all available targets
make help
```

See [REPOSITORY_GUIDE.md](./REPOSITORY_GUIDE.md) for complete command reference.

---

## 🏗️ Architecture

The system follows a data-driven pipeline:

```
EBNF Data Dictionary → OpenAPI Spec → Postman Collections → Mock Server → Tests → Docs/SDKs
```

**Single Source of Truth**: `data_dictionary/c2mapiv2-dd.ebnf`

See [REPOSITORY_GUIDE.md](./REPOSITORY_GUIDE.md) for detailed architecture documentation.

---

## 📁 Related Repositories

This repository is part of a 4-repository ecosystem:

1. **c2m-api-repo** (this repo) - Source of truth
2. **c2m-api-artifacts** - Generated artifacts (OpenAPI, SDKs, docs)
3. **c2m-api-v2-security** - JWT authentication service
4. **click2endpoint-aws** - Interactive endpoint wizard

See **[C2M_API_V2_SYSTEM_ARCHITECTURE.md](../C2M_API_V2_SYSTEM_ARCHITECTURE.md)** for multi-repo overview.

---

## 🗂️ Archive

Previous versions of documentation are preserved in the `archive/` subdirectory and `archive/root-level-docs/` for historical reference.

---

## 🆘 Getting Help

1. **Check [REPOSITORY_GUIDE.md](./REPOSITORY_GUIDE.md)** - Comprehensive troubleshooting section
2. **Review Makefile comments** - Inline documentation for all targets
3. **Check GitHub Actions logs** - CI/CD workflow diagnostics
4. **See [PROJECT_MEMORY.md](./architecture/PROJECT_MEMORY.md)** - Historical context and decisions

---

*Last Updated: 2025-10-08*
*Version: 3.0 - Consolidated into REPOSITORY_GUIDE.md*
