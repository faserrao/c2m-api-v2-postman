#!/usr/bin/env bash

# === Prism Test Script ===
# Extracts request body for a given endpoint from a Postman collection and sends it to Prism mock.

COLLECTION_FILE="postman/generated/c2mapiv2-collection-fixed.json"
PRISM_URL="http://127.0.0.1:4010"
OUTPUT_FILE="prism_test_body.json"

ENDPOINT="$1"
ACTION="$2"  # Optional: --list or --select <n>
SELECT_INDEX=1

if [[ -z "$ENDPOINT" ]]; then
  echo "Usage: $0 <endpoint> [--list | --select <index>]"
  exit 1
fi

# If --select is specified, get the index
if [[ "$ACTION" == "--select" ]]; then
  if [[ -z "$3" ]]; then
    echo "❌ Missing index for --select"
    exit 1
  fi
  SELECT_INDEX="$3"
fi

echo "🔍 Searching for request body in collection for endpoint: $ENDPOINT ..."

# Extract all matching request bodies (escaped JSON strings)
RAW_BODIES=$(jq -r \
  --arg endpoint "$ENDPOINT" \
  '.. | objects | select(has("request")) | select(.request.url.raw | contains($endpoint)) | .request.body.raw // empty' \
  "$COLLECTION_FILE")

BODY_COUNT=$(echo "$RAW_BODIES" | wc -l | tr -d ' ')

if [[ "$BODY_COUNT" -eq 0 ]]; then
  echo "❌ No request body found for endpoint: $ENDPOINT"
  exit 1
fi

if [[ "$ACTION" == "--list" ]]; then
  echo "📋 Found $BODY_COUNT request bodies:"
  INDEX=1
  echo "$RAW_BODIES" | while read -r line; do
    echo "[$INDEX] $(echo "$line" | jq -r . | jq -c .)"
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

# Unescape the JSON string
UNESCAPED_BODY=$(echo "$SELECTED_BODY" | jq -r . 2>/dev/null)

if ! echo "$UNESCAPED_BODY" | jq empty 2>/dev/null; then
  echo "❌ The selected request body (index $SELECT_INDEX) is not valid JSON."
  exit 1
fi

# Save request body
echo "$UNESCAPED_BODY" | jq . > "$OUTPUT_FILE"
echo "📦 Request body saved to $OUTPUT_FILE"

# Send to Prism mock server
echo "🚀 Sending request to Prism mock server: $PRISM_URL/$ENDPOINT"
curl --silent -X POST "$PRISM_URL/$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d @"$OUTPUT_FILE" | jq .

echo "✅ Test completed for endpoint: $ENDPOINT"
