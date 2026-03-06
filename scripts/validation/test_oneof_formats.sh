#!/bin/bash
#
# Test oneOf Union Format Validation
#
# Purpose: Test whether Prism strict validation accepts:
#   - Primitive format: "docSourceAll": 12345
#   - Tagged union format: "docSourceAll": { "documentId": 12345 }
#
# Usage: ./test_oneof_formats.sh
#
# Prerequisites:
#   - Prism CLI installed: npm install -g @stoplight/prism-cli
#   - OpenAPI spec generated: make generate-openapi-spec-from-ebnf-dd
#
# Exit Codes:
#   0 = All tests passed
#   1 = Some tests failed
#   2 = Prism not running or script error

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OPENAPI_SPEC="openapi/c2mapiv2-openapi-spec-base.yaml"
PRISM_PORT=4010
PRISM_URL="http://localhost:${PRISM_PORT}"
PRISM_PID_FILE="/tmp/prism_test_oneof.pid"

# Test results
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Cleanup function
cleanup() {
    if [ -f "$PRISM_PID_FILE" ]; then
        echo -e "\n${BLUE}[CLEANUP]${NC} Stopping Prism mock server..."
        PID=$(cat "$PRISM_PID_FILE")
        kill "$PID" 2>/dev/null || true
        rm -f "$PRISM_PID_FILE"
        echo -e "${GREEN}[CLEANUP]${NC} Prism stopped"
    fi
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Print header
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}  oneOf Format Validation Test Suite${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Print section
print_section() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

# Print test name
print_test() {
    echo -e "${BLUE}[TEST $TESTS_RUN]${NC} $1"
}

# Print result
print_result() {
    local status=$1
    local message=$2

    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC} - $message"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC} - $message"
        ((TESTS_FAILED++))
    fi
}

# Check prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"

    # Check if Prism is installed
    if ! command -v prism &> /dev/null; then
        echo -e "${RED}ERROR:${NC} Prism CLI not found"
        echo -e "Install with: ${YELLOW}npm install -g @stoplight/prism-cli${NC}"
        exit 2
    fi
    echo -e "${GREEN}✓${NC} Prism CLI installed: $(prism --version)"

    # Check if OpenAPI spec exists
    if [ ! -f "$OPENAPI_SPEC" ]; then
        echo -e "${RED}ERROR:${NC} OpenAPI spec not found: $OPENAPI_SPEC"
        echo -e "Generate with: ${YELLOW}make generate-openapi-spec-from-ebnf-dd${NC}"
        exit 2
    fi
    echo -e "${GREEN}✓${NC} OpenAPI spec found: $OPENAPI_SPEC"

    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}ERROR:${NC} curl not found"
        exit 2
    fi
    echo -e "${GREEN}✓${NC} curl available"

    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}ERROR:${NC} jq not found (required for JSON parsing)"
        echo -e "Install with: ${YELLOW}brew install jq${NC}"
        exit 2
    fi
    echo -e "${GREEN}✓${NC} jq available"
}

# Start Prism mock server
start_prism() {
    print_section "Starting Prism Mock Server"

    # Check if Prism is already running on port
    if lsof -Pi :${PRISM_PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}WARNING:${NC} Port ${PRISM_PORT} already in use"
        echo -e "Attempting to kill existing process..."
        lsof -ti:${PRISM_PORT} | xargs kill -9 2>/dev/null || true
        sleep 2
    fi

    # Start Prism in strict mode with validation errors
    echo "Starting Prism with strict validation..."
    prism mock "$OPENAPI_SPEC" \
        --port "$PRISM_PORT" \
        --errors \
        --cors \
        > /tmp/prism_test_oneof.log 2>&1 &

    PRISM_PID=$!
    echo "$PRISM_PID" > "$PRISM_PID_FILE"

    # Wait for Prism to start
    echo "Waiting for Prism to start..."
    for i in {1..10}; do
        if curl -s "${PRISM_URL}" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Prism started successfully (PID: $PRISM_PID)"
            return 0
        fi
        sleep 1
    done

    echo -e "${RED}ERROR:${NC} Prism failed to start"
    cat /tmp/prism_test_oneof.log
    exit 2
}

