# DefaultApi

All URIs are relative to *https://api.example.com/v1*

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**mergeMultiDocParams**](DefaultApi.md#mergeMultiDocParams) | **POST** /jobs/multi-doc-merge | Operation for /jobs/multi-doc-merge |
| [**mergeMultiDocWithTemplateParams**](DefaultApi.md#mergeMultiDocWithTemplateParams) | **POST** /jobs/multi-doc-merge-job-template | Operation for /jobs/multi-doc-merge-job-template |
| [**multiPdfWithCaptureParams**](DefaultApi.md#multiPdfWithCaptureParams) | **POST** /jobs/multi-pdf-address-capture | Operation for /jobs/multi-pdf-address-capture |
| [**singleDocJobParams**](DefaultApi.md#singleDocJobParams) | **POST** /jobs/single-doc | Operation for /jobs/single-doc |
| [**splitPdfParams**](DefaultApi.md#splitPdfParams) | **POST** /jobs/single-pdf-split | Operation for /jobs/single-pdf-split |
| [**splitPdfWithCaptureParams**](DefaultApi.md#splitPdfWithCaptureParams) | **POST** /jobs/single-pdf-split-addressCapture | Operation for /jobs/single-pdf-split-addressCapture |
| [**submitMultiDocParams**](DefaultApi.md#submitMultiDocParams) | **POST** /jobs/multi-doc | Operation for /jobs/multi-doc |
| [**submitMultiDocWithTemplateParams**](DefaultApi.md#submitMultiDocWithTemplateParams) | **POST** /jobs/multi-docs-job-template | Operation for /jobs/multi-docs-job-template |
| [**submitSingleDocWithTemplateParams**](DefaultApi.md#submitSingleDocWithTemplateParams) | **POST** /jobs/single-doc-job-template | Operation for /jobs/single-doc-job-template |


<a id="mergeMultiDocParams"></a>
# **mergeMultiDocParams**
> StandardResponse mergeMultiDocParams(mergeMultiDocParamsRequest)

Operation for /jobs/multi-doc-merge

### Example
```kotlin
// Import classes:
//import com.c2m.api.infrastructure.*
//import com.c2m.api.models.*

val apiInstance = DefaultApi()
val mergeMultiDocParamsRequest : MergeMultiDocParamsRequest =  // MergeMultiDocParamsRequest | 
try {
    val result : StandardResponse = apiInstance.mergeMultiDocParams(mergeMultiDocParamsRequest)
    println(result)
} catch (e: ClientException) {
    println("4xx response calling DefaultApi#mergeMultiDocParams")
    e.printStackTrace()
} catch (e: ServerException) {
    println("5xx response calling DefaultApi#mergeMultiDocParams")
    e.printStackTrace()
}
```

### Parameters
| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **mergeMultiDocParamsRequest** | [**MergeMultiDocParamsRequest**](MergeMultiDocParamsRequest.md)|  | |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization


Configure bearerAuth:
    ApiClient.accessToken = ""

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

<a id="mergeMultiDocWithTemplateParams"></a>
# **mergeMultiDocWithTemplateParams**
> StandardResponse mergeMultiDocWithTemplateParams(mergeMultiDocWithTemplateParamsRequest)

Operation for /jobs/multi-doc-merge-job-template

### Example
```kotlin
// Import classes:
//import com.c2m.api.infrastructure.*
//import com.c2m.api.models.*

val apiInstance = DefaultApi()
val mergeMultiDocWithTemplateParamsRequest : MergeMultiDocWithTemplateParamsRequest =  // MergeMultiDocWithTemplateParamsRequest | 
try {
    val result : StandardResponse = apiInstance.mergeMultiDocWithTemplateParams(mergeMultiDocWithTemplateParamsRequest)
    println(result)
} catch (e: ClientException) {
    println("4xx response calling DefaultApi#mergeMultiDocWithTemplateParams")
    e.printStackTrace()
} catch (e: ServerException) {
    println("5xx response calling DefaultApi#mergeMultiDocWithTemplateParams")
    e.printStackTrace()
}
```

### Parameters
| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **mergeMultiDocWithTemplateParamsRequest** | [**MergeMultiDocWithTemplateParamsRequest**](MergeMultiDocWithTemplateParamsRequest.md)|  | |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization


Configure bearerAuth:
    ApiClient.accessToken = ""

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

<a id="multiPdfWithCaptureParams"></a>
# **multiPdfWithCaptureParams**
> StandardResponse multiPdfWithCaptureParams(multiPdfWithCaptureParamsRequest)

Operation for /jobs/multi-pdf-address-capture

### Example
```kotlin
// Import classes:
//import com.c2m.api.infrastructure.*
//import com.c2m.api.models.*

val apiInstance = DefaultApi()
val multiPdfWithCaptureParamsRequest : MultiPdfWithCaptureParamsRequest =  // MultiPdfWithCaptureParamsRequest | 
try {
    val result : StandardResponse = apiInstance.multiPdfWithCaptureParams(multiPdfWithCaptureParamsRequest)
    println(result)
} catch (e: ClientException) {
    println("4xx response calling DefaultApi#multiPdfWithCaptureParams")
    e.printStackTrace()
} catch (e: ServerException) {
    println("5xx response calling DefaultApi#multiPdfWithCaptureParams")
    e.printStackTrace()
}
```

### Parameters
| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **multiPdfWithCaptureParamsRequest** | [**MultiPdfWithCaptureParamsRequest**](MultiPdfWithCaptureParamsRequest.md)|  | |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization


Configure bearerAuth:
    ApiClient.accessToken = ""

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

<a id="singleDocJobParams"></a>
# **singleDocJobParams**
> StandardResponse singleDocJobParams(singleDocJobParamsRequest)

Operation for /jobs/single-doc

### Example
```kotlin
// Import classes:
//import com.c2m.api.infrastructure.*
//import com.c2m.api.models.*

val apiInstance = DefaultApi()
val singleDocJobParamsRequest : SingleDocJobParamsRequest =  // SingleDocJobParamsRequest | 
try {
    val result : StandardResponse = apiInstance.singleDocJobParams(singleDocJobParamsRequest)
    println(result)
} catch (e: ClientException) {
    println("4xx response calling DefaultApi#singleDocJobParams")
    e.printStackTrace()
} catch (e: ServerException) {
    println("5xx response calling DefaultApi#singleDocJobParams")
    e.printStackTrace()
}
```

### Parameters
| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **singleDocJobParamsRequest** | [**SingleDocJobParamsRequest**](SingleDocJobParamsRequest.md)|  | |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization


Configure bearerAuth:
    ApiClient.accessToken = ""

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

<a id="splitPdfParams"></a>
# **splitPdfParams**
> StandardResponse splitPdfParams(splitPdfParamsRequest)

Operation for /jobs/single-pdf-split

### Example
```kotlin
// Import classes:
//import com.c2m.api.infrastructure.*
//import com.c2m.api.models.*

val apiInstance = DefaultApi()
val splitPdfParamsRequest : SplitPdfParamsRequest =  // SplitPdfParamsRequest | 
try {
    val result : StandardResponse = apiInstance.splitPdfParams(splitPdfParamsRequest)
    println(result)
} catch (e: ClientException) {
    println("4xx response calling DefaultApi#splitPdfParams")
    e.printStackTrace()
} catch (e: ServerException) {
    println("5xx response calling DefaultApi#splitPdfParams")
    e.printStackTrace()
}
```

### Parameters
| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **splitPdfParamsRequest** | [**SplitPdfParamsRequest**](SplitPdfParamsRequest.md)|  | |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization


Configure bearerAuth:
    ApiClient.accessToken = ""

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

<a id="splitPdfWithCaptureParams"></a>
# **splitPdfWithCaptureParams**
> StandardResponse splitPdfWithCaptureParams(splitPdfWithCaptureParamsRequest)

Operation for /jobs/single-pdf-split-addressCapture

### Example
```kotlin
// Import classes:
//import com.c2m.api.infrastructure.*
//import com.c2m.api.models.*

val apiInstance = DefaultApi()
val splitPdfWithCaptureParamsRequest : SplitPdfWithCaptureParamsRequest =  // SplitPdfWithCaptureParamsRequest | 
try {
    val result : StandardResponse = apiInstance.splitPdfWithCaptureParams(splitPdfWithCaptureParamsRequest)
    println(result)
} catch (e: ClientException) {
    println("4xx response calling DefaultApi#splitPdfWithCaptureParams")
    e.printStackTrace()
} catch (e: ServerException) {
    println("5xx response calling DefaultApi#splitPdfWithCaptureParams")
    e.printStackTrace()
}
```

### Parameters
| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **splitPdfWithCaptureParamsRequest** | [**SplitPdfWithCaptureParamsRequest**](SplitPdfWithCaptureParamsRequest.md)|  | |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization


Configure bearerAuth:
    ApiClient.accessToken = ""

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

<a id="submitMultiDocParams"></a>
# **submitMultiDocParams**
> StandardResponse submitMultiDocParams(submitMultiDocParamsRequest)

Operation for /jobs/multi-doc

### Example
```kotlin
// Import classes:
//import com.c2m.api.infrastructure.*
//import com.c2m.api.models.*

val apiInstance = DefaultApi()
val submitMultiDocParamsRequest : SubmitMultiDocParamsRequest =  // SubmitMultiDocParamsRequest | 
try {
    val result : StandardResponse = apiInstance.submitMultiDocParams(submitMultiDocParamsRequest)
    println(result)
} catch (e: ClientException) {
    println("4xx response calling DefaultApi#submitMultiDocParams")
    e.printStackTrace()
} catch (e: ServerException) {
    println("5xx response calling DefaultApi#submitMultiDocParams")
    e.printStackTrace()
}
```

### Parameters
| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **submitMultiDocParamsRequest** | [**SubmitMultiDocParamsRequest**](SubmitMultiDocParamsRequest.md)|  | |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization


Configure bearerAuth:
    ApiClient.accessToken = ""

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

<a id="submitMultiDocWithTemplateParams"></a>
# **submitMultiDocWithTemplateParams**
> StandardResponse submitMultiDocWithTemplateParams(submitMultiDocWithTemplateParamsRequest)

Operation for /jobs/multi-docs-job-template

### Example
```kotlin
// Import classes:
//import com.c2m.api.infrastructure.*
//import com.c2m.api.models.*

val apiInstance = DefaultApi()
val submitMultiDocWithTemplateParamsRequest : SubmitMultiDocWithTemplateParamsRequest =  // SubmitMultiDocWithTemplateParamsRequest | 
try {
    val result : StandardResponse = apiInstance.submitMultiDocWithTemplateParams(submitMultiDocWithTemplateParamsRequest)
    println(result)
} catch (e: ClientException) {
    println("4xx response calling DefaultApi#submitMultiDocWithTemplateParams")
    e.printStackTrace()
} catch (e: ServerException) {
    println("5xx response calling DefaultApi#submitMultiDocWithTemplateParams")
    e.printStackTrace()
}
```

### Parameters
| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **submitMultiDocWithTemplateParamsRequest** | [**SubmitMultiDocWithTemplateParamsRequest**](SubmitMultiDocWithTemplateParamsRequest.md)|  | |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization


Configure bearerAuth:
    ApiClient.accessToken = ""

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

<a id="submitSingleDocWithTemplateParams"></a>
# **submitSingleDocWithTemplateParams**
> StandardResponse submitSingleDocWithTemplateParams(submitSingleDocWithTemplateParamsRequest)

Operation for /jobs/single-doc-job-template

### Example
```kotlin
// Import classes:
//import com.c2m.api.infrastructure.*
//import com.c2m.api.models.*

val apiInstance = DefaultApi()
val submitSingleDocWithTemplateParamsRequest : SubmitSingleDocWithTemplateParamsRequest =  // SubmitSingleDocWithTemplateParamsRequest | 
try {
    val result : StandardResponse = apiInstance.submitSingleDocWithTemplateParams(submitSingleDocWithTemplateParamsRequest)
    println(result)
} catch (e: ClientException) {
    println("4xx response calling DefaultApi#submitSingleDocWithTemplateParams")
    e.printStackTrace()
} catch (e: ServerException) {
    println("5xx response calling DefaultApi#submitSingleDocWithTemplateParams")
    e.printStackTrace()
}
```

### Parameters
| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **submitSingleDocWithTemplateParamsRequest** | [**SubmitSingleDocWithTemplateParamsRequest**](SubmitSingleDocWithTemplateParamsRequest.md)|  | |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization


Configure bearerAuth:
    ApiClient.accessToken = ""

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

