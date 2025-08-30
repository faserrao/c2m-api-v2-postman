walk(
  if type == "object"
     and (has("url"))
     and ((.url | type) == "object")
     and (.url.raw)
  then .url.raw |= sub("http://localhost"; "{{baseUrl}}")
  else .
  end
)