# Test function
test_request() {
    local test_name=$1
    local endpoint=$2
    local payload=$3
    local expected_status=$4

    ((TESTS_RUN++))
    print_test "$test_name"

    # Make request
    local response=$(curl -s -w "\n%{http_code}" \
        -X POST "${PRISM_URL}${endpoint}" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "$payload" 2>&1)

    # Extract status code and body
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    # Check status code
    if [ "$http_code" = "$expected_status" ]; then
        print_result "PASS" "HTTP $http_code (expected $expected_status)"

        # Show response body (first 200 chars)
        if [ -n "$body" ]; then
            local preview=$(echo "$body" | head -c 200)
            echo -e "  ${BLUE}Response:${NC} ${preview}..."
        fi

        return 0
    else
        print_result "FAIL" "HTTP $http_code (expected $expected_status)"

        # Show error details
        echo -e "  ${RED}Response body:${NC}"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"

        return 1
    fi
}

# Test Suite: docSourceAll (Document Source)
test_docSourceAll() {
    print_section "Test Suite 1: docSourceAll (Document Source)"

    # Test 1: Primitive format - documentId as integer
    test_request \
        "Primitive format: documentId as bare integer" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": 12345,
            "recipientAddressSource": {
                "firstName": "John",
                "lastName": "Doe",
                "address1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "jobTemplate": "test_template"
        }' \
        "200"

    # Test 2: Tagged union format - documentId wrapped in object
    test_request \
        "Tagged union format: documentId in object wrapper" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": {
                "documentId": 12345
            },
            "recipientAddressSource": {
                "firstName": "John",
                "lastName": "Doe",
                "address1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "jobTemplate": "test_template"
        }' \
        "200"

    # Test 3: Primitive format - URL as string
    test_request \
        "Primitive format: url as bare string" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": "https://example.com/document.pdf",
            "recipientAddressSource": {
                "firstName": "John",
                "lastName": "Doe",
                "address1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "jobTemplate": "test_template"
        }' \
        "200"

    # Test 4: Tagged union format - URL wrapped in object
    test_request \
        "Tagged union format: url in object wrapper" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": {
                "url": "https://example.com/document.pdf"
            },
            "recipientAddressSource": {
                "firstName": "John",
                "lastName": "Doe",
                "address1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "jobTemplate": "test_template"
        }' \
        "200"

    # Test 5: Object format - requestId + filename (valid object, not primitive)
    test_request \
        "Object format: requestId + filename (naturally an object)" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": {
                "requestId": 67890,
                "filename": "document.pdf"
            },
            "recipientAddressSource": {
                "firstName": "John",
                "lastName": "Doe",
                "address1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "jobTemplate": "test_template"
        }' \
        "200"
}

# Test Suite: recipientAddressSource
test_recipientAddressSource() {
    print_section "Test Suite 2: recipientAddressSource"

    # Test 6: Object format - single address (naturally an object)
    test_request \
        "Object format: single address" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": {
                "documentId": 12345
            },
            "recipientAddressSource": {
                "firstName": "Jane",
                "lastName": "Smith",
                "address1": "456 Oak Ave",
                "city": "Chicago",
                "state": "IL",
                "zip": "60601",
                "country": "USA"
            },
            "jobTemplate": "test_template"
        }' \
        "200"

    # Test 7: Primitive format - addressListId as string
    test_request \
        "Primitive format: addressListId as bare string" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": {
                "documentId": 12345
            },
            "recipientAddressSource": "my_address_list_123",
            "jobTemplate": "test_template"
        }' \
        "200"

    # Test 8: Tagged union format - addressListId wrapped in object
    test_request \
        "Tagged union format: addressListId in object wrapper" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": {
                "documentId": 12345
            },
            "recipientAddressSource": {
                "addressListId": "my_address_list_123"
            },
            "jobTemplate": "test_template"
        }' \
        "200"
}

