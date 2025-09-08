#!/bin/bash
# Fetch C2M API test credentials from AWS Secrets Manager
# This script retrieves test credentials and outputs them as environment variables

set -euo pipefail

# Configuration
SECRET_NAME="${C2M_SECRET_NAME:-c2m-api-test-credentials}"
REGION="${AWS_REGION:-us-east-1}"

# Function to check if AWS CLI is available
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        echo "❌ AWS CLI not found. Please install AWS CLI and configure credentials." >&2
        echo "   Run: pip install awscli && aws configure" >&2
        exit 1
    fi
}

# Function to fetch secret from AWS Secrets Manager
fetch_secret() {
    local secret_name=$1
    local region=$2
    
    echo "🔐 Fetching credentials from AWS Secrets Manager..." >&2
    
    # Fetch the secret
    local secret_json=$(aws secretsmanager get-secret-value \
        --secret-id "$secret_name" \
        --region "$region" \
        --query 'SecretString' \
        --output text 2>/dev/null) || {
        echo "❌ Failed to fetch secret '$secret_name' from AWS Secrets Manager" >&2
        echo "   Make sure you have appropriate AWS permissions and the secret exists" >&2
        exit 1
    }
    
    echo "$secret_json"
}

# Function to parse and export credentials
parse_credentials() {
    local secret_json=$1
    
    # Extract values using jq if available, otherwise use grep/sed
    if command -v jq &> /dev/null; then
        CLIENT_ID=$(echo "$secret_json" | jq -r '.client_id // .clientId // empty')
        CLIENT_SECRET=$(echo "$secret_json" | jq -r '.client_secret // .clientSecret // empty')
        BASE_URL=$(echo "$secret_json" | jq -r '.base_url // .baseUrl // empty')
    else
        # Fallback to basic parsing
        CLIENT_ID=$(echo "$secret_json" | grep -o '"client_id"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
        CLIENT_SECRET=$(echo "$secret_json" | grep -o '"client_secret"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
        BASE_URL=$(echo "$secret_json" | grep -o '"base_url"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
    fi
    
    # Use default values if not found in secret
    CLIENT_ID="${CLIENT_ID:-test-client-123}"
    CLIENT_SECRET="${CLIENT_SECRET:-super-secret-password-123}"
    BASE_URL="${BASE_URL:-https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev}"
    
    # Output as environment variable exports
    cat <<EOF
export C2M_CLIENT_ID="$CLIENT_ID"
export C2M_CLIENT_SECRET="$CLIENT_SECRET"
export C2M_BASE_URL="$BASE_URL"
EOF
}

# Main execution
main() {
    # Check if we should use local defaults (for CI/CD or local testing)
    if [[ "${USE_LOCAL_CREDS:-false}" == "true" ]]; then
        echo "ℹ️  Using local test credentials (USE_LOCAL_CREDS=true)" >&2
        cat <<EOF
export C2M_CLIENT_ID="test-client-123"
export C2M_CLIENT_SECRET="super-secret-password-123"
export C2M_BASE_URL="https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev"
EOF
        exit 0
    fi
    
    # Check AWS CLI
    check_aws_cli
    
    # Fetch and parse credentials
    secret_json=$(fetch_secret "$SECRET_NAME" "$REGION")
    parse_credentials "$secret_json"
    
    echo "✅ Credentials fetched successfully" >&2
}

# Run main function
main