# C2M.Api.Api.DefaultApi

All URIs are relative to *https://api.example.com/v1*

| Method | HTTP request | Description |
|--------|--------------|-------------|
| [**MergeMultiDocParams**](DefaultApi.md#mergemultidocparams) | **POST** /jobs/multi-doc-merge | Operation for /jobs/multi-doc-merge |
| [**MergeMultiDocWithTemplateParams**](DefaultApi.md#mergemultidocwithtemplateparams) | **POST** /jobs/multi-doc-merge-job-template | Operation for /jobs/multi-doc-merge-job-template |
| [**MultiPdfWithCaptureParams**](DefaultApi.md#multipdfwithcaptureparams) | **POST** /jobs/multi-pdf-address-capture | Operation for /jobs/multi-pdf-address-capture |
| [**SingleDocJobParams**](DefaultApi.md#singledocjobparams) | **POST** /jobs/single-doc | Operation for /jobs/single-doc |
| [**SplitPdfParams**](DefaultApi.md#splitpdfparams) | **POST** /jobs/single-pdf-split | Operation for /jobs/single-pdf-split |
| [**SplitPdfWithCaptureParams**](DefaultApi.md#splitpdfwithcaptureparams) | **POST** /jobs/single-pdf-split-addressCapture | Operation for /jobs/single-pdf-split-addressCapture |
| [**SubmitMultiDocParams**](DefaultApi.md#submitmultidocparams) | **POST** /jobs/multi-doc | Operation for /jobs/multi-doc |
| [**SubmitMultiDocWithTemplateParams**](DefaultApi.md#submitmultidocwithtemplateparams) | **POST** /jobs/multi-docs-job-template | Operation for /jobs/multi-docs-job-template |
| [**SubmitSingleDocWithTemplateParams**](DefaultApi.md#submitsingledocwithtemplateparams) | **POST** /jobs/single-doc-job-template | Operation for /jobs/single-doc-job-template |

<a id="mergemultidocparams"></a>
# **MergeMultiDocParams**
> StandardResponse MergeMultiDocParams (MergeMultiDocParamsRequest mergeMultiDocParamsRequest)

Operation for /jobs/multi-doc-merge


### Parameters

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| **mergeMultiDocParamsRequest** | [**MergeMultiDocParamsRequest**](MergeMultiDocParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Success |  -  |
| **400** | Invalid request |  -  |
| **401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

<a id="mergemultidocwithtemplateparams"></a>
# **MergeMultiDocWithTemplateParams**
> StandardResponse MergeMultiDocWithTemplateParams (MergeMultiDocWithTemplateParamsRequest mergeMultiDocWithTemplateParamsRequest)

Operation for /jobs/multi-doc-merge-job-template


### Parameters

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| **mergeMultiDocWithTemplateParamsRequest** | [**MergeMultiDocWithTemplateParamsRequest**](MergeMultiDocWithTemplateParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Success |  -  |
| **400** | Invalid request |  -  |
| **401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

<a id="multipdfwithcaptureparams"></a>
# **MultiPdfWithCaptureParams**
> StandardResponse MultiPdfWithCaptureParams (MultiPdfWithCaptureParamsRequest multiPdfWithCaptureParamsRequest)

Operation for /jobs/multi-pdf-address-capture


### Parameters

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| **multiPdfWithCaptureParamsRequest** | [**MultiPdfWithCaptureParamsRequest**](MultiPdfWithCaptureParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Success |  -  |
| **400** | Invalid request |  -  |
| **401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

<a id="singledocjobparams"></a>
# **SingleDocJobParams**
> StandardResponse SingleDocJobParams (SingleDocJobParamsRequest singleDocJobParamsRequest)

Operation for /jobs/single-doc


### Parameters

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| **singleDocJobParamsRequest** | [**SingleDocJobParamsRequest**](SingleDocJobParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Success |  -  |
| **400** | Invalid request |  -  |
| **401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

<a id="splitpdfparams"></a>
# **SplitPdfParams**
> StandardResponse SplitPdfParams (SplitPdfParamsRequest splitPdfParamsRequest)

Operation for /jobs/single-pdf-split


### Parameters

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| **splitPdfParamsRequest** | [**SplitPdfParamsRequest**](SplitPdfParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Success |  -  |
| **400** | Invalid request |  -  |
| **401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

<a id="splitpdfwithcaptureparams"></a>
# **SplitPdfWithCaptureParams**
> StandardResponse SplitPdfWithCaptureParams (SplitPdfWithCaptureParamsRequest splitPdfWithCaptureParamsRequest)

Operation for /jobs/single-pdf-split-addressCapture


### Parameters

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| **splitPdfWithCaptureParamsRequest** | [**SplitPdfWithCaptureParamsRequest**](SplitPdfWithCaptureParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Success |  -  |
| **400** | Invalid request |  -  |
| **401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

<a id="submitmultidocparams"></a>
# **SubmitMultiDocParams**
> StandardResponse SubmitMultiDocParams (SubmitMultiDocParamsRequest submitMultiDocParamsRequest)

Operation for /jobs/multi-doc


### Parameters

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| **submitMultiDocParamsRequest** | [**SubmitMultiDocParamsRequest**](SubmitMultiDocParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Success |  -  |
| **400** | Invalid request |  -  |
| **401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

<a id="submitmultidocwithtemplateparams"></a>
# **SubmitMultiDocWithTemplateParams**
> StandardResponse SubmitMultiDocWithTemplateParams (SubmitMultiDocWithTemplateParamsRequest submitMultiDocWithTemplateParamsRequest)

Operation for /jobs/multi-docs-job-template


### Parameters

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| **submitMultiDocWithTemplateParamsRequest** | [**SubmitMultiDocWithTemplateParamsRequest**](SubmitMultiDocWithTemplateParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Success |  -  |
| **400** | Invalid request |  -  |
| **401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

<a id="submitsingledocwithtemplateparams"></a>
# **SubmitSingleDocWithTemplateParams**
> StandardResponse SubmitSingleDocWithTemplateParams (SubmitSingleDocWithTemplateParamsRequest submitSingleDocWithTemplateParamsRequest)

Operation for /jobs/single-doc-job-template


### Parameters

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| **submitSingleDocWithTemplateParamsRequest** | [**SubmitSingleDocWithTemplateParamsRequest**](SubmitSingleDocWithTemplateParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Success |  -  |
| **400** | Invalid request |  -  |
| **401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

