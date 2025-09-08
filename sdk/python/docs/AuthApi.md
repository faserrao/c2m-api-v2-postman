# c2m_api.AuthApi

All URIs are relative to *https://api.example.com/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**issue_long_term_token**](AuthApi.md#issue_long_term_token) | **POST** /auth/tokens/long | Issue or rotate a long-term token
[**issue_short_term_token**](AuthApi.md#issue_short_term_token) | **POST** /auth/tokens/short | Issue a short-term access token
[**revoke_token**](AuthApi.md#revoke_token) | **POST** /auth/tokens/{tokenId}/revoke | Revoke a token


# **issue_long_term_token**
> LongTokenResponse issue_long_term_token(long_token_request)

Issue or rotate a long-term token

Issues a long-term token (e.g., 30-90 days) for automation or server-to-server use.
Requires step-up authentication. Choose one of the supported grant types:

- `client_credentials` + `client_secret`
- `client_credentials` + one-time `otp_code`
- `assertion` (e.g., signed JWT by your private key)
- Or an existing short-term token with the `tokens:write` scope

Only one mechanism is required per call.


### Example

* Bearer (JWT) Authentication (ShortTokenAuth):
* Api Key Authentication (ClientKey):

```python
import c2m_api
from c2m_api.models.long_token_request import LongTokenRequest
from c2m_api.models.long_token_response import LongTokenResponse
from c2m_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.example.com/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = c2m_api.Configuration(
    host = "https://api.example.com/v1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): ShortTokenAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Configure API key authorization: ClientKey
configuration.api_key['ClientKey'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ClientKey'] = 'Bearer'

# Enter a context with an instance of the API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = c2m_api.AuthApi(api_client)
    long_token_request = {"grant_type":"client_credentials","client_id":"c2m_abc123","client_secret":"supersecret123","scopes":["jobs:submit","templates:read"],"ttl_seconds":7776000} # LongTokenRequest | 

    try:
        # Issue or rotate a long-term token
        api_response = api_instance.issue_long_term_token(long_token_request)
        print("The response of AuthApi->issue_long_term_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthApi->issue_long_term_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **long_token_request** | [**LongTokenRequest**](LongTokenRequest.md)|  | 

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
**201** | Long-term token issued |  * X-Token-Id - Server-generated identifier for revocation and audit <br>  |
**400** | Bad request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**429** | Too Many Requests |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **issue_short_term_token**
> ShortTokenResponse issue_short_term_token(short_token_request=short_token_request)

Issue a short-term access token

Exchange a valid long-term token for a short-lived JWT (e.g., 15 minutes).
The long-term token must be sent in the Authorization header as `Bearer <long_token>`.


### Example

* Bearer (JWT) Authentication (LongTokenAuth):

```python
import c2m_api
from c2m_api.models.short_token_request import ShortTokenRequest
from c2m_api.models.short_token_response import ShortTokenResponse
from c2m_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.example.com/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = c2m_api.Configuration(
    host = "https://api.example.com/v1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): LongTokenAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = c2m_api.AuthApi(api_client)
    short_token_request = {"scopes":["jobs:submit","templates:read"]} # ShortTokenRequest |  (optional)

    try:
        # Issue a short-term access token
        api_response = api_instance.issue_short_term_token(short_token_request=short_token_request)
        print("The response of AuthApi->issue_short_term_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthApi->issue_short_term_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **short_token_request** | [**ShortTokenRequest**](ShortTokenRequest.md)|  | [optional] 

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
**201** | Short-term token issued |  -  |
**400** | Bad request |  -  |
**401** | Unauthorized |  -  |
**429** | Too Many Requests |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revoke_token**
> revoke_token(token_id)

Revoke a token

Revokes a short- or long-term token by its `tokenId`. Idempotent.

### Example

* Bearer (JWT) Authentication (LongTokenAuth):
* Bearer (JWT) Authentication (ShortTokenAuth):

```python
import c2m_api
from c2m_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.example.com/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = c2m_api.Configuration(
    host = "https://api.example.com/v1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): LongTokenAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Configure Bearer authorization (JWT): ShortTokenAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = c2m_api.AuthApi(api_client)
    token_id = 'token_id_example' # str | The token ID to revoke

    try:
        # Revoke a token
        api_instance.revoke_token(token_id)
    except Exception as e:
        print("Exception when calling AuthApi->revoke_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token_id** | **str**| The token ID to revoke | 

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
**204** | Revoked (idempotent) |  -  |
**401** | Unauthorized |  -  |
**404** | Not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

