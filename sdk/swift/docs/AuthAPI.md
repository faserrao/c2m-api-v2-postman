# AuthAPI

All URIs are relative to *https://api.example.com/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**issueLongTermToken**](AuthAPI.md#issuelongtermtoken) | **POST** /auth/tokens/long | Issue or rotate a long-term token
[**issueShortTermToken**](AuthAPI.md#issueshorttermtoken) | **POST** /auth/tokens/short | Issue a short-term access token
[**revokeToken**](AuthAPI.md#revoketoken) | **POST** /auth/tokens/{tokenId}/revoke | Revoke a token


# **issueLongTermToken**
```swift
    open class func issueLongTermToken(longTokenRequest: LongTokenRequest, completion: @escaping (_ data: LongTokenResponse?, _ error: Error?) -> Void)
```

Issue or rotate a long-term token

Issues a long-term token (e.g., 30-90 days) for automation or server-to-server use. Requires step-up authentication. Choose one of the supported grant types:  - `client_credentials` + `client_secret` - `client_credentials` + one-time `otp_code` - `assertion` (e.g., signed JWT by your private key) - Or an existing short-term token with the `tokens:write` scope  Only one mechanism is required per call. 

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OpenAPIClient

let longTokenRequest = LongTokenRequest(grantType: "grantType_example", clientId: "clientId_example", clientSecret: "clientSecret_example", otpCode: "otpCode_example", assertionType: "assertionType_example", assertion: "assertion_example", scopes: ["scopes_example"], ttlSeconds: 123) // LongTokenRequest | 

// Issue or rotate a long-term token
AuthAPI.issueLongTermToken(longTokenRequest: longTokenRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **longTokenRequest** | [**LongTokenRequest**](LongTokenRequest.md) |  | 

### Return type

[**LongTokenResponse**](LongTokenResponse.md)

### Authorization

[ShortTokenAuth](../README.md#ShortTokenAuth), [ClientKey](../README.md#ClientKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **issueShortTermToken**
```swift
    open class func issueShortTermToken(shortTokenRequest: ShortTokenRequest? = nil, completion: @escaping (_ data: ShortTokenResponse?, _ error: Error?) -> Void)
```

Issue a short-term access token

Exchange a valid long-term token for a short-lived JWT (e.g., 15 minutes). The long-term token must be sent in the Authorization header as `Bearer <long_token>`. 

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OpenAPIClient

let shortTokenRequest = ShortTokenRequest(longToken: "longToken_example", scopes: ["scopes_example"]) // ShortTokenRequest |  (optional)

// Issue a short-term access token
AuthAPI.issueShortTermToken(shortTokenRequest: shortTokenRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortTokenRequest** | [**ShortTokenRequest**](ShortTokenRequest.md) |  | [optional] 

### Return type

[**ShortTokenResponse**](ShortTokenResponse.md)

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revokeToken**
```swift
    open class func revokeToken(tokenId: String, completion: @escaping (_ data: Void?, _ error: Error?) -> Void)
```

Revoke a token

Revokes a short- or long-term token by its `tokenId`. Idempotent.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OpenAPIClient

let tokenId = "tokenId_example" // String | The token ID to revoke

// Revoke a token
AuthAPI.revokeToken(tokenId: tokenId) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tokenId** | **String** | The token ID to revoke | 

### Return type

Void (empty response body)

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth), [ShortTokenAuth](../README.md#ShortTokenAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

