{
  name: $name,
  type: $type,
  files: [
    {
      path: $path,
      content: ($content | fromjson)
    }
  ]
}