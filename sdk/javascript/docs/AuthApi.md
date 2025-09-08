# C2MApiV2AuthOverlay.AuthApi

All URIs are relative to *https://api.example.com/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**issueLongTermToken**](AuthApi.md#issueLongTermToken) | **POST** /auth/tokens/long | Issue or rotate a long-term token
[**issueShortTermToken**](AuthApi.md#issueShortTermToken) | **POST** /auth/tokens/short | Issue a short-term access token
[**revokeToken**](AuthApi.md#revokeToken) | **POST** /auth/tokens/{tokenId}/revoke | Revoke a token



## issueLongTermToken

> LongTokenResponse issueLongTermToken(longTokenRequest)

Issue or rotate a long-term token

Issues a long-term token (e.g., 30-90 days) for automation or server-to-server use. Requires step-up authentication. Choose one of the supported grant types:  - &#x60;client_credentials&#x60; + &#x60;client_secret&#x60; - &#x60;client_credentials&#x60; + one-time &#x60;otp_code&#x60; - &#x60;assertion&#x60; (e.g., signed JWT by your private key) - Or an existing short-term token with the &#x60;tokens:write&#x60; scope  Only one mechanism is required per call. 

### Example

```javascript
import C2MApiV2AuthOverlay from 'c2_m_api_v2_auth_overlay';
let defaultClient = C2MApiV2AuthOverlay.ApiClient.instance;
// Configure Bearer (JWT) access token for authorization: ShortTokenAuth
let ShortTokenAuth = defaultClient.authentications['ShortTokenAuth'];
ShortTokenAuth.accessToken = "YOUR ACCESS TOKEN"
// Configure API key authorization: ClientKey
let ClientKey = defaultClient.authentications['ClientKey'];
ClientKey.apiKey = 'YOUR API KEY';
// Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
//ClientKey.apiKeyPrefix = 'Token';

let apiInstance = new C2MApiV2AuthOverlay.AuthApi();
let longTokenRequest = {"grant_type":"client_credentials","client_id":"c2m_abc123","client_secret":"supersecret123","scopes":["jobs:submit","templates:read"],"ttl_seconds":7776000}; // LongTokenRequest | 
apiInstance.issueLongTermToken(longTokenRequest, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **longTokenRequest** | [**LongTokenRequest**](LongTokenRequest.md)|  | 

### Return type

[**LongTokenResponse**](LongTokenResponse.md)

### Authorization

[ShortTokenAuth](../README.md#ShortTokenAuth), [ClientKey](../README.md#ClientKey)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## issueShortTermToken

> ShortTokenResponse issueShortTermToken(opts)

Issue a short-term access token

Exchange a valid long-term token for a short-lived JWT (e.g., 15 minutes). The long-term token must be sent in the Authorization header as &#x60;Bearer &lt;long_token&gt;&#x60;. 

### Example

```javascript
import C2MApiV2AuthOverlay from 'c2_m_api_v2_auth_overlay';
let defaultClient = C2MApiV2AuthOverlay.ApiClient.instance;
// Configure Bearer (JWT) access token for authorization: LongTokenAuth
let LongTokenAuth = defaultClient.authentications['LongTokenAuth'];
LongTokenAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new C2MApiV2AuthOverlay.AuthApi();
let opts = {
  'shortTokenRequest': {"scopes":["jobs:submit","templates:read"]} // ShortTokenRequest | 
};
apiInstance.issueShortTermToken(opts, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortTokenRequest** | [**ShortTokenRequest**](ShortTokenRequest.md)|  | [optional] 

### Return type

[**ShortTokenResponse**](ShortTokenResponse.md)

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## revokeToken

> revokeToken(tokenId)

Revoke a token

Revokes a short- or long-term token by its &#x60;tokenId&#x60;. Idempotent.

### Example

```javascript
import C2MApiV2AuthOverlay from 'c2_m_api_v2_auth_overlay';
let defaultClient = C2MApiV2AuthOverlay.ApiClient.instance;
// Configure Bearer (JWT) access token for authorization: LongTokenAuth
let LongTokenAuth = defaultClient.authentications['LongTokenAuth'];
LongTokenAuth.accessToken = "YOUR ACCESS TOKEN"
// Configure Bearer (JWT) access token for authorization: ShortTokenAuth
let ShortTokenAuth = defaultClient.authentications['ShortTokenAuth'];
ShortTokenAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new C2MApiV2AuthOverlay.AuthApi();
let tokenId = "tokenId_example"; // String | The token ID to revoke
apiInstance.revokeToken(tokenId, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully.');
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tokenId** | **String**| The token ID to revoke | 

### Return type

null (empty response body)

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth), [ShortTokenAuth](../README.md#ShortTokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

