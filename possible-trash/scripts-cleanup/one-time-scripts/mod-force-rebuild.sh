# Backup first
cp Makefile Makefile.pre-fix2

# Rebuild target lines cleanly for the specific rules we touched
awk '
function trim(s){ sub(/^[ \t\r\n]+/,"",s); sub(/[ \t\r\n]+$/,"",s); return s }
BEGIN{ FS=":"; OFS=":" }
# Only touch these file-producing rules
$0 ~ /^(\$\(POSTMAN_API_UID_FILE\)|\$\(POSTMAN_COLLECTION_RAW\)|\$\(POSTMAN_COLLECTION_UID_FILE\)|\$\(POSTMAN_LINK_STAMP\)|\$\(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES\)|\$\(POSTMAN_TEST_COLLECTION_MERGED\)|\$\(POSTMAN_TEST_COLLECTION_WITH_TESTS\)|\$\(POSTMAN_TEST_COLLECTION_FIXED\)|\$\(POSTMAN_TEST_COLLECTION_UID_FILE\)|\$\(POSTMAN_ENV_UID_FILE\)|\$\(POSTMAN_MOCK_URL_FILE\) \$\(POSTMAN_MOCK_UID_FILE\)|\$\(REDOC_HTML_OUTPUT\) \$\(OPENAPI_BUNDLED_FILE\)|\$\(OPENAPI_LINT_STAMP\)|\$\(C2MAPIV2_OPENAPI_SPEC\)):[[:space:]]/ {
  lhs = $1
  rhs = substr($0, length(lhs)+2)         # everything after the colon (keep original whitespace intention)

  # Strip any accidental FORCE tokens from rhs first
  gsub(/\|\s*\$\((FORCE_REBUILD|FORCE)\)[ \t]*/," | ", rhs)
  gsub(/\$\((FORCE_REBUILD|FORCE)\)[ \t]*/," ", rhs)

  # Split at first pipe into normal vs order-only
  p = index(rhs, "|")
  if (p) {
    normal = trim(substr(rhs, 1, p-1))
    order  = trim(substr(rhs, p+1))
  } else {
    normal = trim(rhs)
    order  = ""
  }

  # Ensure FORCE_REBUILD is in the order-only list
  if (order ~ /\$\((FORCE_REBUILD|FORCE)\)/) {
    # ok
  } else {
    order = trim(order " $(FORCE_REBUILD)")
  }

  # Reprint with normalized spacing: "<lhs>: <normal> | <order>"
  out = lhs ":"
  if (normal != "") out = out " " normal
  if (order  != "") out = out " | " order
  print out
  next
}
{ print }
' Makefile > Makefile.fixed2 && mv Makefile.fixed2 Makefile

