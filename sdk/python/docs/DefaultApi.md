# c2m_api.DefaultApi

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


# **merge_multi_doc_params**
> StandardResponse merge_multi_doc_params(merge_multi_doc_params_request)

Operation for /jobs/multi-doc-merge

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import c2m_api
from c2m_api.models.merge_multi_doc_params_request import MergeMultiDocParamsRequest
from c2m_api.models.standard_response import StandardResponse
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

# Configure Bearer authorization (JWT): bearerAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = c2m_api.DefaultApi(api_client)
    merge_multi_doc_params_request = c2m_api.MergeMultiDocParamsRequest() # MergeMultiDocParamsRequest | 

    try:
        # Operation for /jobs/multi-doc-merge
        api_response = api_instance.merge_multi_doc_params(merge_multi_doc_params_request)
        print("The response of DefaultApi->merge_multi_doc_params:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->merge_multi_doc_params: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merge_multi_doc_params_request** | [**MergeMultiDocParamsRequest**](MergeMultiDocParamsRequest.md)|  | 

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
**200** | Success |  -  |
**400** | Invalid request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **merge_multi_doc_with_template_params**
> StandardResponse merge_multi_doc_with_template_params(merge_multi_doc_with_template_params_request)

Operation for /jobs/multi-doc-merge-job-template

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import c2m_api
from c2m_api.models.merge_multi_doc_with_template_params_request import MergeMultiDocWithTemplateParamsRequest
from c2m_api.models.standard_response import StandardResponse
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

# Configure Bearer authorization (JWT): bearerAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = c2m_api.DefaultApi(api_client)
    merge_multi_doc_with_template_params_request = c2m_api.MergeMultiDocWithTemplateParamsRequest() # MergeMultiDocWithTemplateParamsRequest | 

    try:
        # Operation for /jobs/multi-doc-merge-job-template
        api_response = api_instance.merge_multi_doc_with_template_params(merge_multi_doc_with_template_params_request)
        print("The response of DefaultApi->merge_multi_doc_with_template_params:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->merge_multi_doc_with_template_params: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merge_multi_doc_with_template_params_request** | [**MergeMultiDocWithTemplateParamsRequest**](MergeMultiDocWithTemplateParamsRequest.md)|  | 

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
**200** | Success |  -  |
**400** | Invalid request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **multi_pdf_with_capture_params**
> StandardResponse multi_pdf_with_capture_params(multi_pdf_with_capture_params_request)

Operation for /jobs/multi-pdf-address-capture

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import c2m_api
from c2m_api.models.multi_pdf_with_capture_params_request import MultiPdfWithCaptureParamsRequest
from c2m_api.models.standard_response import StandardResponse
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

# Configure Bearer authorization (JWT): bearerAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = c2m_api.DefaultApi(api_client)
    multi_pdf_with_capture_params_request = c2m_api.MultiPdfWithCaptureParamsRequest() # MultiPdfWithCaptureParamsRequest | 

    try:
        # Operation for /jobs/multi-pdf-address-capture
        api_response = api_instance.multi_pdf_with_capture_params(multi_pdf_with_capture_params_request)
        print("The response of DefaultApi->multi_pdf_with_capture_params:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->multi_pdf_with_capture_params: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **multi_pdf_with_capture_params_request** | [**MultiPdfWithCaptureParamsRequest**](MultiPdfWithCaptureParamsRequest.md)|  | 

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
**200** | Success |  -  |
**400** | Invalid request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **single_doc_job_params**
> StandardResponse single_doc_job_params(single_doc_job_params_request)

Operation for /jobs/single-doc

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import c2m_api
from c2m_api.models.single_doc_job_params_request import SingleDocJobParamsRequest
from c2m_api.models.standard_response import StandardResponse
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

# Configure Bearer authorization (JWT): bearerAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = c2m_api.DefaultApi(api_client)
    single_doc_job_params_request = c2m_api.SingleDocJobParamsRequest() # SingleDocJobParamsRequest | 

    try:
        # Operation for /jobs/single-doc
        api_response = api_instance.single_doc_job_params(single_doc_job_params_request)
        print("The response of DefaultApi->single_doc_job_params:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->single_doc_job_params: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **single_doc_job_params_request** | [**SingleDocJobParamsRequest**](SingleDocJobParamsRequest.md)|  | 

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
**200** | Success |  -  |
**400** | Invalid request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **split_pdf_params**
> StandardResponse split_pdf_params(split_pdf_params_request)

Operation for /jobs/single-pdf-split

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import c2m_api
from c2m_api.models.split_pdf_params_request import SplitPdfParamsRequest
from c2m_api.models.standard_response import StandardResponse
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

# Configure Bearer authorization (JWT): bearerAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = c2m_api.DefaultApi(api_client)
    split_pdf_params_request = c2m_api.SplitPdfParamsRequest() # SplitPdfParamsRequest | 

    try:
        # Operation for /jobs/single-pdf-split
        api_response = api_instance.split_pdf_params(split_pdf_params_request)
        print("The response of DefaultApi->split_pdf_params:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->split_pdf_params: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **split_pdf_params_request** | [**SplitPdfParamsRequest**](SplitPdfParamsRequest.md)|  | 

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
**200** | Success |  -  |
**400** | Invalid request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **split_pdf_with_capture_params**
> StandardResponse split_pdf_with_capture_params(split_pdf_with_capture_params_request)

Operation for /jobs/single-pdf-split-addressCapture

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import c2m_api
from c2m_api.models.split_pdf_with_capture_params_request import SplitPdfWithCaptureParamsRequest
from c2m_api.models.standard_response import StandardResponse
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

# Configure Bearer authorization (JWT): bearerAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = c2m_api.DefaultApi(api_client)
    split_pdf_with_capture_params_request = c2m_api.SplitPdfWithCaptureParamsRequest() # SplitPdfWithCaptureParamsRequest | 

    try:
        # Operation for /jobs/single-pdf-split-addressCapture
        api_response = api_instance.split_pdf_with_capture_params(split_pdf_with_capture_params_request)
        print("The response of DefaultApi->split_pdf_with_capture_params:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->split_pdf_with_capture_params: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **split_pdf_with_capture_params_request** | [**SplitPdfWithCaptureParamsRequest**](SplitPdfWithCaptureParamsRequest.md)|  | 

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
**200** | Success |  -  |
**400** | Invalid request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **submit_multi_doc_params**
> StandardResponse submit_multi_doc_params(submit_multi_doc_params_request)

Operation for /jobs/multi-doc

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import c2m_api
from c2m_api.models.standard_response import StandardResponse
from c2m_api.models.submit_multi_doc_params_request import SubmitMultiDocParamsRequest
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

# Configure Bearer authorization (JWT): bearerAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = c2m_api.DefaultApi(api_client)
    submit_multi_doc_params_request = c2m_api.SubmitMultiDocParamsRequest() # SubmitMultiDocParamsRequest | 

    try:
        # Operation for /jobs/multi-doc
        api_response = api_instance.submit_multi_doc_params(submit_multi_doc_params_request)
        print("The response of DefaultApi->submit_multi_doc_params:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->submit_multi_doc_params: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **submit_multi_doc_params_request** | [**SubmitMultiDocParamsRequest**](SubmitMultiDocParamsRequest.md)|  | 

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
**200** | Success |  -  |
**400** | Invalid request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **submit_multi_doc_with_template_params**
> StandardResponse submit_multi_doc_with_template_params(submit_multi_doc_with_template_params_request)

Operation for /jobs/multi-docs-job-template

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import c2m_api
from c2m_api.models.standard_response import StandardResponse
from c2m_api.models.submit_multi_doc_with_template_params_request import SubmitMultiDocWithTemplateParamsRequest
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

# Configure Bearer authorization (JWT): bearerAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = c2m_api.DefaultApi(api_client)
    submit_multi_doc_with_template_params_request = c2m_api.SubmitMultiDocWithTemplateParamsRequest() # SubmitMultiDocWithTemplateParamsRequest | 

    try:
        # Operation for /jobs/multi-docs-job-template
        api_response = api_instance.submit_multi_doc_with_template_params(submit_multi_doc_with_template_params_request)
        print("The response of DefaultApi->submit_multi_doc_with_template_params:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->submit_multi_doc_with_template_params: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **submit_multi_doc_with_template_params_request** | [**SubmitMultiDocWithTemplateParamsRequest**](SubmitMultiDocWithTemplateParamsRequest.md)|  | 

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
**200** | Success |  -  |
**400** | Invalid request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **submit_single_doc_with_template_params**
> StandardResponse submit_single_doc_with_template_params(submit_single_doc_with_template_params_request)

Operation for /jobs/single-doc-job-template

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import c2m_api
from c2m_api.models.standard_response import StandardResponse
from c2m_api.models.submit_single_doc_with_template_params_request import SubmitSingleDocWithTemplateParamsRequest
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

# Configure Bearer authorization (JWT): bearerAuth
configuration = c2m_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = c2m_api.DefaultApi(api_client)
    submit_single_doc_with_template_params_request = c2m_api.SubmitSingleDocWithTemplateParamsRequest() # SubmitSingleDocWithTemplateParamsRequest | 

    try:
        # Operation for /jobs/single-doc-job-template
        api_response = api_instance.submit_single_doc_with_template_params(submit_single_doc_with_template_params_request)
        print("The response of DefaultApi->submit_single_doc_with_template_params:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->submit_single_doc_with_template_params: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **submit_single_doc_with_template_params_request** | [**SubmitSingleDocWithTemplateParamsRequest**](SubmitSingleDocWithTemplateParamsRequest.md)|  | 

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
**200** | Success |  -  |
**400** | Invalid request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

