# 📦 LOB API Testing Template

A GitHub-ready, Docker-compatible template for testing LOB-style APIs using Postman and Schemathesis.

## 🚀 Features

- 🔐 JWT Auth, tagged environments (Dev, Staging, Prod)
- ✅ Newman tests with HTML + JUnit reports
- 🔁 Schemathesis OpenAPI schema fuzz testing
- 🧪 GitHub Actions with alerts and coverage dashboard
- 🐳 Dockerfile for local test automation

## 🐳 Run Locally with Docker

```bash
docker build -t lob-api-tests .
docker run --rm -v $PWD:/tests lob-api-tests
```

## ✅ GitHub Actions

- `.github/workflows/postman-tests.yml`: matrix test runner
- `.github/workflows/schemathesis-coverage.yml`: OpenAPI contract coverage

## 📁 Postman Collections

- `postman/lob_postman_collection_monitor_ready.json` – used in CI/CD
- `postman/lob_postman_generated_with_examples_and_tests.json` – generated from OpenAPI

---

© 2025 · Template maintained by Frank Serrao