# Test Suite: paymentDetails
test_paymentDetails() {
    print_section "Test Suite 3: paymentDetails"

    # Test 9: Object format - credit card details (naturally an object)
    test_request \
        "Object format: creditCard details" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": {
                "documentId": 12345
            },
            "recipientAddressSource": {
                "firstName": "John",
                "lastName": "Doe",
                "address1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "jobTemplate": "test_template",
            "paymentDetails": {
                "creditCardDetails": {
                    "cardType": "visa",
                    "cardNumber": "4111111111111111",
                    "expirationDate": {
                        "month": 12,
                        "year": 2025
                    },
                    "cvv": 123
                }
            }
        }' \
        "200"

    # Test 10: Primitive format - paymentMethodId as string
    test_request \
        "Primitive format: paymentMethodId as bare string" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": {
                "documentId": 12345
            },
            "recipientAddressSource": {
                "firstName": "John",
                "lastName": "Doe",
                "address1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "jobTemplate": "test_template",
            "paymentDetails": "payment_method_abc123"
        }' \
        "200"

    # Test 11: Tagged union format - paymentMethodId wrapped in object
    test_request \
        "Tagged union format: paymentMethodId in object wrapper" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": {
                "documentId": 12345
            },
            "recipientAddressSource": {
                "firstName": "John",
                "lastName": "Doe",
                "address1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "jobTemplate": "test_template",
            "paymentDetails": {
                "paymentMethodId": "payment_method_abc123"
            }
        }' \
        "200"
}

# Test Suite: Invalid formats (should fail)
test_invalid_formats() {
    print_section "Test Suite 4: Invalid Formats (Expected to Fail)"

    # Test 12: Invalid - wrong primitive type
    test_request \
        "Invalid: documentId as string instead of integer" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": "not_a_valid_id",
            "recipientAddressSource": {
                "firstName": "John",
                "lastName": "Doe",
                "address1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "jobTemplate": "test_template"
        }' \
        "400"

    # Test 13: Invalid - missing required field
    test_request \
        "Invalid: missing recipientAddressSource (required)" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": {
                "documentId": 12345
            },
            "jobTemplate": "test_template"
        }' \
        "400"

    # Test 14: Invalid - empty object for oneOf
    test_request \
        "Invalid: empty object for docSourceAll" \
        "/jobs/submit/single/doc" \
        '{
            "docSourceAll": {},
            "recipientAddressSource": {
                "firstName": "John",
                "lastName": "Doe",
                "address1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "jobTemplate": "test_template"
        }' \
        "400"
}

# Print summary
print_summary() {
    print_section "Test Summary"

    echo -e "Total Tests Run:    ${BLUE}${TESTS_RUN}${NC}"
    echo -e "Tests Passed:       ${GREEN}${TESTS_PASSED}${NC}"
    echo -e "Tests Failed:       ${RED}${TESTS_FAILED}${NC}"

    if [ "$TESTS_FAILED" -eq 0 ]; then
        echo -e "\n${GREEN}✓ ALL TESTS PASSED${NC}"
        return 0
    else
        echo -e "\n${RED}✗ SOME TESTS FAILED${NC}"
        return 1
    fi
}

# Print conclusions
print_conclusions() {
    print_section "Conclusions"

    echo -e "${BLUE}Based on test results:${NC}\n"

    # Analyze docSourceAll results
    echo -e "${YELLOW}1. docSourceAll (Document Source):${NC}"
    echo -e "   - Tests 1-5 show which formats Prism accepts"
    echo -e "   - If both primitive and tagged pass: Schema allows both"
    echo -e "   - If only tagged passes: Schema requires object wrapper"
    echo -e "   - If only primitive passes: Schema expects bare values\n"

    echo -e "${YELLOW}2. recipientAddressSource:${NC}"
    echo -e "   - Tests 6-8 compare object vs primitive formats"
    echo -e "   - addressListId test shows if primitives are accepted\n"

    echo -e "${YELLOW}3. paymentDetails:${NC}"
    echo -e "   - Tests 9-11 show payment variant handling"
    echo -e "   - paymentMethodId test validates primitive vs tagged\n"

    echo -e "${YELLOW}4. Recommendations:${NC}"
    echo -e "   - Review failed tests to understand Prism's expectations"
    echo -e "   - Update oneOfFixtures in addRandomDataToRaw.js if needed"
    echo -e "   - Document the official wire format based on results"
    echo -e "   - Consider updating COLLECTION_GENERATION_ARCHITECTURE.md\n"

    echo -e "${BLUE}Prism log file:${NC} /tmp/prism_test_oneof.log"
    echo -e "${BLUE}Review log with:${NC} tail -f /tmp/prism_test_oneof.log\n"
}

# Main execution
main() {
    print_header
    check_prerequisites
    start_prism

    # Run test suites
    test_docSourceAll
    test_recipientAddressSource
    test_paymentDetails
    test_invalid_formats

    # Print results
    print_summary
    local exit_code=$?

    print_conclusions

    exit $exit_code
}

# Run main
main
