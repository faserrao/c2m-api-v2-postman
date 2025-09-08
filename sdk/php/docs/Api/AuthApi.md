# C2MApi\AuthApi

All URIs are relative to https://api.example.com/v1, except if the operation defines another base path.

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**issueLongTermToken()**](AuthApi.md#issueLongTermToken) | **POST** /auth/tokens/long | Issue or rotate a long-term token |
| [**issueShortTermToken()**](AuthApi.md#issueShortTermToken) | **POST** /auth/tokens/short | Issue a short-term access token |
| [**revokeToken()**](AuthApi.md#revokeToken) | **POST** /auth/tokens/{tokenId}/revoke | Revoke a token |


## `issueLongTermToken()`

```php
issueLongTermToken($long_token_request): \C2MApi\Model\LongTokenResponse
```

Issue or rotate a long-term token

Issues a long-term token (e.g., 30-90 days) for automation or server-to-server use. Requires step-up authentication. Choose one of the supported grant types:  - `client_credentials` + `client_secret` - `client_credentials` + one-time `otp_code` - `assertion` (e.g., signed JWT by your private key) - Or an existing short-term token with the `tokens:write` scope  Only one mechanism is required per call.

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure Bearer (JWT) authorization: ShortTokenAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');

// Configure API key authorization: ClientKey
$config = C2MApi\Configuration::getDefaultConfiguration()->setApiKey('X-Client-Id', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = C2MApi\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-Client-Id', 'Bearer');


$apiInstance = new C2MApi\Api\AuthApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$long_token_request = {"grant_type":"client_credentials","client_id":"c2m_abc123","client_secret":"supersecret123","scopes":["jobs:submit","templates:read"],"ttl_seconds":7776000}; // \C2MApi\Model\LongTokenRequest

try {
    $result = $apiInstance->issueLongTermToken($long_token_request);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AuthApi->issueLongTermToken: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **long_token_request** | [**\C2MApi\Model\LongTokenRequest**](../Model/LongTokenRequest.md)|  | |

### Return type

[**\C2MApi\Model\LongTokenResponse**](../Model/LongTokenResponse.md)

### Authorization

[ShortTokenAuth](../../README.md#ShortTokenAuth), [ClientKey](../../README.md#ClientKey)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `issueShortTermToken()`

```php
issueShortTermToken($short_token_request): \C2MApi\Model\ShortTokenResponse
```

Issue a short-term access token

Exchange a valid long-term token for a short-lived JWT (e.g., 15 minutes). The long-term token must be sent in the Authorization header as `Bearer <long_token>`.

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure Bearer (JWT) authorization: LongTokenAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');


$apiInstance = new C2MApi\Api\AuthApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$short_token_request = {"scopes":["jobs:submit","templates:read"]}; // \C2MApi\Model\ShortTokenRequest

try {
    $result = $apiInstance->issueShortTermToken($short_token_request);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AuthApi->issueShortTermToken: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **short_token_request** | [**\C2MApi\Model\ShortTokenRequest**](../Model/ShortTokenRequest.md)|  | [optional] |

### Return type

[**\C2MApi\Model\ShortTokenResponse**](../Model/ShortTokenResponse.md)

### Authorization

[LongTokenAuth](../../README.md#LongTokenAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `revokeToken()`

```php
revokeToken($token_id)
```

Revoke a token

Revokes a short- or long-term token by its `tokenId`. Idempotent.

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure Bearer (JWT) authorization: LongTokenAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');

// Configure Bearer (JWT) authorization: ShortTokenAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');


$apiInstance = new C2MApi\Api\AuthApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$token_id = 'token_id_example'; // string | The token ID to revoke

try {
    $apiInstance->revokeToken($token_id);
} catch (Exception $e) {
    echo 'Exception when calling AuthApi->revokeToken: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **token_id** | **string**| The token ID to revoke | |

### Return type

void (empty response body)

### Authorization

[LongTokenAuth](../../README.md#LongTokenAuth), [ShortTokenAuth](../../README.md#ShortTokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)
