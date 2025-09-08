# C2MApi\DefaultApi

All URIs are relative to https://api.example.com/v1, except if the operation defines another base path.

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**mergeMultiDocParams()**](DefaultApi.md#mergeMultiDocParams) | **POST** /jobs/multi-doc-merge | Operation for /jobs/multi-doc-merge |
| [**mergeMultiDocWithTemplateParams()**](DefaultApi.md#mergeMultiDocWithTemplateParams) | **POST** /jobs/multi-doc-merge-job-template | Operation for /jobs/multi-doc-merge-job-template |
| [**multiPdfWithCaptureParams()**](DefaultApi.md#multiPdfWithCaptureParams) | **POST** /jobs/multi-pdf-address-capture | Operation for /jobs/multi-pdf-address-capture |
| [**singleDocJobParams()**](DefaultApi.md#singleDocJobParams) | **POST** /jobs/single-doc | Operation for /jobs/single-doc |
| [**splitPdfParams()**](DefaultApi.md#splitPdfParams) | **POST** /jobs/single-pdf-split | Operation for /jobs/single-pdf-split |
| [**splitPdfWithCaptureParams()**](DefaultApi.md#splitPdfWithCaptureParams) | **POST** /jobs/single-pdf-split-addressCapture | Operation for /jobs/single-pdf-split-addressCapture |
| [**submitMultiDocParams()**](DefaultApi.md#submitMultiDocParams) | **POST** /jobs/multi-doc | Operation for /jobs/multi-doc |
| [**submitMultiDocWithTemplateParams()**](DefaultApi.md#submitMultiDocWithTemplateParams) | **POST** /jobs/multi-docs-job-template | Operation for /jobs/multi-docs-job-template |
| [**submitSingleDocWithTemplateParams()**](DefaultApi.md#submitSingleDocWithTemplateParams) | **POST** /jobs/single-doc-job-template | Operation for /jobs/single-doc-job-template |


## `mergeMultiDocParams()`

```php
mergeMultiDocParams($merge_multi_doc_params_request): \C2MApi\Model\StandardResponse
```

Operation for /jobs/multi-doc-merge

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure Bearer (JWT) authorization: bearerAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');


$apiInstance = new C2MApi\Api\DefaultApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$merge_multi_doc_params_request = new \C2MApi\Model\MergeMultiDocParamsRequest(); // \C2MApi\Model\MergeMultiDocParamsRequest

try {
    $result = $apiInstance->mergeMultiDocParams($merge_multi_doc_params_request);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling DefaultApi->mergeMultiDocParams: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **merge_multi_doc_params_request** | [**\C2MApi\Model\MergeMultiDocParamsRequest**](../Model/MergeMultiDocParamsRequest.md)|  | |

### Return type

[**\C2MApi\Model\StandardResponse**](../Model/StandardResponse.md)

### Authorization

[bearerAuth](../../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `mergeMultiDocWithTemplateParams()`

```php
mergeMultiDocWithTemplateParams($merge_multi_doc_with_template_params_request): \C2MApi\Model\StandardResponse
```

Operation for /jobs/multi-doc-merge-job-template

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure Bearer (JWT) authorization: bearerAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');


$apiInstance = new C2MApi\Api\DefaultApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$merge_multi_doc_with_template_params_request = new \C2MApi\Model\MergeMultiDocWithTemplateParamsRequest(); // \C2MApi\Model\MergeMultiDocWithTemplateParamsRequest

try {
    $result = $apiInstance->mergeMultiDocWithTemplateParams($merge_multi_doc_with_template_params_request);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling DefaultApi->mergeMultiDocWithTemplateParams: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **merge_multi_doc_with_template_params_request** | [**\C2MApi\Model\MergeMultiDocWithTemplateParamsRequest**](../Model/MergeMultiDocWithTemplateParamsRequest.md)|  | |

### Return type

[**\C2MApi\Model\StandardResponse**](../Model/StandardResponse.md)

### Authorization

[bearerAuth](../../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `multiPdfWithCaptureParams()`

```php
multiPdfWithCaptureParams($multi_pdf_with_capture_params_request): \C2MApi\Model\StandardResponse
```

Operation for /jobs/multi-pdf-address-capture

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure Bearer (JWT) authorization: bearerAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');


$apiInstance = new C2MApi\Api\DefaultApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$multi_pdf_with_capture_params_request = new \C2MApi\Model\MultiPdfWithCaptureParamsRequest(); // \C2MApi\Model\MultiPdfWithCaptureParamsRequest

try {
    $result = $apiInstance->multiPdfWithCaptureParams($multi_pdf_with_capture_params_request);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling DefaultApi->multiPdfWithCaptureParams: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **multi_pdf_with_capture_params_request** | [**\C2MApi\Model\MultiPdfWithCaptureParamsRequest**](../Model/MultiPdfWithCaptureParamsRequest.md)|  | |

### Return type

[**\C2MApi\Model\StandardResponse**](../Model/StandardResponse.md)

### Authorization

[bearerAuth](../../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `singleDocJobParams()`

```php
singleDocJobParams($single_doc_job_params_request): \C2MApi\Model\StandardResponse
```

Operation for /jobs/single-doc

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure Bearer (JWT) authorization: bearerAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');


$apiInstance = new C2MApi\Api\DefaultApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$single_doc_job_params_request = new \C2MApi\Model\SingleDocJobParamsRequest(); // \C2MApi\Model\SingleDocJobParamsRequest

try {
    $result = $apiInstance->singleDocJobParams($single_doc_job_params_request);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling DefaultApi->singleDocJobParams: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **single_doc_job_params_request** | [**\C2MApi\Model\SingleDocJobParamsRequest**](../Model/SingleDocJobParamsRequest.md)|  | |

### Return type

[**\C2MApi\Model\StandardResponse**](../Model/StandardResponse.md)

### Authorization

[bearerAuth](../../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `splitPdfParams()`

```php
splitPdfParams($split_pdf_params_request): \C2MApi\Model\StandardResponse
```

Operation for /jobs/single-pdf-split

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure Bearer (JWT) authorization: bearerAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');


$apiInstance = new C2MApi\Api\DefaultApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$split_pdf_params_request = new \C2MApi\Model\SplitPdfParamsRequest(); // \C2MApi\Model\SplitPdfParamsRequest

try {
    $result = $apiInstance->splitPdfParams($split_pdf_params_request);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling DefaultApi->splitPdfParams: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **split_pdf_params_request** | [**\C2MApi\Model\SplitPdfParamsRequest**](../Model/SplitPdfParamsRequest.md)|  | |

### Return type

[**\C2MApi\Model\StandardResponse**](../Model/StandardResponse.md)

### Authorization

[bearerAuth](../../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `splitPdfWithCaptureParams()`

```php
splitPdfWithCaptureParams($split_pdf_with_capture_params_request): \C2MApi\Model\StandardResponse
```

Operation for /jobs/single-pdf-split-addressCapture

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure Bearer (JWT) authorization: bearerAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');


$apiInstance = new C2MApi\Api\DefaultApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$split_pdf_with_capture_params_request = new \C2MApi\Model\SplitPdfWithCaptureParamsRequest(); // \C2MApi\Model\SplitPdfWithCaptureParamsRequest

try {
    $result = $apiInstance->splitPdfWithCaptureParams($split_pdf_with_capture_params_request);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling DefaultApi->splitPdfWithCaptureParams: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **split_pdf_with_capture_params_request** | [**\C2MApi\Model\SplitPdfWithCaptureParamsRequest**](../Model/SplitPdfWithCaptureParamsRequest.md)|  | |

### Return type

[**\C2MApi\Model\StandardResponse**](../Model/StandardResponse.md)

### Authorization

[bearerAuth](../../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `submitMultiDocParams()`

```php
submitMultiDocParams($submit_multi_doc_params_request): \C2MApi\Model\StandardResponse
```

Operation for /jobs/multi-doc

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure Bearer (JWT) authorization: bearerAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');


$apiInstance = new C2MApi\Api\DefaultApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$submit_multi_doc_params_request = new \C2MApi\Model\SubmitMultiDocParamsRequest(); // \C2MApi\Model\SubmitMultiDocParamsRequest

try {
    $result = $apiInstance->submitMultiDocParams($submit_multi_doc_params_request);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling DefaultApi->submitMultiDocParams: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **submit_multi_doc_params_request** | [**\C2MApi\Model\SubmitMultiDocParamsRequest**](../Model/SubmitMultiDocParamsRequest.md)|  | |

### Return type

[**\C2MApi\Model\StandardResponse**](../Model/StandardResponse.md)

### Authorization

[bearerAuth](../../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `submitMultiDocWithTemplateParams()`

```php
submitMultiDocWithTemplateParams($submit_multi_doc_with_template_params_request): \C2MApi\Model\StandardResponse
```

Operation for /jobs/multi-docs-job-template

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure Bearer (JWT) authorization: bearerAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');


$apiInstance = new C2MApi\Api\DefaultApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$submit_multi_doc_with_template_params_request = new \C2MApi\Model\SubmitMultiDocWithTemplateParamsRequest(); // \C2MApi\Model\SubmitMultiDocWithTemplateParamsRequest

try {
    $result = $apiInstance->submitMultiDocWithTemplateParams($submit_multi_doc_with_template_params_request);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling DefaultApi->submitMultiDocWithTemplateParams: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **submit_multi_doc_with_template_params_request** | [**\C2MApi\Model\SubmitMultiDocWithTemplateParamsRequest**](../Model/SubmitMultiDocWithTemplateParamsRequest.md)|  | |

### Return type

[**\C2MApi\Model\StandardResponse**](../Model/StandardResponse.md)

### Authorization

[bearerAuth](../../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `submitSingleDocWithTemplateParams()`

```php
submitSingleDocWithTemplateParams($submit_single_doc_with_template_params_request): \C2MApi\Model\StandardResponse
```

Operation for /jobs/single-doc-job-template

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure Bearer (JWT) authorization: bearerAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');


$apiInstance = new C2MApi\Api\DefaultApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$submit_single_doc_with_template_params_request = new \C2MApi\Model\SubmitSingleDocWithTemplateParamsRequest(); // \C2MApi\Model\SubmitSingleDocWithTemplateParamsRequest

try {
    $result = $apiInstance->submitSingleDocWithTemplateParams($submit_single_doc_with_template_params_request);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling DefaultApi->submitSingleDocWithTemplateParams: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **submit_single_doc_with_template_params_request** | [**\C2MApi\Model\SubmitSingleDocWithTemplateParamsRequest**](../Model/SubmitSingleDocWithTemplateParamsRequest.md)|  | |

### Return type

[**\C2MApi\Model\StandardResponse**](../Model/StandardResponse.md)

### Authorization

[bearerAuth](../../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)
