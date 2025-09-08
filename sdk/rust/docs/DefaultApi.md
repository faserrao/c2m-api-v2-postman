# \DefaultApi

All URIs are relative to *https://api.example.com/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**merge_multi_doc_params**](DefaultApi.md#merge_multi_doc_params) | **POST** /jobs/multi-doc-merge | Operation for /jobs/multi-doc-merge
[**merge_multi_doc_with_template_params**](DefaultApi.md#merge_multi_doc_with_template_params) | **POST** /jobs/multi-doc-merge-job-template | Operation for /jobs/multi-doc-merge-job-template
[**multi_pdf_with_capture_params**](DefaultApi.md#multi_pdf_with_capture_params) | **POST** /jobs/multi-pdf-address-capture | Operation for /jobs/multi-pdf-address-capture
[**single_doc_job_params**](DefaultApi.md#single_doc_job_params) | **POST** /jobs/single-doc | Operation for /jobs/single-doc
[**split_pdf_params**](DefaultApi.md#split_pdf_params) | **POST** /jobs/single-pdf-split | Operation for /jobs/single-pdf-split
[**split_pdf_with_capture_params**](DefaultApi.md#split_pdf_with_capture_params) | **POST** /jobs/single-pdf-split-addressCapture | Operation for /jobs/single-pdf-split-addressCapture
[**submit_multi_doc_params**](DefaultApi.md#submit_multi_doc_params) | **POST** /jobs/multi-doc | Operation for /jobs/multi-doc
[**submit_multi_doc_with_template_params**](DefaultApi.md#submit_multi_doc_with_template_params) | **POST** /jobs/multi-docs-job-template | Operation for /jobs/multi-docs-job-template
[**submit_single_doc_with_template_params**](DefaultApi.md#submit_single_doc_with_template_params) | **POST** /jobs/single-doc-job-template | Operation for /jobs/single-doc-job-template



## merge_multi_doc_params

> models::StandardResponse merge_multi_doc_params(merge_multi_doc_params_request)
Operation for /jobs/multi-doc-merge

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**merge_multi_doc_params_request** | [**MergeMultiDocParamsRequest**](MergeMultiDocParamsRequest.md) |  | [required] |

### Return type

[**models::StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## merge_multi_doc_with_template_params

> models::StandardResponse merge_multi_doc_with_template_params(merge_multi_doc_with_template_params_request)
Operation for /jobs/multi-doc-merge-job-template

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**merge_multi_doc_with_template_params_request** | [**MergeMultiDocWithTemplateParamsRequest**](MergeMultiDocWithTemplateParamsRequest.md) |  | [required] |

### Return type

[**models::StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## multi_pdf_with_capture_params

> models::StandardResponse multi_pdf_with_capture_params(multi_pdf_with_capture_params_request)
Operation for /jobs/multi-pdf-address-capture

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**multi_pdf_with_capture_params_request** | [**MultiPdfWithCaptureParamsRequest**](MultiPdfWithCaptureParamsRequest.md) |  | [required] |

### Return type

[**models::StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## single_doc_job_params

> models::StandardResponse single_doc_job_params(single_doc_job_params_request)
Operation for /jobs/single-doc

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**single_doc_job_params_request** | [**SingleDocJobParamsRequest**](SingleDocJobParamsRequest.md) |  | [required] |

### Return type

[**models::StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## split_pdf_params

> models::StandardResponse split_pdf_params(split_pdf_params_request)
Operation for /jobs/single-pdf-split

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**split_pdf_params_request** | [**SplitPdfParamsRequest**](SplitPdfParamsRequest.md) |  | [required] |

### Return type

[**models::StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## split_pdf_with_capture_params

> models::StandardResponse split_pdf_with_capture_params(split_pdf_with_capture_params_request)
Operation for /jobs/single-pdf-split-addressCapture

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**split_pdf_with_capture_params_request** | [**SplitPdfWithCaptureParamsRequest**](SplitPdfWithCaptureParamsRequest.md) |  | [required] |

### Return type

[**models::StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## submit_multi_doc_params

> models::StandardResponse submit_multi_doc_params(submit_multi_doc_params_request)
Operation for /jobs/multi-doc

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**submit_multi_doc_params_request** | [**SubmitMultiDocParamsRequest**](SubmitMultiDocParamsRequest.md) |  | [required] |

### Return type

[**models::StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## submit_multi_doc_with_template_params

> models::StandardResponse submit_multi_doc_with_template_params(submit_multi_doc_with_template_params_request)
Operation for /jobs/multi-docs-job-template

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**submit_multi_doc_with_template_params_request** | [**SubmitMultiDocWithTemplateParamsRequest**](SubmitMultiDocWithTemplateParamsRequest.md) |  | [required] |

### Return type

[**models::StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## submit_single_doc_with_template_params

> models::StandardResponse submit_single_doc_with_template_params(submit_single_doc_with_template_params_request)
Operation for /jobs/single-doc-job-template

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**submit_single_doc_with_template_params_request** | [**SubmitSingleDocWithTemplateParamsRequest**](SubmitSingleDocWithTemplateParamsRequest.md) |  | [required] |

### Return type

[**models::StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

