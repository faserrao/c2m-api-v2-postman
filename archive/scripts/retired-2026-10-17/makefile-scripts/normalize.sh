awk '
function trim(s){gsub(/^[ \t]+|[ \t]+$/,"",s); return s}

BEGIN{
  target["$(C2MAPIV2_OPENAPI_SPEC)"]=1
  target["$(OPENAPI_LINT_STAMP)"]=1
  target["$(POSTMAN_API_UID_FILE)"]=1
  target["$(POSTMAN_COLLECTION_RAW)"]=1
  target["$(POSTMAN_COLLECTION_UID_FILE)"]=1
  target["$(POSTMAN_LINK_STAMP)"]=1
  target["$(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES)"]=1
  target["$(POSTMAN_TEST_COLLECTION_MERGED)"]=1
  target["$(POSTMAN_TEST_COLLECTION_WITH_TESTS)"]=1
  target["$(POSTMAN_TEST_COLLECTION_FIXED)"]=1
  target["$(POSTMAN_TEST_COLLECTION_UID_FILE)"]=1
  target["$(POSTMAN_ENV_UID_FILE)"]=1
  target["$(POSTMAN_MOCK_URL_FILE) $(POSTMAN_MOCK_UID_FILE)"]=1
  target["$(REDOC_HTML_OUTPUT) $(OPENAPI_BUNDLED_FILE)"]=1
}

/^[^:]+:/ {
  line=$0
  split(line,a,":")
  tgt=a[1]
  rest=substr(line,length(tgt)+2)

  if(!(tgt in target)){ print line; next }

  # split at the FIRST '|' only
  p=index(rest,"|")
  if(p==0){
    normal=trim(rest); order=""
  }else{
    normal=trim(substr(rest,1,p-1))
    order =trim(substr(rest,p+1))
    gsub(/\|/," ",order)  # collapse extra pipes
    order=trim(order)
  }

  # ensure FORCE_REBUILD is in the order-only set (once)
  if(order !~ /\$\((FORCE|FORCE_REBUILD)\)/){
    order = (order?order" ":"")"$(FORCE_REBUILD)"
  }

  out=tgt":"
  if(normal!="") out=out" "normal
  if(order!="")  out=out" | "order
  print out
  next
}

{ print }
' Makefile > Makefile.new && cp -i Makefile Makefile.bak.normalize && mv Makefile.new Makefile

