#!/bin/bash
# Generate Postman environment file with credentials

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_TEMPLATE_FILE="${1:-}"
OUTPUT_FILE="${2:-}"

# Default values
DEFAULT_CLIENT_ID="${C2M_CLIENT_ID:-test-client-123}"
DEFAULT_CLIENT_SECRET="${C2M_CLIENT_SECRET:-super-secret-password-123}"
DEFAULT_BASE_URL="${C2M_BASE_URL:-https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev}"
DEFAULT_AUTH_URL="${C2M_AUTH_URL:-https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev}"

# Function to generate environment JSON
generate_env_json() {
    local client_id="$1"
    local client_secret="$2"
    local base_url="$3"
    local auth_url="${4:-$base_url}"  # Default to base_url if not provided
    
    cat <<EOF
{
  "environment": {
    "name": "${ENV_NAME:-C2M API - Auto-Generated}",
    "values": [
      {
        "key": "baseUrl",
        "value": "$base_url",
        "type": "default",
        "enabled": true
      },
      {
        "key": "authUrl",
        "value": "$auth_url",
        "type": "default",
        "enabled": true
      },
      {
        "key": "clientId", 
        "value": "$client_id",
        "type": "default",
        "enabled": true
      },
      {
        "key": "clientSecret",
        "value": "$client_secret",
        "type": "secret",
        "enabled": true
      },
      {
        "key": "longTermToken",
        "value": "",
        "type": "secret",
        "enabled": true
      },
      {
        "key": "shortTermToken",
        "value": "",
        "type": "secret", 
        "enabled": true
      },
      {
        "key": "tokenExpiry",
        "value": "",
        "type": "default",
        "enabled": true
      },
      {
        "key": "currentTokenId",
        "value": "",
        "type": "default",
        "enabled": true
      },
      {
        "key": "longTokenId",
        "value": "",
        "type": "default",
        "enabled": true
      },
      {
        "key": "longTokenExpiry",
        "value": "",
        "type": "default",
        "enabled": true
      }
    ]
  }
}
EOF
}

# Function to update existing environment file
update_env_file() {
    local template_file="$1"
    local client_id="$2"
    local client_secret="$3"
    local base_url="$4"
    local auth_url="${5:-$base_url}"  # Default to base_url if not provided
    
    if command -v jq &> /dev/null; then
        # Use jq to update values - handle both wrapped and unwrapped formats
        jq --arg client_id "$client_id" \
           --arg client_secret "$client_secret" \
           --arg base_url "$base_url" \
           --arg auth_url "$auth_url" \
           'if .environment then
               .environment.values |= map(
                   if .key == "clientId" then .value = $client_id
                   elif .key == "clientSecret" then .value = $client_secret
                   elif .key == "baseUrl" then .value = $base_url
                   elif .key == "authUrl" then .value = $auth_url
                   else . end
               )
           else
               .values |= map(
                   if .key == "clientId" then .value = $client_id
                   elif .key == "clientSecret" then .value = $client_secret
                   elif .key == "baseUrl" then .value = $base_url
                   elif .key == "authUrl" then .value = $auth_url
                   else . end
               )
           end' "$template_file"
    else
        # Fallback to generate new file
        echo "⚠️  jq not found, generating new environment file" >&2
        generate_env_json "$client_id" "$client_secret" "$base_url" "$auth_url"
    fi
}

# Main execution
main() {
    # Get credentials from environment or use defaults
    CLIENT_ID="${C2M_CLIENT_ID:-$DEFAULT_CLIENT_ID}"
    CLIENT_SECRET="${C2M_CLIENT_SECRET:-$DEFAULT_CLIENT_SECRET}"
    BASE_URL="${C2M_BASE_URL:-$DEFAULT_BASE_URL}"
    AUTH_URL="${C2M_AUTH_URL:-$DEFAULT_AUTH_URL}"
    
    echo "🔧 Generating Postman environment with credentials..." >&2
    
    # Generate or update environment file
    if [[ -n "$ENV_TEMPLATE_FILE" && -f "$ENV_TEMPLATE_FILE" ]]; then
        # Update existing template
        result=$(update_env_file "$ENV_TEMPLATE_FILE" "$CLIENT_ID" "$CLIENT_SECRET" "$BASE_URL" "$AUTH_URL")
    else
        # Generate new file
        result=$(generate_env_json "$CLIENT_ID" "$CLIENT_SECRET" "$BASE_URL" "$AUTH_URL")
    fi
    
    # Output to file or stdout
    if [[ -n "$OUTPUT_FILE" ]]; then
        echo "$result" > "$OUTPUT_FILE"
        echo "✅ Environment file written to: $OUTPUT_FILE" >&2
    else
        echo "$result"
    fi
}

# Run main function
main