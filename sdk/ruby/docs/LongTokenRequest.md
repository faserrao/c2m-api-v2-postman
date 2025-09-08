# OpenapiClient::LongTokenRequest

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **grant_type** | **String** | The authentication grant type |  |
| **client_id** | **String** | Client identifier issued by Click2Mail |  |
| **client_secret** | **String** | Required if using client_credentials with secret | [optional] |
| **otp_code** | **String** | Required if your policy mandates OTP for issuance | [optional] |
| **assertion_type** | **String** | Required when grant_type&#x3D;assertion | [optional] |
| **assertion** | **String** | Signed JWT or other accepted assertion | [optional] |
| **scopes** | **Array&lt;String&gt;** | Scopes to assign to the long-term token | [optional] |
| **ttl_seconds** | **Integer** | Requested lifetime (1 hour - 90 days). Server may clamp. | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::LongTokenRequest.new(
  grant_type: null,
  client_id: null,
  client_secret: null,
  otp_code: null,
  assertion_type: null,
  assertion: null,
  scopes: null,
  ttl_seconds: null
)
```

