# C2M.Api.Api.AuthApi

All URIs are relative to *https://api.example.com/v1*

| Method | HTTP request | Description |
|--------|--------------|-------------|
| [**IssueLongTermToken**](AuthApi.md#issuelongtermtoken) | **POST** /auth/tokens/long | Issue or rotate a long-term token |
| [**IssueShortTermToken**](AuthApi.md#issueshorttermtoken) | **POST** /auth/tokens/short | Issue a short-term access token |
| [**RevokeToken**](AuthApi.md#revoketoken) | **POST** /auth/tokens/{tokenId}/revoke | Revoke a token |

<a id="issuelongtermtoken"></a>
# **IssueLongTermToken**
> LongTokenResponse IssueLongTermToken (LongTokenRequest longTokenRequest)

Issue or rotate a long-term token

Issues a long-term token (e.g., 30-90 days) for automation or server-to-server use. Requires step-up authentication. Choose one of the supported grant types:  - `client_credentials` + `client_secret` - `client_credentials` + one-time `otp_code` - `assertion` (e.g., signed JWT by your private key) - Or an existing short-term token with the `tokens:write` scope  Only one mechanism is required per call. 


### Parameters

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| **longTokenRequest** | [**LongTokenRequest**](LongTokenRequest.md) |  |  |

### Return type

[**LongTokenResponse**](LongTokenResponse.md)

### Authorization

[ShortTokenAuth](../README.md#ShortTokenAuth), [ClientKey](../README.md#ClientKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Long-term token issued |  * X-Token-Id - Server-generated identifier for revocation and audit <br>  |
| **400** | Bad request |  -  |
| **401** | Unauthorized |  -  |
| **403** | Forbidden |  -  |
| **429** | Too Many Requests |  -  |

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

<a id="issueshorttermtoken"></a>
# **IssueShortTermToken**
> ShortTokenResponse IssueShortTermToken (ShortTokenRequest shortTokenRequest = null)

Issue a short-term access token

Exchange a valid long-term token for a short-lived JWT (e.g., 15 minutes). The long-term token must be sent in the Authorization header as `Bearer <long_token>`. 


### Parameters

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| **shortTokenRequest** | [**ShortTokenRequest**](ShortTokenRequest.md) |  | [optional]  |

### Return type

[**ShortTokenResponse**](ShortTokenResponse.md)

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Short-term token issued |  -  |
| **400** | Bad request |  -  |
| **401** | Unauthorized |  -  |
| **429** | Too Many Requests |  -  |

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

<a id="revoketoken"></a>
# **RevokeToken**
> void RevokeToken (string tokenId)

Revoke a token

Revokes a short- or long-term token by its `tokenId`. Idempotent.


### Parameters

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| **tokenId** | **string** | The token ID to revoke |  |

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
| **204** | Revoked (idempotent) |  -  |
| **401** | Unauthorized |  -  |
| **404** | Not found |  -  |

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

