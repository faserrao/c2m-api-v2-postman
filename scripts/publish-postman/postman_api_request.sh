#!/bin/bash
# One Postman API call that fails loudly.
# Usage: postman_api_request.sh METHOD URL [curl args, e.g. --header ...]
# Prints the response body. Exits 1 if the request fails or the status is not 2xx;
# a 404 on DELETE counts as success (the resource is already gone).
# Used by the Makefile cleanup targets: curl --silent alone exits 0 on HTTP errors,
# so a refused list call looked like an empty workspace and a refused delete was ignored.
# Transport failures (dropped connection, HTTP/2 framing error, timeout) are retried a
# few times; an HTTP error status is not retried here and fails at once. Retrying a
# DELETE is safe: if the first attempt went through, the retry gets 404 (accepted).

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 METHOD URL [curl args...]" >&2
  exit 2
fi

method=$1
url=$2
shift 2

body=$(mktemp)
trap 'rm -f "$body"' EXIT

code=$(curl --silent --location --retry 3 --retry-delay 2 --retry-all-errors \
    --request "$method" "$url" "$@" \
    --output "$body" --write-out '%{http_code}') || {
  rc=$?
  echo "❌ $method $url: request failed (curl exit $rc)" >&2
  exit 1
}

if [[ $code == 2* ]] || { [ "$method" = "DELETE" ] && [ "$code" = "404" ]; }; then
  cat "$body"
  exit 0
fi

echo "❌ $method $url → HTTP $code" >&2
head -c 500 "$body" >&2
echo >&2
exit 1
