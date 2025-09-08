# \AuthApi

All URIs are relative to *https://api.example.com/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**issue_long_term_token**](AuthApi.md#issue_long_term_token) | **POST** /auth/tokens/long | Issue or rotate a long-term token
[**issue_short_term_token**](AuthApi.md#issue_short_term_token) | **POST** /auth/tokens/short | Issue a short-term access token
[**revoke_token**](AuthApi.md#revoke_token) | **POST** /auth/tokens/{tokenId}/revoke | Revoke a token



## issue_long_term_token

> models::LongTokenResponse issue_long_term_token(long_token_request)
Issue or rotate a long-term token

Issues a long-term token (e.g., 30-90 days) for automation or server-to-server use. Requires step-up authentication. Choose one of the supported grant types:  - `client_credentials` + `client_secret` - `client_credentials` + one-time `otp_code` - `assertion` (e.g., signed JWT by your private key) - Or an existing short-term token with the `tokens:write` scope  Only one mechanism is required per call. 

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**long_token_request** | [**LongTokenRequest**](LongTokenRequest.md) |  | [required] |

### Return type

[**models::LongTokenResponse**](LongTokenResponse.md)

### Authorization

[ShortTokenAuth](../README.md#ShortTokenAuth), [ClientKey](../README.md#ClientKey)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## issue_short_term_token

> models::ShortTokenResponse issue_short_term_token(short_token_request)
Issue a short-term access token

Exchange a valid long-term token for a short-lived JWT (e.g., 15 minutes). The long-term token must be sent in the Authorization header as `Bearer <long_token>`. 

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**short_token_request** | Option<[**ShortTokenRequest**](ShortTokenRequest.md)> |  |  |

### Return type

[**models::ShortTokenResponse**](ShortTokenResponse.md)

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## revoke_token

> revoke_token(token_id)
Revoke a token

Revokes a short- or long-term token by its `tokenId`. Idempotent.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**token_id** | **String** | The token ID to revoke | [required] |

### Return type

 (empty response body)

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth), [ShortTokenAuth](../README.md#ShortTokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

