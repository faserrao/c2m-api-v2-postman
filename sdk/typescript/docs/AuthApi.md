# AuthApi

All URIs are relative to *https://api.example.com/v1*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**issueLongTermToken**](#issuelongtermtoken) | **POST** /auth/tokens/long | Issue or rotate a long-term token|
|[**issueShortTermToken**](#issueshorttermtoken) | **POST** /auth/tokens/short | Issue a short-term access token|
|[**revokeToken**](#revoketoken) | **POST** /auth/tokens/{tokenId}/revoke | Revoke a token|

# **issueLongTermToken**
> LongTokenResponse issueLongTermToken(longTokenRequest)

Issues a long-term token (e.g., 30-90 days) for automation or server-to-server use. Requires step-up authentication. Choose one of the supported grant types:  - `client_credentials` + `client_secret` - `client_credentials` + one-time `otp_code` - `assertion` (e.g., signed JWT by your private key) - Or an existing short-term token with the `tokens:write` scope  Only one mechanism is required per call. 

### Example

```typescript
import {
    AuthApi,
    Configuration,
    LongTokenRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let longTokenRequest: LongTokenRequest; //

const { status, data } = await apiInstance.issueLongTermToken(
    longTokenRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **longTokenRequest** | **LongTokenRequest**|  | |


### Return type

**LongTokenResponse**

### Authorization

[ShortTokenAuth](../README.md#ShortTokenAuth), [ClientKey](../README.md#ClientKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Long-term token issued |  * X-Token-Id - Server-generated identifier for revocation and audit <br>  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**429** | Too Many Requests |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **issueShortTermToken**
> ShortTokenResponse issueShortTermToken()

Exchange a valid long-term token for a short-lived JWT (e.g., 15 minutes). The long-term token must be sent in the Authorization header as `Bearer <long_token>`. 

### Example

```typescript
import {
    AuthApi,
    Configuration,
    ShortTokenRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let shortTokenRequest: ShortTokenRequest; // (optional)

const { status, data } = await apiInstance.issueShortTermToken(
    shortTokenRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **shortTokenRequest** | **ShortTokenRequest**|  | |


### Return type

**ShortTokenResponse**

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Short-term token issued |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**429** | Too Many Requests |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revokeToken**
> revokeToken()

Revokes a short- or long-term token by its `tokenId`. Idempotent.

### Example

```typescript
import {
    AuthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let tokenId: string; //The token ID to revoke (default to undefined)

const { status, data } = await apiInstance.revokeToken(
    tokenId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **tokenId** | [**string**] | The token ID to revoke | defaults to undefined|


### Return type

void (empty response body)

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth), [ShortTokenAuth](../README.md#ShortTokenAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Revoked (idempotent) |  -  |
|**401** | Unauthorized |  -  |
|**404** | Not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

