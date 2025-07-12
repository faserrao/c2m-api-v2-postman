# 🧪 CI/CD: Postman Testing Pipeline

## ✅ Overview

This repo includes a GitHub Actions workflow that runs Postman collections across Dev, Staging, and Production environments. It:

- Validates endpoint responses
- Uploads test results as artifacts
- Triggers webhook alerts on failures

## 📂 Files

- `.github/workflows/postman-tests.yml`: GitHub Actions workflow
- `postman/c2m_postman_collection_monitor_ready.json`: Collection
- `postman/c2m_postman_environment_*.json`: Environments (dev, staging, prod)

## 🔁 Triggered By

- `push` to `main`
- Scheduled: Daily at 12PM UTC
- Manual: From GitHub Actions tab

## 🔔 Webhook Alerts

Add a secret in your repo:

```
POSTMAN_ALERT_WEBHOOK=https://hooks.example.com/postman-alert
```

You’ll get a `POST` payload like:

```json
{
  "message": "🚨 Postman tests failed in production",
  "repo": "your-org/c2m-api",
  ...
}
```

## 📥 Test Reports

You’ll see downloadable `.xml` test results per environment.

## 🛠 Customize

- Add more environments or conditions in `matrix`
- Add more test assertions inside Postman
- Add custom alerts via Slack, Email, Discord, Zapier, etc.

---

© 2025 · Maintained by Frank Serrao