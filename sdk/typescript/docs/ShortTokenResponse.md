# ShortTokenResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token_type** | **string** |  | [default to undefined]
**access_token** | **string** | Short-lived JWT | [default to undefined]
**expires_in** | **number** | Lifetime in seconds (e.g., 900 for 15 minutes) | [default to undefined]
**expires_at** | **string** | ISO 8601 timestamp of expiration | [default to undefined]
**scopes** | **Array&lt;string&gt;** | Granted scopes | [optional] [default to undefined]
**token_id** | **string** | Server-issued identifier for this token | [optional] [default to undefined]

## Example

```typescript
import { ShortTokenResponse } from './api';

const instance: ShortTokenResponse = {
    token_type,
    access_token,
    expires_in,
    expires_at,
    scopes,
    token_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
