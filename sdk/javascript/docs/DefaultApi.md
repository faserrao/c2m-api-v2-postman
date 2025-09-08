# C2MApiV2AuthOverlay.DefaultApi

All URIs are relative to *https://api.example.com/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**mergeMultiDocParams**](DefaultApi.md#mergeMultiDocParams) | **POST** /jobs/multi-doc-merge | Operation for /jobs/multi-doc-merge
[**mergeMultiDocWithTemplateParams**](DefaultApi.md#mergeMultiDocWithTemplateParams) | **POST** /jobs/multi-doc-merge-job-template | Operation for /jobs/multi-doc-merge-job-template
[**multiPdfWithCaptureParams**](DefaultApi.md#multiPdfWithCaptureParams) | **POST** /jobs/multi-pdf-address-capture | Operation for /jobs/multi-pdf-address-capture
[**singleDocJobParams**](DefaultApi.md#singleDocJobParams) | **POST** /jobs/single-doc | Operation for /jobs/single-doc
[**splitPdfParams**](DefaultApi.md#splitPdfParams) | **POST** /jobs/single-pdf-split | Operation for /jobs/single-pdf-split
[**splitPdfWithCaptureParams**](DefaultApi.md#splitPdfWithCaptureParams) | **POST** /jobs/single-pdf-split-addressCapture | Operation for /jobs/single-pdf-split-addressCapture
[**submitMultiDocParams**](DefaultApi.md#submitMultiDocParams) | **POST** /jobs/multi-doc | Operation for /jobs/multi-doc
[**submitMultiDocWithTemplateParams**](DefaultApi.md#submitMultiDocWithTemplateParams) | **POST** /jobs/multi-docs-job-template | Operation for /jobs/multi-docs-job-template
[**submitSingleDocWithTemplateParams**](DefaultApi.md#submitSingleDocWithTemplateParams) | **POST** /jobs/single-doc-job-template | Operation for /jobs/single-doc-job-template



## mergeMultiDocParams

> StandardResponse mergeMultiDocParams(mergeMultiDocParamsRequest)

Operation for /jobs/multi-doc-merge

### Example

```javascript
import C2MApiV2AuthOverlay from 'c2_m_api_v2_auth_overlay';
let defaultClient = C2MApiV2AuthOverlay.ApiClient.instance;
// Configure Bearer (JWT) access token for authorization: bearerAuth
let bearerAuth = defaultClient.authentications['bearerAuth'];
bearerAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new C2MApiV2AuthOverlay.DefaultApi();
let mergeMultiDocParamsRequest = new C2MApiV2AuthOverlay.MergeMultiDocParamsRequest(); // MergeMultiDocParamsRequest | 
apiInstance.mergeMultiDocParams(mergeMultiDocParamsRequest, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mergeMultiDocParamsRequest** | [**MergeMultiDocParamsRequest**](MergeMultiDocParamsRequest.md)|  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## mergeMultiDocWithTemplateParams

> StandardResponse mergeMultiDocWithTemplateParams(mergeMultiDocWithTemplateParamsRequest)

Operation for /jobs/multi-doc-merge-job-template

### Example

```javascript
import C2MApiV2AuthOverlay from 'c2_m_api_v2_auth_overlay';
let defaultClient = C2MApiV2AuthOverlay.ApiClient.instance;
// Configure Bearer (JWT) access token for authorization: bearerAuth
let bearerAuth = defaultClient.authentications['bearerAuth'];
bearerAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new C2MApiV2AuthOverlay.DefaultApi();
let mergeMultiDocWithTemplateParamsRequest = new C2MApiV2AuthOverlay.MergeMultiDocWithTemplateParamsRequest(); // MergeMultiDocWithTemplateParamsRequest | 
apiInstance.mergeMultiDocWithTemplateParams(mergeMultiDocWithTemplateParamsRequest, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mergeMultiDocWithTemplateParamsRequest** | [**MergeMultiDocWithTemplateParamsRequest**](MergeMultiDocWithTemplateParamsRequest.md)|  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## multiPdfWithCaptureParams

> StandardResponse multiPdfWithCaptureParams(multiPdfWithCaptureParamsRequest)

Operation for /jobs/multi-pdf-address-capture

### Example

```javascript
import C2MApiV2AuthOverlay from 'c2_m_api_v2_auth_overlay';
let defaultClient = C2MApiV2AuthOverlay.ApiClient.instance;
// Configure Bearer (JWT) access token for authorization: bearerAuth
let bearerAuth = defaultClient.authentications['bearerAuth'];
bearerAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new C2MApiV2AuthOverlay.DefaultApi();
let multiPdfWithCaptureParamsRequest = new C2MApiV2AuthOverlay.MultiPdfWithCaptureParamsRequest(); // MultiPdfWithCaptureParamsRequest | 
apiInstance.multiPdfWithCaptureParams(multiPdfWithCaptureParamsRequest, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **multiPdfWithCaptureParamsRequest** | [**MultiPdfWithCaptureParamsRequest**](MultiPdfWithCaptureParamsRequest.md)|  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## singleDocJobParams

> StandardResponse singleDocJobParams(singleDocJobParamsRequest)

Operation for /jobs/single-doc

### Example

```javascript
import C2MApiV2AuthOverlay from 'c2_m_api_v2_auth_overlay';
let defaultClient = C2MApiV2AuthOverlay.ApiClient.instance;
// Configure Bearer (JWT) access token for authorization: bearerAuth
let bearerAuth = defaultClient.authentications['bearerAuth'];
bearerAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new C2MApiV2AuthOverlay.DefaultApi();
let singleDocJobParamsRequest = new C2MApiV2AuthOverlay.SingleDocJobParamsRequest(); // SingleDocJobParamsRequest | 
apiInstance.singleDocJobParams(singleDocJobParamsRequest, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **singleDocJobParamsRequest** | [**SingleDocJobParamsRequest**](SingleDocJobParamsRequest.md)|  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## splitPdfParams

> StandardResponse splitPdfParams(splitPdfParamsRequest)

Operation for /jobs/single-pdf-split

### Example

```javascript
import C2MApiV2AuthOverlay from 'c2_m_api_v2_auth_overlay';
let defaultClient = C2MApiV2AuthOverlay.ApiClient.instance;
// Configure Bearer (JWT) access token for authorization: bearerAuth
let bearerAuth = defaultClient.authentications['bearerAuth'];
bearerAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new C2MApiV2AuthOverlay.DefaultApi();
let splitPdfParamsRequest = new C2MApiV2AuthOverlay.SplitPdfParamsRequest(); // SplitPdfParamsRequest | 
apiInstance.splitPdfParams(splitPdfParamsRequest, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **splitPdfParamsRequest** | [**SplitPdfParamsRequest**](SplitPdfParamsRequest.md)|  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## splitPdfWithCaptureParams

> StandardResponse splitPdfWithCaptureParams(splitPdfWithCaptureParamsRequest)

Operation for /jobs/single-pdf-split-addressCapture

### Example

```javascript
import C2MApiV2AuthOverlay from 'c2_m_api_v2_auth_overlay';
let defaultClient = C2MApiV2AuthOverlay.ApiClient.instance;
// Configure Bearer (JWT) access token for authorization: bearerAuth
let bearerAuth = defaultClient.authentications['bearerAuth'];
bearerAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new C2MApiV2AuthOverlay.DefaultApi();
let splitPdfWithCaptureParamsRequest = new C2MApiV2AuthOverlay.SplitPdfWithCaptureParamsRequest(); // SplitPdfWithCaptureParamsRequest | 
apiInstance.splitPdfWithCaptureParams(splitPdfWithCaptureParamsRequest, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **splitPdfWithCaptureParamsRequest** | [**SplitPdfWithCaptureParamsRequest**](SplitPdfWithCaptureParamsRequest.md)|  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## submitMultiDocParams

> StandardResponse submitMultiDocParams(submitMultiDocParamsRequest)

Operation for /jobs/multi-doc

### Example

```javascript
import C2MApiV2AuthOverlay from 'c2_m_api_v2_auth_overlay';
let defaultClient = C2MApiV2AuthOverlay.ApiClient.instance;
// Configure Bearer (JWT) access token for authorization: bearerAuth
let bearerAuth = defaultClient.authentications['bearerAuth'];
bearerAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new C2MApiV2AuthOverlay.DefaultApi();
let submitMultiDocParamsRequest = new C2MApiV2AuthOverlay.SubmitMultiDocParamsRequest(); // SubmitMultiDocParamsRequest | 
apiInstance.submitMultiDocParams(submitMultiDocParamsRequest, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **submitMultiDocParamsRequest** | [**SubmitMultiDocParamsRequest**](SubmitMultiDocParamsRequest.md)|  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## submitMultiDocWithTemplateParams

> StandardResponse submitMultiDocWithTemplateParams(submitMultiDocWithTemplateParamsRequest)

Operation for /jobs/multi-docs-job-template

### Example

```javascript
import C2MApiV2AuthOverlay from 'c2_m_api_v2_auth_overlay';
let defaultClient = C2MApiV2AuthOverlay.ApiClient.instance;
// Configure Bearer (JWT) access token for authorization: bearerAuth
let bearerAuth = defaultClient.authentications['bearerAuth'];
bearerAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new C2MApiV2AuthOverlay.DefaultApi();
let submitMultiDocWithTemplateParamsRequest = new C2MApiV2AuthOverlay.SubmitMultiDocWithTemplateParamsRequest(); // SubmitMultiDocWithTemplateParamsRequest | 
apiInstance.submitMultiDocWithTemplateParams(submitMultiDocWithTemplateParamsRequest, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **submitMultiDocWithTemplateParamsRequest** | [**SubmitMultiDocWithTemplateParamsRequest**](SubmitMultiDocWithTemplateParamsRequest.md)|  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## submitSingleDocWithTemplateParams

> StandardResponse submitSingleDocWithTemplateParams(submitSingleDocWithTemplateParamsRequest)

Operation for /jobs/single-doc-job-template

### Example

```javascript
import C2MApiV2AuthOverlay from 'c2_m_api_v2_auth_overlay';
let defaultClient = C2MApiV2AuthOverlay.ApiClient.instance;
// Configure Bearer (JWT) access token for authorization: bearerAuth
let bearerAuth = defaultClient.authentications['bearerAuth'];
bearerAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new C2MApiV2AuthOverlay.DefaultApi();
let submitSingleDocWithTemplateParamsRequest = new C2MApiV2AuthOverlay.SubmitSingleDocWithTemplateParamsRequest(); // SubmitSingleDocWithTemplateParamsRequest | 
apiInstance.submitSingleDocWithTemplateParams(submitSingleDocWithTemplateParamsRequest, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **submitSingleDocWithTemplateParamsRequest** | [**SubmitSingleDocWithTemplateParamsRequest**](SubmitSingleDocWithTemplateParamsRequest.md)|  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

