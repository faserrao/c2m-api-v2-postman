# OpenapiClient::ShortTokenResponse

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **token_type** | **String** |  |  |
| **access_token** | **String** | Short-lived JWT |  |
| **expires_in** | **Integer** | Lifetime in seconds (e.g., 900 for 15 minutes) |  |
| **expires_at** | **Time** | ISO 8601 timestamp of expiration |  |
| **scopes** | **Array&lt;String&gt;** | Granted scopes | [optional] |
| **token_id** | **String** | Server-issued identifier for this token | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::ShortTokenResponse.new(
  token_type: null,
  access_token: null,
  expires_in: null,
  expires_at: null,
  scopes: null,
  token_id: null
)
```

