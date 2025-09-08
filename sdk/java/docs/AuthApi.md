# AuthApi

All URIs are relative to *https://api.example.com/v1*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**issueLongTermToken**](AuthApi.md#issueLongTermToken) | **POST** /auth/tokens/long | Issue or rotate a long-term token |
| [**issueShortTermToken**](AuthApi.md#issueShortTermToken) | **POST** /auth/tokens/short | Issue a short-term access token |
| [**revokeToken**](AuthApi.md#revokeToken) | **POST** /auth/tokens/{tokenId}/revoke | Revoke a token |


<a id="issueLongTermToken"></a>
# **issueLongTermToken**
> LongTokenResponse issueLongTermToken(longTokenRequest)

Issue or rotate a long-term token

Issues a long-term token (e.g., 30-90 days) for automation or server-to-server use. Requires step-up authentication. Choose one of the supported grant types:  - &#x60;client_credentials&#x60; + &#x60;client_secret&#x60; - &#x60;client_credentials&#x60; + one-time &#x60;otp_code&#x60; - &#x60;assertion&#x60; (e.g., signed JWT by your private key) - Or an existing short-term token with the &#x60;tokens:write&#x60; scope  Only one mechanism is required per call. 

### Example
```java
// Import classes:
import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.models.*;
import com.c2m.api.AuthApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("https://api.example.com/v1");
    
    // Configure HTTP bearer authorization: ShortTokenAuth
    HttpBearerAuth ShortTokenAuth = (HttpBearerAuth) defaultClient.getAuthentication("ShortTokenAuth");
    ShortTokenAuth.setBearerToken("BEARER TOKEN");

    // Configure API key authorization: ClientKey
    ApiKeyAuth ClientKey = (ApiKeyAuth) defaultClient.getAuthentication("ClientKey");
    ClientKey.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //ClientKey.setApiKeyPrefix("Token");

    AuthApi apiInstance = new AuthApi(defaultClient);
    LongTokenRequest longTokenRequest = new LongTokenRequest(); // LongTokenRequest | 
    try {
      LongTokenResponse result = apiInstance.issueLongTermToken(longTokenRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AuthApi#issueLongTermToken");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **longTokenRequest** | [**LongTokenRequest**](LongTokenRequest.md)|  | |

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

<a id="issueShortTermToken"></a>
# **issueShortTermToken**
> ShortTokenResponse issueShortTermToken(shortTokenRequest)

Issue a short-term access token

Exchange a valid long-term token for a short-lived JWT (e.g., 15 minutes). The long-term token must be sent in the Authorization header as &#x60;Bearer &lt;long_token&gt;&#x60;. 

### Example
```java
// Import classes:
import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.models.*;
import com.c2m.api.AuthApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("https://api.example.com/v1");
    
    // Configure HTTP bearer authorization: LongTokenAuth
    HttpBearerAuth LongTokenAuth = (HttpBearerAuth) defaultClient.getAuthentication("LongTokenAuth");
    LongTokenAuth.setBearerToken("BEARER TOKEN");

    AuthApi apiInstance = new AuthApi(defaultClient);
    ShortTokenRequest shortTokenRequest = new ShortTokenRequest(); // ShortTokenRequest | 
    try {
      ShortTokenResponse result = apiInstance.issueShortTermToken(shortTokenRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AuthApi#issueShortTermToken");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **shortTokenRequest** | [**ShortTokenRequest**](ShortTokenRequest.md)|  | [optional] |

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

<a id="revokeToken"></a>
# **revokeToken**
> revokeToken(tokenId)

Revoke a token

Revokes a short- or long-term token by its &#x60;tokenId&#x60;. Idempotent.

### Example
```java
// Import classes:
import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.models.*;
import com.c2m.api.AuthApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("https://api.example.com/v1");
    
    // Configure HTTP bearer authorization: LongTokenAuth
    HttpBearerAuth LongTokenAuth = (HttpBearerAuth) defaultClient.getAuthentication("LongTokenAuth");
    LongTokenAuth.setBearerToken("BEARER TOKEN");

    // Configure HTTP bearer authorization: ShortTokenAuth
    HttpBearerAuth ShortTokenAuth = (HttpBearerAuth) defaultClient.getAuthentication("ShortTokenAuth");
    ShortTokenAuth.setBearerToken("BEARER TOKEN");

    AuthApi apiInstance = new AuthApi(defaultClient);
    String tokenId = "tokenId_example"; // String | The token ID to revoke
    try {
      apiInstance.revokeToken(tokenId);
    } catch (ApiException e) {
      System.err.println("Exception when calling AuthApi#revokeToken");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **tokenId** | **String**| The token ID to revoke | |

### Return type

null (empty response body)

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

