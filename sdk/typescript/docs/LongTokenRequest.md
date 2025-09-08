# LongTokenRequest

One of several credential mechanisms must be provided.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**grant_type** | **string** | The authentication grant type | [default to undefined]
**client_id** | **string** | Client identifier issued by Click2Mail | [default to undefined]
**client_secret** | **string** | Required if using client_credentials with secret | [optional] [default to undefined]
**otp_code** | **string** | Required if your policy mandates OTP for issuance | [optional] [default to undefined]
**assertion_type** | **string** | Required when grant_type&#x3D;assertion | [optional] [default to undefined]
**assertion** | **string** | Signed JWT or other accepted assertion | [optional] [default to undefined]
**scopes** | **Array&lt;string&gt;** | Scopes to assign to the long-term token | [optional] [default to undefined]
**ttl_seconds** | **number** | Requested lifetime (1 hour - 90 days). Server may clamp. | [optional] [default to undefined]

## Example

```typescript
import { LongTokenRequest } from './api';

const instance: LongTokenRequest = {
    grant_type,
    client_id,
    client_secret,
    otp_code,
    assertion_type,
    assertion,
    scopes,
    ttl_seconds,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
