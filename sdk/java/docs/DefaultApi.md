# DefaultApi

All URIs are relative to *https://api.example.com/v1*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
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
```java
// Import classes:
import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.models.*;
import com.c2m.api.DefaultApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("https://api.example.com/v1");
    
    // Configure HTTP bearer authorization: bearerAuth
    HttpBearerAuth bearerAuth = (HttpBearerAuth) defaultClient.getAuthentication("bearerAuth");
    bearerAuth.setBearerToken("BEARER TOKEN");

    DefaultApi apiInstance = new DefaultApi(defaultClient);
    MergeMultiDocParamsRequest mergeMultiDocParamsRequest = new MergeMultiDocParamsRequest(); // MergeMultiDocParamsRequest | 
    try {
      StandardResponse result = apiInstance.mergeMultiDocParams(mergeMultiDocParamsRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling DefaultApi#mergeMultiDocParams");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **mergeMultiDocParamsRequest** | [**MergeMultiDocParamsRequest**](MergeMultiDocParamsRequest.md)|  | |

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

<a id="mergeMultiDocWithTemplateParams"></a>
# **mergeMultiDocWithTemplateParams**
> StandardResponse mergeMultiDocWithTemplateParams(mergeMultiDocWithTemplateParamsRequest)

Operation for /jobs/multi-doc-merge-job-template

### Example
```java
// Import classes:
import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.models.*;
import com.c2m.api.DefaultApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("https://api.example.com/v1");
    
    // Configure HTTP bearer authorization: bearerAuth
    HttpBearerAuth bearerAuth = (HttpBearerAuth) defaultClient.getAuthentication("bearerAuth");
    bearerAuth.setBearerToken("BEARER TOKEN");

    DefaultApi apiInstance = new DefaultApi(defaultClient);
    MergeMultiDocWithTemplateParamsRequest mergeMultiDocWithTemplateParamsRequest = new MergeMultiDocWithTemplateParamsRequest(); // MergeMultiDocWithTemplateParamsRequest | 
    try {
      StandardResponse result = apiInstance.mergeMultiDocWithTemplateParams(mergeMultiDocWithTemplateParamsRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling DefaultApi#mergeMultiDocWithTemplateParams");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **mergeMultiDocWithTemplateParamsRequest** | [**MergeMultiDocWithTemplateParamsRequest**](MergeMultiDocWithTemplateParamsRequest.md)|  | |

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

<a id="multiPdfWithCaptureParams"></a>
# **multiPdfWithCaptureParams**
> StandardResponse multiPdfWithCaptureParams(multiPdfWithCaptureParamsRequest)

Operation for /jobs/multi-pdf-address-capture

### Example
```java
// Import classes:
import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.models.*;
import com.c2m.api.DefaultApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("https://api.example.com/v1");
    
    // Configure HTTP bearer authorization: bearerAuth
    HttpBearerAuth bearerAuth = (HttpBearerAuth) defaultClient.getAuthentication("bearerAuth");
    bearerAuth.setBearerToken("BEARER TOKEN");

    DefaultApi apiInstance = new DefaultApi(defaultClient);
    MultiPdfWithCaptureParamsRequest multiPdfWithCaptureParamsRequest = new MultiPdfWithCaptureParamsRequest(); // MultiPdfWithCaptureParamsRequest | 
    try {
      StandardResponse result = apiInstance.multiPdfWithCaptureParams(multiPdfWithCaptureParamsRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling DefaultApi#multiPdfWithCaptureParams");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **multiPdfWithCaptureParamsRequest** | [**MultiPdfWithCaptureParamsRequest**](MultiPdfWithCaptureParamsRequest.md)|  | |

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

<a id="singleDocJobParams"></a>
# **singleDocJobParams**
> StandardResponse singleDocJobParams(singleDocJobParamsRequest)

Operation for /jobs/single-doc

### Example
```java
// Import classes:
import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.models.*;
import com.c2m.api.DefaultApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("https://api.example.com/v1");
    
    // Configure HTTP bearer authorization: bearerAuth
    HttpBearerAuth bearerAuth = (HttpBearerAuth) defaultClient.getAuthentication("bearerAuth");
    bearerAuth.setBearerToken("BEARER TOKEN");

    DefaultApi apiInstance = new DefaultApi(defaultClient);
    SingleDocJobParamsRequest singleDocJobParamsRequest = new SingleDocJobParamsRequest(); // SingleDocJobParamsRequest | 
    try {
      StandardResponse result = apiInstance.singleDocJobParams(singleDocJobParamsRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling DefaultApi#singleDocJobParams");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **singleDocJobParamsRequest** | [**SingleDocJobParamsRequest**](SingleDocJobParamsRequest.md)|  | |

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

<a id="splitPdfParams"></a>
# **splitPdfParams**
> StandardResponse splitPdfParams(splitPdfParamsRequest)

Operation for /jobs/single-pdf-split

### Example
```java
// Import classes:
import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.models.*;
import com.c2m.api.DefaultApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("https://api.example.com/v1");
    
    // Configure HTTP bearer authorization: bearerAuth
    HttpBearerAuth bearerAuth = (HttpBearerAuth) defaultClient.getAuthentication("bearerAuth");
    bearerAuth.setBearerToken("BEARER TOKEN");

    DefaultApi apiInstance = new DefaultApi(defaultClient);
    SplitPdfParamsRequest splitPdfParamsRequest = new SplitPdfParamsRequest(); // SplitPdfParamsRequest | 
    try {
      StandardResponse result = apiInstance.splitPdfParams(splitPdfParamsRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling DefaultApi#splitPdfParams");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **splitPdfParamsRequest** | [**SplitPdfParamsRequest**](SplitPdfParamsRequest.md)|  | |

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

<a id="splitPdfWithCaptureParams"></a>
# **splitPdfWithCaptureParams**
> StandardResponse splitPdfWithCaptureParams(splitPdfWithCaptureParamsRequest)

Operation for /jobs/single-pdf-split-addressCapture

### Example
```java
// Import classes:
import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.models.*;
import com.c2m.api.DefaultApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("https://api.example.com/v1");
    
    // Configure HTTP bearer authorization: bearerAuth
    HttpBearerAuth bearerAuth = (HttpBearerAuth) defaultClient.getAuthentication("bearerAuth");
    bearerAuth.setBearerToken("BEARER TOKEN");

    DefaultApi apiInstance = new DefaultApi(defaultClient);
    SplitPdfWithCaptureParamsRequest splitPdfWithCaptureParamsRequest = new SplitPdfWithCaptureParamsRequest(); // SplitPdfWithCaptureParamsRequest | 
    try {
      StandardResponse result = apiInstance.splitPdfWithCaptureParams(splitPdfWithCaptureParamsRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling DefaultApi#splitPdfWithCaptureParams");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **splitPdfWithCaptureParamsRequest** | [**SplitPdfWithCaptureParamsRequest**](SplitPdfWithCaptureParamsRequest.md)|  | |

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

<a id="submitMultiDocParams"></a>
# **submitMultiDocParams**
> StandardResponse submitMultiDocParams(submitMultiDocParamsRequest)

Operation for /jobs/multi-doc

### Example
```java
// Import classes:
import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.models.*;
import com.c2m.api.DefaultApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("https://api.example.com/v1");
    
    // Configure HTTP bearer authorization: bearerAuth
    HttpBearerAuth bearerAuth = (HttpBearerAuth) defaultClient.getAuthentication("bearerAuth");
    bearerAuth.setBearerToken("BEARER TOKEN");

    DefaultApi apiInstance = new DefaultApi(defaultClient);
    SubmitMultiDocParamsRequest submitMultiDocParamsRequest = new SubmitMultiDocParamsRequest(); // SubmitMultiDocParamsRequest | 
    try {
      StandardResponse result = apiInstance.submitMultiDocParams(submitMultiDocParamsRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling DefaultApi#submitMultiDocParams");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **submitMultiDocParamsRequest** | [**SubmitMultiDocParamsRequest**](SubmitMultiDocParamsRequest.md)|  | |

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

<a id="submitMultiDocWithTemplateParams"></a>
# **submitMultiDocWithTemplateParams**
> StandardResponse submitMultiDocWithTemplateParams(submitMultiDocWithTemplateParamsRequest)

Operation for /jobs/multi-docs-job-template

### Example
```java
// Import classes:
import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.models.*;
import com.c2m.api.DefaultApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("https://api.example.com/v1");
    
    // Configure HTTP bearer authorization: bearerAuth
    HttpBearerAuth bearerAuth = (HttpBearerAuth) defaultClient.getAuthentication("bearerAuth");
    bearerAuth.setBearerToken("BEARER TOKEN");

    DefaultApi apiInstance = new DefaultApi(defaultClient);
    SubmitMultiDocWithTemplateParamsRequest submitMultiDocWithTemplateParamsRequest = new SubmitMultiDocWithTemplateParamsRequest(); // SubmitMultiDocWithTemplateParamsRequest | 
    try {
      StandardResponse result = apiInstance.submitMultiDocWithTemplateParams(submitMultiDocWithTemplateParamsRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling DefaultApi#submitMultiDocWithTemplateParams");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **submitMultiDocWithTemplateParamsRequest** | [**SubmitMultiDocWithTemplateParamsRequest**](SubmitMultiDocWithTemplateParamsRequest.md)|  | |

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

<a id="submitSingleDocWithTemplateParams"></a>
# **submitSingleDocWithTemplateParams**
> StandardResponse submitSingleDocWithTemplateParams(submitSingleDocWithTemplateParamsRequest)

Operation for /jobs/single-doc-job-template

### Example
```java
// Import classes:
import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.models.*;
import com.c2m.api.DefaultApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("https://api.example.com/v1");
    
    // Configure HTTP bearer authorization: bearerAuth
    HttpBearerAuth bearerAuth = (HttpBearerAuth) defaultClient.getAuthentication("bearerAuth");
    bearerAuth.setBearerToken("BEARER TOKEN");

    DefaultApi apiInstance = new DefaultApi(defaultClient);
    SubmitSingleDocWithTemplateParamsRequest submitSingleDocWithTemplateParamsRequest = new SubmitSingleDocWithTemplateParamsRequest(); // SubmitSingleDocWithTemplateParamsRequest | 
    try {
      StandardResponse result = apiInstance.submitSingleDocWithTemplateParams(submitSingleDocWithTemplateParamsRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling DefaultApi#submitSingleDocWithTemplateParams");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **submitSingleDocWithTemplateParamsRequest** | [**SubmitSingleDocWithTemplateParamsRequest**](SubmitSingleDocWithTemplateParamsRequest.md)|  | |

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

