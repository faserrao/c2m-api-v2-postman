# OpenapiClient::ShortTokenRequest

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **long_token** | **String** | Optional if the long-term token is provided in Authorization header | [optional] |
| **scopes** | **Array&lt;String&gt;** | Optional scope narrowing; defaults to the long-term token&#39;s scopes | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::ShortTokenRequest.new(
  long_token: null,
  scopes: null
)
```

