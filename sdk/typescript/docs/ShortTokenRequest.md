# ShortTokenRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**long_token** | **string** | Optional if the long-term token is provided in Authorization header | [optional] [default to undefined]
**scopes** | **Array&lt;string&gt;** | Optional scope narrowing; defaults to the long-term token\&#39;s scopes | [optional] [default to undefined]

## Example

```typescript
import { ShortTokenRequest } from './api';

const instance: ShortTokenRequest = {
    long_token,
    scopes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
