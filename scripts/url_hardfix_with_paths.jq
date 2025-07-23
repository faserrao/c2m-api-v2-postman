walk(
  if type == "object" then
    (
      # Fix casing in .url.path arrays
      if has("url") and (.url.path | type) == "array" then
        .url.path |= map(
          if . == "jobtemplate" then "jobTemplate"
          elif . == "addresscapture" then "addressCapture"
          else . end
        )
      else . end
    )
    |
    (
      # Hard fix request.url objects
      if has("request") and (.request.url | type) == "object" then
        .request.url = {
          "raw": "{{baseUrl}}/" + ((.request.url.path // []) | join("/")),
          "host": ["{{baseUrl}}"],
          "path": (.request.url.path // [])
        }
      else . end
    )
  else .
  end
)
