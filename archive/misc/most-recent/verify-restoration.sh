#!/bin/bash
# Verify the restoration was successful

echo "🔍 Verifying C2M API Restoration..."
echo "=================================="

# Check Makefile size
echo "📏 Checking Makefile size..."
MAKEFILE_LINES=$(wc -l < Makefile)
echo "   Lines in Makefile: $MAKEFILE_LINES"
if [ "$MAKEFILE_LINES" -lt 2500 ]; then
    echo "   ✅ Makefile is reasonable size (not bloated)"
else
    echo "   ⚠️  Makefile seems large, might have redundant targets"
fi

# Check for original scripts
echo ""
echo "📂 Checking for original scripts..."
SCRIPTS_OK=true
for script in "scripts/active/add_tests.js" "scripts/active/validate_collection.js"; do
    if [ -f "$script" ]; then
        echo "   ✅ Found: $script"
    else
        echo "   ❌ Missing: $script"
        SCRIPTS_OK=false
    fi
done

# Check for auth scripts that should NOT be here
echo ""
echo "🚫 Checking for scripts that belong in security repo..."
AUTH_SCRIPTS_OK=true
for script in "scripts/active/add_auth_examples.js" "scripts/active/fetch_aws_credentials.sh"; do
    if [ ! -f "$script" ]; then
        echo "   ✅ Correctly absent: $script"
    else
        echo "   ⚠️  Found auth script that belongs in security repo: $script"
        AUTH_SCRIPTS_OK=false
    fi
done

# Check for key targets
echo ""
echo "🎯 Checking for key Makefile targets..."
TARGETS_OK=true
for target in "postman-instance-build-and-test" "postman-cleanup-all" "postman-create-test-collection"; do
    if grep -q "^${target}:" Makefile; then
        echo "   ✅ Found target: $target"
    else
        echo "   ❌ Missing target: $target"
        TARGETS_OK=false
    fi
done

# Check for redundant auth targets
echo ""
echo "🔍 Checking for redundant auth-specific targets..."
REDUNDANT_TARGETS=0
for target in "postman-build-auth-deploy" "postman-full-auto-deploy" "postman-deploy-personal"; do
    if grep -q "^${target}:" Makefile; then
        echo "   ⚠️  Found redundant target: $target"
        ((REDUNDANT_TARGETS++))
    fi
done
if [ "$REDUNDANT_TARGETS" -eq 0 ]; then
    echo "   ✅ No redundant auth deployment targets found"
fi

# Summary
echo ""
echo "=================================="
echo "📊 SUMMARY"
echo "=================================="
if [ "$SCRIPTS_OK" = true ] && [ "$TARGETS_OK" = true ] && [ "$AUTH_SCRIPTS_OK" = true ] && [ "$REDUNDANT_TARGETS" -eq 0 ]; then
    echo "✅ Restoration appears successful!"
    echo "   The repository is in a clean state."
else
    echo "⚠️  Some issues detected. Please review above."
fi

echo ""
echo "Next step: Test the build pipeline with:"
echo "  make postman-cleanup-all && make postman-instance-build-and-test"