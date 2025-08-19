#!/bin/bash

echo "=== Testing Postman API Key ==="
echo ""

# Load .env file
if [ -f .env ]; then
    source .env
    echo "✅ Loaded .env file"
else
    echo "❌ No .env file found"
    exit 1
fi

# Check if variable is set
if [ -n "$POSTMAN_SERRAO_API_KEY" ]; then
    echo "✅ POSTMAN_SERRAO_API_KEY is set (length: ${#POSTMAN_SERRAO_API_KEY})"
else
    echo "❌ POSTMAN_SERRAO_API_KEY is not set"
    exit 1
fi

# Test the API key directly
echo ""
echo "Testing API key with Postman API..."
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" --header "X-Api-Key: $POSTMAN_SERRAO_API_KEY" https://api.getpostman.com/me)
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

echo "HTTP Status: $HTTP_STATUS"
echo "Response:"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"

if [ "$HTTP_STATUS" = "200" ]; then
    echo ""
    echo "✅ API key is valid!"
else
    echo ""
    echo "❌ API key authentication failed"
fi

# Check what Make sees
echo ""
echo "=== Checking Makefile Variables ==="
make -n postman-api-debug-B 2>&1 | grep -E "POSTMAN_API_KEY|POSTMAN_WS" | head -5