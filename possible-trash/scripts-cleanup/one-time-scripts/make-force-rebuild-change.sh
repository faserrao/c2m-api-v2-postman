cat > /tmp/add_force_rebuild.awk <<'AWK'
BEGIN {
  T = "^(\\$\\(POSTMAN_API_UID_FILE\\)|\\$\\(POSTMAN_COLLECTION_RAW\\)|\\$\\(POSTMAN_COLLECTION_UID_FILE\\)|\\$\\(POSTMAN_LINK_STAMP\\)|\\$\\(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES\\)|\\$\\(POSTMAN_TEST_COLLECTION_MERGED\\)|\\$\\(POSTMAN_TEST_COLLECTION_WITH_TESTS\\)|\\$\\(POSTMAN_TEST_COLLECTION_FIXED\\)|\\$\\(POSTMAN_TEST_COLLECTION_UID_FILE\\)|\\$\\(POSTMAN_ENV_UID_FILE\\)|\\$\\(POSTMAN_MOCK_URL_FILE\\) \\$\\(POSTMAN_MOCK_UID_FILE\\)|\\$\\(REDOC_HTML_OUTPUT\\) \\$\\(OPENAPI_BUNDLED_FILE\\)|\\$\\(OPENAPI_LINT_STAMP\\)|\\$\\(C2MAPIV2_OPENAPI_SPEC\\)):";
}
$0 ~ T {
  if ($0 !~ /\|\s*\$\((FORCE|FORCE_REBUILD)\)/) {
    sub(/:[[:space:]]*/, "&| $(FORCE_REBUILD) ");
  }
}
{ print }
AWK

cp Makefile Makefile.bak
awk -f /tmp/add_force_rebuild.awk Makefile > Makefile.new && mv Makefile.new Makefile

