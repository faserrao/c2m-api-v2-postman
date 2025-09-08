# AuthApi

All URIs are relative to *https://api.example.com/v1*

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**issueLongTermToken**](AuthApi.md#issueLongTermToken) | **POST** /auth/tokens/long | Issue or rotate a long-term token |
| [**issueShortTermToken**](AuthApi.md#issueShortTermToken) | **POST** /auth/tokens/short | Issue a short-term access token |
| [**revokeToken**](AuthApi.md#revokeToken) | **POST** /auth/tokens/{tokenId}/revoke | Revoke a token |


<a id="issueLongTermToken"></a>
# **issueLongTermToken**
> LongTokenResponse issueLongTermToken(longTokenRequest)

Issue or rotate a long-term token

Issues a long-term token (e.g., 30-90 days) for automation or server-to-server use. Requires step-up authentication. Choose one of the supported grant types:  - &#x60;client_credentials&#x60; + &#x60;client_secret&#x60; - &#x60;client_credentials&#x60; + one-time &#x60;otp_code&#x60; - &#x60;assertion&#x60; (e.g., signed JWT by your private key) - Or an existing short-term token with the &#x60;tokens:write&#x60; scope  Only one mechanism is required per call. 

### Example
```kotlin
// Import classes:
//import com.c2m.api.infrastructure.*
//import com.c2m.api.models.*

val apiInstance = AuthApi()
val longTokenRequest : LongTokenRequest = {"grant_type":"client_credentials","client_id":"c2m_abc123","client_secret":"supersecret123","scopes":["jobs:submit","templates:read"],"ttl_seconds":7776000} // LongTokenRequest | 
try {
    val result : LongTokenResponse = apiInstance.issueLongTermToken(longTokenRequest)
    println(result)
} catch (e: ClientException) {
    println("4xx response calling AuthApi#issueLongTermToken")
    e.printStackTrace()
} catch (e: ServerException) {
    println("5xx response calling AuthApi#issueLongTermToken")
    e.printStackTrace()
}
```

### Parameters
| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **longTokenRequest** | [**LongTokenRequest**](LongTokenRequest.md)|  | |

### Return type

[**LongTokenResponse**](LongTokenResponse.md)

### Authorization


Configure ShortTokenAuth:
    ApiClient.accessToken = ""
Configure ClientKey:
    ApiClient.apiKey["X-Client-Id"] = ""
    ApiClient.apiKeyPrefix["X-Client-Id"] = ""

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

<a id="issueShortTermToken"></a>
# **issueShortTermToken**
> ShortTokenResponse issueShortTermToken(shortTokenRequest)

Issue a short-term access token

Exchange a valid long-term token for a short-lived JWT (e.g., 15 minutes). The long-term token must be sent in the Authorization header as &#x60;Bearer &lt;long_token&gt;&#x60;. 

### Example
```kotlin
// Import classes:
//import com.c2m.api.infrastructure.*
//import com.c2m.api.models.*

val apiInstance = AuthApi()
val shortTokenRequest : ShortTokenRequest = {"scopes":["jobs:submit","templates:read"]} // ShortTokenRequest | 
try {
    val result : ShortTokenResponse = apiInstance.issueShortTermToken(shortTokenRequest)
    println(result)
} catch (e: ClientException) {
    println("4xx response calling AuthApi#issueShortTermToken")
    e.printStackTrace()
} catch (e: ServerException) {
    println("5xx response calling AuthApi#issueShortTermToken")
    e.printStackTrace()
}
```

### Parameters
| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **shortTokenRequest** | [**ShortTokenRequest**](ShortTokenRequest.md)|  | [optional] |

### Return type

[**ShortTokenResponse**](ShortTokenResponse.md)

### Authorization


Configure LongTokenAuth:
    ApiClient.accessToken = ""

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

<a id="revokeToken"></a>
# **revokeToken**
> revokeToken(tokenId)

Revoke a token

Revokes a short- or long-term token by its &#x60;tokenId&#x60;. Idempotent.

### Example
```kotlin
// Import classes:
//import com.c2m.api.infrastructure.*
//import com.c2m.api.models.*

val apiInstance = AuthApi()
val tokenId : kotlin.String = tokenId_example // kotlin.String | The token ID to revoke
try {
    apiInstance.revokeToken(tokenId)
} catch (e: ClientException) {
    println("4xx response calling AuthApi#revokeToken")
    e.printStackTrace()
} catch (e: ServerException) {
    println("5xx response calling AuthApi#revokeToken")
    e.printStackTrace()
}
```

### Parameters
| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **tokenId** | **kotlin.String**| The token ID to revoke | |

### Return type

null (empty response body)

### Authorization


Configure LongTokenAuth:
    ApiClient.accessToken = ""
Configure ShortTokenAuth:
    ApiClient.accessToken = ""

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

