# OpenapiClient::AuthError

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **code** | **String** | OAuth-style error code |  |
| **message** | **String** | Human-readable error message |  |
| **details** | **Object** | Additional error details | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::AuthError.new(
  code: invalid_grant,
  message: The provided client credentials are invalid.,
  details: null
)
```

