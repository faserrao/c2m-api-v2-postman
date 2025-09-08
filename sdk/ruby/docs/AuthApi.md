# OpenapiClient::AuthApi

All URIs are relative to *https://api.example.com/v1*

| Method | HTTP request | Description |
| ------ | ------------ | ----------- |
| [**issue_long_term_token**](AuthApi.md#issue_long_term_token) | **POST** /auth/tokens/long | Issue or rotate a long-term token |
| [**issue_short_term_token**](AuthApi.md#issue_short_term_token) | **POST** /auth/tokens/short | Issue a short-term access token |
| [**revoke_token**](AuthApi.md#revoke_token) | **POST** /auth/tokens/{tokenId}/revoke | Revoke a token |


## issue_long_term_token

> <LongTokenResponse> issue_long_term_token(long_token_request)

Issue or rotate a long-term token

Issues a long-term token (e.g., 30-90 days) for automation or server-to-server use. Requires step-up authentication. Choose one of the supported grant types:  - `client_credentials` + `client_secret` - `client_credentials` + one-time `otp_code` - `assertion` (e.g., signed JWT by your private key) - Or an existing short-term token with the `tokens:write` scope  Only one mechanism is required per call. 

### Examples

```ruby
require 'time'
require 'openapi_client'
# setup authorization
OpenapiClient.configure do |config|
  # Configure Bearer authorization (JWT): ShortTokenAuth
  config.access_token = 'YOUR_BEARER_TOKEN'

  # Configure API key authorization: ClientKey
  config.api_key['X-Client-Id'] = 'YOUR API KEY'
  # Uncomment the following line to set a prefix for the API key, e.g. 'Bearer' (defaults to nil)
  # config.api_key_prefix['X-Client-Id'] = 'Bearer'
end

api_instance = OpenapiClient::AuthApi.new
long_token_request = OpenapiClient::LongTokenRequest.new({grant_type: 'client_credentials', client_id: 'client_id_example'}) # LongTokenRequest | 

begin
  # Issue or rotate a long-term token
  result = api_instance.issue_long_term_token(long_token_request)
  p result
rescue OpenapiClient::ApiError => e
  puts "Error when calling AuthApi->issue_long_term_token: #{e}"
end
```

#### Using the issue_long_term_token_with_http_info variant

This returns an Array which contains the response data, status code and headers.

> <Array(<LongTokenResponse>, Integer, Hash)> issue_long_term_token_with_http_info(long_token_request)

```ruby
begin
  # Issue or rotate a long-term token
  data, status_code, headers = api_instance.issue_long_term_token_with_http_info(long_token_request)
  p status_code # => 2xx
  p headers # => { ... }
  p data # => <LongTokenResponse>
rescue OpenapiClient::ApiError => e
  puts "Error when calling AuthApi->issue_long_term_token_with_http_info: #{e}"
end
```

### Parameters

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **long_token_request** | [**LongTokenRequest**](LongTokenRequest.md) |  |  |

### Return type

[**LongTokenResponse**](LongTokenResponse.md)

### Authorization

[ShortTokenAuth](../README.md#ShortTokenAuth), [ClientKey](../README.md#ClientKey)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## issue_short_term_token

> <ShortTokenResponse> issue_short_term_token(opts)

Issue a short-term access token

Exchange a valid long-term token for a short-lived JWT (e.g., 15 minutes). The long-term token must be sent in the Authorization header as `Bearer <long_token>`. 

### Examples

```ruby
require 'time'
require 'openapi_client'
# setup authorization
OpenapiClient.configure do |config|
  # Configure Bearer authorization (JWT): LongTokenAuth
  config.access_token = 'YOUR_BEARER_TOKEN'
end

api_instance = OpenapiClient::AuthApi.new
opts = {
  short_token_request: OpenapiClient::ShortTokenRequest.new # ShortTokenRequest | 
}

begin
  # Issue a short-term access token
  result = api_instance.issue_short_term_token(opts)
  p result
rescue OpenapiClient::ApiError => e
  puts "Error when calling AuthApi->issue_short_term_token: #{e}"
end
```

#### Using the issue_short_term_token_with_http_info variant

This returns an Array which contains the response data, status code and headers.

> <Array(<ShortTokenResponse>, Integer, Hash)> issue_short_term_token_with_http_info(opts)

```ruby
begin
  # Issue a short-term access token
  data, status_code, headers = api_instance.issue_short_term_token_with_http_info(opts)
  p status_code # => 2xx
  p headers # => { ... }
  p data # => <ShortTokenResponse>
rescue OpenapiClient::ApiError => e
  puts "Error when calling AuthApi->issue_short_term_token_with_http_info: #{e}"
end
```

### Parameters

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **short_token_request** | [**ShortTokenRequest**](ShortTokenRequest.md) |  | [optional] |

### Return type

[**ShortTokenResponse**](ShortTokenResponse.md)

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## revoke_token

> revoke_token(token_id)

Revoke a token

Revokes a short- or long-term token by its `tokenId`. Idempotent.

### Examples

```ruby
require 'time'
require 'openapi_client'
# setup authorization
OpenapiClient.configure do |config|
  # Configure Bearer authorization (JWT): LongTokenAuth
  config.access_token = 'YOUR_BEARER_TOKEN'

  # Configure Bearer authorization (JWT): ShortTokenAuth
  config.access_token = 'YOUR_BEARER_TOKEN'
end

api_instance = OpenapiClient::AuthApi.new
token_id = 'token_id_example' # String | The token ID to revoke

begin
  # Revoke a token
  api_instance.revoke_token(token_id)
rescue OpenapiClient::ApiError => e
  puts "Error when calling AuthApi->revoke_token: #{e}"
end
```

#### Using the revoke_token_with_http_info variant

This returns an Array which contains the response data (`nil` in this case), status code and headers.

> <Array(nil, Integer, Hash)> revoke_token_with_http_info(token_id)

```ruby
begin
  # Revoke a token
  data, status_code, headers = api_instance.revoke_token_with_http_info(token_id)
  p status_code # => 2xx
  p headers # => { ... }
  p data # => nil
rescue OpenapiClient::ApiError => e
  puts "Error when calling AuthApi->revoke_token_with_http_info: #{e}"
end
```

### Parameters

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **token_id** | **String** | The token ID to revoke |  |

### Return type

nil (empty response body)

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth), [ShortTokenAuth](../README.md#ShortTokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

