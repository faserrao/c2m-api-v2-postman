walk(
  if type == "object" and has("url") and (.url.path|type) == "array" then
    .url.path |= map(
      if . == "jobtemplate" then "jobTemplate"
      elif . == "addresscapture" then "addressCapture"
      else . end
    )
  else . end
)
