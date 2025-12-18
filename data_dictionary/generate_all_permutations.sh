#!/bin/bash
#
# Generate permutations for all C2M API V2 endpoints
#
# This script automates the generation of test data permutations for all
# /jobs/submit/... endpoints by calling the permutation generator for each.

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "Generating Permutations for All Endpoints"
echo "============================================================"
echo

# All 8 current endpoints
ENDPOINTS=(
    1  # submitMultiDocMergeParams
    2  # submitMultiDocParams
    3  # submitMultiZipAddressCaptureParams
    4  # submitMultiZipParams
    5  # submitSingleDocParams
    6  # submitSinglePdfAddressCaptureParams
    7  # submitSinglePdfSplitAddressCaptureParams
    8  # submitSinglePdfSplitParams
)

ENDPOINT_NAMES=(
    "submitMultiDocMergeParams"
    "submitMultiDocParams"
    "submitMultiZipAddressCaptureParams"
    "submitMultiZipParams"
    "submitSingleDocParams"
    "submitSinglePdfAddressCaptureParams"
    "submitSinglePdfSplitAddressCaptureParams"
    "submitSinglePdfSplitParams"
)

# Generate permutations for each endpoint
for i in "${!ENDPOINTS[@]}"; do
    endpoint_num="${ENDPOINTS[$i]}"
    endpoint_name="${ENDPOINT_NAMES[$i]}"

    echo "[$((i+1))/8] Generating: $endpoint_name"
    echo "$endpoint_num" | python3 generate_endpoint_permutations.py > /dev/null 2>&1

    # Count permutations generated
    if [ -f "permutations/${endpoint_name}.json" ]; then
        count=$(jq '.permutations | length' "permutations/${endpoint_name}.json")
        size=$(ls -lh "permutations/${endpoint_name}.json" | awk '{print $5}')
        echo "    Generated: $count permutations ($size)"
    else
        echo "    ERROR: Failed to generate permutations"
    fi
    echo
done

echo "============================================================"
echo "Summary"
echo "============================================================"
echo
echo "Permutation files generated:"
ls -lh permutations/*.json
echo
echo "Total permutations by endpoint:"
for name in "${ENDPOINT_NAMES[@]}"; do
    if [ -f "permutations/${name}.json" ]; then
        count=$(jq '.permutations | length' "permutations/${name}.json")
        printf "  %-45s %6d permutations\n" "$name" "$count"
    fi
done
echo
echo "SUCCESS: All permutations generated"
echo
