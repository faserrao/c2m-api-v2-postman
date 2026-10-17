#!/usr/bin/env bash
set -uo pipefail   # explicit checks below; exits 1 when Prism answers 4xx/5xx

# === Prism Test Script ===
# Extracts the request body for an endpoint (e.g. /static) from a Postman collection and sends it
# to a running Prism mock (make prism-start). Defaults to the Test collection, which has real values.
# Overridable: COLLECTION_FILE, PRISM_URL, OUTPUT_FILE, AUTH_TOKEN.

COLLECTION_FILE="${COLLECTION_FILE:-postman/generated/c2mapiv2-test-collection-flat.json}"
PRISM_URL="${PRISM_URL:-http://127.0.0.1:4010}"
OUTPUT_FILE="${OUTPUT_FILE:-prism_test_body.json}"
AUTH_TOKEN="${AUTH_TOKEN:-dummy-token}"   # Prism checks that a bearer token is present, not its value

ENDPOINT="${1:-}"
ACTION="${2:-}"  # Optional: --list or --select <n>
SELECT_INDEX=1

if [[ -z "$ENDPOINT" ]]; then
  echo "Usage: $0 <endpoint> [--list | --select <index>]"
  exit 1
fi

# If --select is specified, get the index
if [[ "$ACTION" == "--select" ]]; then
  if [[ -z "${3:-}" ]]; then
    echo "❌ Missing index for --select"
    exit 1
  fi
  SELECT_INDEX="$3"
fi

if [[ ! -f "$COLLECTION_FILE" ]]; then
  echo "❌ Collection not found: $COLLECTION_FILE (run make postman-build-golden-test-fixtures)"
  exit 1
fi

echo "🔍 Searching for request body in collection for endpoint: $ENDPOINT ..."

# One compact JSON body per line, for requests whose path is exactly $ENDPOINT
# (bodies are stored pretty-printed; "/static" must not also match "/static/address-capture")
RAW_BODIES=$(jq -r \
  --arg endpoint "$ENDPOINT" \
  '.. | objects | select(has("request") and (.request | type) == "object")
   | select(("/" + ((.request.url.path // []) | join("/"))) == $endpoint)
   | .request.body.raw // empty | select(length > 0) | fromjson | tojson' \
  "$COLLECTION_FILE")

BODY_COUNT=$(printf '%s' "$RAW_BODIES" | grep -c . || true)

if [[ "$BODY_COUNT" -eq 0 ]]; then
  echo "❌ No request body found for endpoint: $ENDPOINT"
  exit 1
fi

if [[ "$ACTION" == "--list" ]]; then
  echo "📋 Found $BODY_COUNT request bodies:"
  INDEX=1
  echo "$RAW_BODIES" | while read -r line; do
    echo "[$INDEX] $line"
    INDEX=$((INDEX + 1))
  done
  exit 0
fi

if [[ "$BODY_COUNT" -gt 1 ]]; then
  echo "⚠️  Found $BODY_COUNT matching request bodies."
  echo "   Using the request body at index: $SELECT_INDEX"
fi

# Select the desired body
SELECTED_BODY=$(echo "$RAW_BODIES" | sed -n "${SELECT_INDEX}p")

if [[ -z "$SELECTED_BODY" ]]; then
  echo "❌ No request body at index $SELECT_INDEX (found $BODY_COUNT)"
  exit 1
fi

# Save request body
echo "$SELECTED_BODY" | jq . > "$OUTPUT_FILE"
echo "📦 Request body saved to $OUTPUT_FILE"

# Send to Prism mock server
echo "🚀 Sending request to Prism mock server: $PRISM_URL$ENDPOINT"
RESPONSE=$(curl --silent -X POST "$PRISM_URL$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -w '\n%{http_code}' \
  -d @"$OUTPUT_FILE") || { echo "❌ Could not reach Prism at $PRISM_URL (make prism-start)"; exit 1; }
STATUS="${RESPONSE##*$'\n'}"
echo "${RESPONSE%$'\n'*}"
echo "HTTP $STATUS"

if [[ "$STATUS" -ge 400 ]]; then
  echo "❌ Prism rejected the request for $ENDPOINT (HTTP $STATUS)"
  exit 1
fi
echo "✅ Test completed for endpoint: $ENDPOINT"
