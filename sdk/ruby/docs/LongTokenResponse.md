# OpenapiClient::LongTokenResponse

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **token_type** | **String** |  |  |
| **access_token** | **String** | Long-lived token (opaque or JWT depending on deployment) |  |
| **expires_in** | **Integer** | Lifetime in seconds |  |
| **expires_at** | **Time** | ISO 8601 timestamp of expiration |  |
| **scopes** | **Array&lt;String&gt;** | Granted scopes | [optional] |
| **token_id** | **String** | Server-issued identifier for this token | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::LongTokenResponse.new(
  token_type: null,
  access_token: null,
  expires_in: null,
  expires_at: null,
  scopes: null,
  token_id: null
)
```

