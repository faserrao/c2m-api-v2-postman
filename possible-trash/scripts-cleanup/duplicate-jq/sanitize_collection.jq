walk(
  if type == "string" then
    gsub("<string>"; "example")
    | gsub("<integer>"; "123")
    | gsub("<number>"; "1.23")
    | gsub("<boolean>"; "true")
  else .
  end
)
