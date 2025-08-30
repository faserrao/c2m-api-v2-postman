def add_tests:
{
  "event": [
    {
      "listen": "test",
      "script": {
        "type": "text/javascript",
        "exec": [
          $test1,
          $test2
        ]
      }
    }
  ]
};

walk(
  if type == "object" and has("request") then
    . + add_tests
  else .
  end
)
