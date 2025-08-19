walk(
  if type == "object" and (has("name") and (has("request") | not) and (has("item") | not))
  then . + { "item": [] }
  else .
  end
)
