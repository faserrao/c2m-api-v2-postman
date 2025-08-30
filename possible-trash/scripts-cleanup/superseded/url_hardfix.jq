walk(
  if type == "object" and has("request") and (.request.url|type) == "object" then
    .request.url = {
      "raw": "{{baseUrl}}/" + ((.request.url.path // []) | join("/")),
      "host": ["{{baseUrl}}"],
      "path": (.request.url.path // [])
    }
  else .
  end
)
