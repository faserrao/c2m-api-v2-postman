#!/bin/bash

# Set development context for local builds
# Usage: ./scripts/utilities/set-context.sh [personal|click2mail]

set -e

CONTEXT=$1
CONTEXT_FILE=".git-context"

if [ -z "$CONTEXT" ]; then
    echo "Usage: $0 [personal|click2mail]"
    echo ""
    echo "Current context: $(cat $CONTEXT_FILE 2>/dev/null || echo 'NOT SET')"
    echo ""
    echo "Available contexts:"
    echo "  personal   - Use faserrao repo → personal Postman workspace"
    echo "  click2mail - Use click2mail repo → corporate Postman workspace"
    exit 1
fi

if [ "$CONTEXT" != "personal" ] && [ "$CONTEXT" != "click2mail" ]; then
    echo "Error: Invalid context '$CONTEXT'"
    echo "Must be 'personal' or 'click2mail'"
    exit 1
fi

# Get current git origin to verify consistency
ORIGIN_URL=$(git remote get-url origin 2>/dev/null || echo "")

if [[ "$ORIGIN_URL" == *"faserrao"* ]] && [ "$CONTEXT" = "click2mail" ]; then
    echo "Warning: Setting context to 'click2mail' but git origin is faserrao"
    echo "This is allowed but unusual. Consider using 'personal' context."
    echo ""
fi

if [[ "$ORIGIN_URL" == *"click2mail"* ]] && [ "$CONTEXT" = "personal" ]; then
    echo "Warning: Setting context to 'personal' but git origin is click2mail"
    echo "This is allowed but unusual. Consider using 'click2mail' context."
    echo ""
fi

# Set context
echo "$CONTEXT" > $CONTEXT_FILE
echo "✓ Context set to: $CONTEXT"
echo ""
echo "This will affect:"
case $CONTEXT in
    personal)
        echo "  - Postman workspace: Personal (d8a1f479-a2aa-4471-869e-b12feea0a98c)"
        echo "  - API key: POSTMAN_SERRAO_API_KEY"
        echo "  - Git remote: origin (faserrao)"
        ;;
    click2mail)
        echo "  - Postman workspace: Corporate (c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1)"
        echo "  - API key: POSTMAN_C2M_API_KEY"
        echo "  - Git remote: click2mail"
        ;;
esac
echo ""
echo "Run 'make postman-instance-build-with-tests' to build with this context."
