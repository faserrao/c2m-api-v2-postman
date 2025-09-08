# DefaultApi

All URIs are relative to *https://api.example.com/v1*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**mergeMultiDocParams**](#mergemultidocparams) | **POST** /jobs/multi-doc-merge | Operation for /jobs/multi-doc-merge|
|[**mergeMultiDocWithTemplateParams**](#mergemultidocwithtemplateparams) | **POST** /jobs/multi-doc-merge-job-template | Operation for /jobs/multi-doc-merge-job-template|
|[**multiPdfWithCaptureParams**](#multipdfwithcaptureparams) | **POST** /jobs/multi-pdf-address-capture | Operation for /jobs/multi-pdf-address-capture|
|[**singleDocJobParams**](#singledocjobparams) | **POST** /jobs/single-doc | Operation for /jobs/single-doc|
|[**splitPdfParams**](#splitpdfparams) | **POST** /jobs/single-pdf-split | Operation for /jobs/single-pdf-split|
|[**splitPdfWithCaptureParams**](#splitpdfwithcaptureparams) | **POST** /jobs/single-pdf-split-addressCapture | Operation for /jobs/single-pdf-split-addressCapture|
|[**submitMultiDocParams**](#submitmultidocparams) | **POST** /jobs/multi-doc | Operation for /jobs/multi-doc|
|[**submitMultiDocWithTemplateParams**](#submitmultidocwithtemplateparams) | **POST** /jobs/multi-docs-job-template | Operation for /jobs/multi-docs-job-template|
|[**submitSingleDocWithTemplateParams**](#submitsingledocwithtemplateparams) | **POST** /jobs/single-doc-job-template | Operation for /jobs/single-doc-job-template|

# **mergeMultiDocParams**
> StandardResponse mergeMultiDocParams(mergeMultiDocParamsRequest)


### Example

```typescript
import {
    DefaultApi,
    Configuration,
    MergeMultiDocParamsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let mergeMultiDocParamsRequest: MergeMultiDocParamsRequest; //

const { status, data } = await apiInstance.mergeMultiDocParams(
    mergeMultiDocParamsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **mergeMultiDocParamsRequest** | **MergeMultiDocParamsRequest**|  | |


### Return type

**StandardResponse**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Success |  -  |
|**400** | Invalid request |  -  |
|**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **mergeMultiDocWithTemplateParams**
> StandardResponse mergeMultiDocWithTemplateParams(mergeMultiDocWithTemplateParamsRequest)


### Example

```typescript
import {
    DefaultApi,
    Configuration,
    MergeMultiDocWithTemplateParamsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let mergeMultiDocWithTemplateParamsRequest: MergeMultiDocWithTemplateParamsRequest; //

const { status, data } = await apiInstance.mergeMultiDocWithTemplateParams(
    mergeMultiDocWithTemplateParamsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **mergeMultiDocWithTemplateParamsRequest** | **MergeMultiDocWithTemplateParamsRequest**|  | |


### Return type

**StandardResponse**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Success |  -  |
|**400** | Invalid request |  -  |
|**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **multiPdfWithCaptureParams**
> StandardResponse multiPdfWithCaptureParams(multiPdfWithCaptureParamsRequest)


### Example

```typescript
import {
    DefaultApi,
    Configuration,
    MultiPdfWithCaptureParamsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let multiPdfWithCaptureParamsRequest: MultiPdfWithCaptureParamsRequest; //

const { status, data } = await apiInstance.multiPdfWithCaptureParams(
    multiPdfWithCaptureParamsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **multiPdfWithCaptureParamsRequest** | **MultiPdfWithCaptureParamsRequest**|  | |


### Return type

**StandardResponse**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Success |  -  |
|**400** | Invalid request |  -  |
|**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **singleDocJobParams**
> StandardResponse singleDocJobParams(singleDocJobParamsRequest)


### Example

```typescript
import {
    DefaultApi,
    Configuration,
    SingleDocJobParamsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let singleDocJobParamsRequest: SingleDocJobParamsRequest; //

const { status, data } = await apiInstance.singleDocJobParams(
    singleDocJobParamsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **singleDocJobParamsRequest** | **SingleDocJobParamsRequest**|  | |


### Return type

**StandardResponse**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Success |  -  |
|**400** | Invalid request |  -  |
|**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **splitPdfParams**
> StandardResponse splitPdfParams(splitPdfParamsRequest)


### Example

```typescript
import {
    DefaultApi,
    Configuration,
    SplitPdfParamsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let splitPdfParamsRequest: SplitPdfParamsRequest; //

const { status, data } = await apiInstance.splitPdfParams(
    splitPdfParamsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **splitPdfParamsRequest** | **SplitPdfParamsRequest**|  | |


### Return type

**StandardResponse**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Success |  -  |
|**400** | Invalid request |  -  |
|**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **splitPdfWithCaptureParams**
> StandardResponse splitPdfWithCaptureParams(splitPdfWithCaptureParamsRequest)


### Example

```typescript
import {
    DefaultApi,
    Configuration,
    SplitPdfWithCaptureParamsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let splitPdfWithCaptureParamsRequest: SplitPdfWithCaptureParamsRequest; //

const { status, data } = await apiInstance.splitPdfWithCaptureParams(
    splitPdfWithCaptureParamsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **splitPdfWithCaptureParamsRequest** | **SplitPdfWithCaptureParamsRequest**|  | |


### Return type

**StandardResponse**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Success |  -  |
|**400** | Invalid request |  -  |
|**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **submitMultiDocParams**
> StandardResponse submitMultiDocParams(submitMultiDocParamsRequest)


### Example

```typescript
import {
    DefaultApi,
    Configuration,
    SubmitMultiDocParamsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let submitMultiDocParamsRequest: SubmitMultiDocParamsRequest; //

const { status, data } = await apiInstance.submitMultiDocParams(
    submitMultiDocParamsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **submitMultiDocParamsRequest** | **SubmitMultiDocParamsRequest**|  | |


### Return type

**StandardResponse**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Success |  -  |
|**400** | Invalid request |  -  |
|**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **submitMultiDocWithTemplateParams**
> StandardResponse submitMultiDocWithTemplateParams(submitMultiDocWithTemplateParamsRequest)


### Example

```typescript
import {
    DefaultApi,
    Configuration,
    SubmitMultiDocWithTemplateParamsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let submitMultiDocWithTemplateParamsRequest: SubmitMultiDocWithTemplateParamsRequest; //

const { status, data } = await apiInstance.submitMultiDocWithTemplateParams(
    submitMultiDocWithTemplateParamsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **submitMultiDocWithTemplateParamsRequest** | **SubmitMultiDocWithTemplateParamsRequest**|  | |


### Return type

**StandardResponse**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Success |  -  |
|**400** | Invalid request |  -  |
|**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **submitSingleDocWithTemplateParams**
> StandardResponse submitSingleDocWithTemplateParams(submitSingleDocWithTemplateParamsRequest)


### Example

```typescript
import {
    DefaultApi,
    Configuration,
    SubmitSingleDocWithTemplateParamsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let submitSingleDocWithTemplateParamsRequest: SubmitSingleDocWithTemplateParamsRequest; //

const { status, data } = await apiInstance.submitSingleDocWithTemplateParams(
    submitSingleDocWithTemplateParamsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **submitSingleDocWithTemplateParamsRequest** | **SubmitSingleDocWithTemplateParamsRequest**|  | |


### Return type

**StandardResponse**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Success |  -  |
|**400** | Invalid request |  -  |
|**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

