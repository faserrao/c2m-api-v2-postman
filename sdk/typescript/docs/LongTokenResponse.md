# LongTokenResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token_type** | **string** |  | [default to undefined]
**access_token** | **string** | Long-lived token (opaque or JWT depending on deployment) | [default to undefined]
**expires_in** | **number** | Lifetime in seconds | [default to undefined]
**expires_at** | **string** | ISO 8601 timestamp of expiration | [default to undefined]
**scopes** | **Array&lt;string&gt;** | Granted scopes | [optional] [default to undefined]
**token_id** | **string** | Server-issued identifier for this token | [optional] [default to undefined]

## Example

```typescript
import { LongTokenResponse } from './api';

const instance: LongTokenResponse = {
    token_type,
    access_token,
    expires_in,
    expires_at,
    scopes,
    token_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
