# \DefaultAPI

All URIs are relative to *https://api.example.com/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**MergeMultiDocParams**](DefaultAPI.md#MergeMultiDocParams) | **Post** /jobs/multi-doc-merge | Operation for /jobs/multi-doc-merge
[**MergeMultiDocWithTemplateParams**](DefaultAPI.md#MergeMultiDocWithTemplateParams) | **Post** /jobs/multi-doc-merge-job-template | Operation for /jobs/multi-doc-merge-job-template
[**MultiPdfWithCaptureParams**](DefaultAPI.md#MultiPdfWithCaptureParams) | **Post** /jobs/multi-pdf-address-capture | Operation for /jobs/multi-pdf-address-capture
[**SingleDocJobParams**](DefaultAPI.md#SingleDocJobParams) | **Post** /jobs/single-doc | Operation for /jobs/single-doc
[**SplitPdfParams**](DefaultAPI.md#SplitPdfParams) | **Post** /jobs/single-pdf-split | Operation for /jobs/single-pdf-split
[**SplitPdfWithCaptureParams**](DefaultAPI.md#SplitPdfWithCaptureParams) | **Post** /jobs/single-pdf-split-addressCapture | Operation for /jobs/single-pdf-split-addressCapture
[**SubmitMultiDocParams**](DefaultAPI.md#SubmitMultiDocParams) | **Post** /jobs/multi-doc | Operation for /jobs/multi-doc
[**SubmitMultiDocWithTemplateParams**](DefaultAPI.md#SubmitMultiDocWithTemplateParams) | **Post** /jobs/multi-docs-job-template | Operation for /jobs/multi-docs-job-template
[**SubmitSingleDocWithTemplateParams**](DefaultAPI.md#SubmitSingleDocWithTemplateParams) | **Post** /jobs/single-doc-job-template | Operation for /jobs/single-doc-job-template



## MergeMultiDocParams

> StandardResponse MergeMultiDocParams(ctx).MergeMultiDocParamsRequest(mergeMultiDocParamsRequest).Execute()

Operation for /jobs/multi-doc-merge

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	mergeMultiDocParamsRequest := *openapiclient.NewMergeMultiDocParamsRequest([]openapiclient.DocumentSourceIdentifier{openapiclient.documentSourceIdentifier{DocumentSourceIdentifierOneOf: openapiclient.NewDocumentSourceIdentifierOneOf(int32(123), "DocumentName_example")}}, openapiclient.recipientAddressSource{RecipientAddress: openapiclient.NewRecipientAddress("FirstName_example", "LastName_example", "Address1_example", "City_example", "State_example", "Zip_example", "Country_example")}) // MergeMultiDocParamsRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DefaultAPI.MergeMultiDocParams(context.Background()).MergeMultiDocParamsRequest(mergeMultiDocParamsRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DefaultAPI.MergeMultiDocParams``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `MergeMultiDocParams`: StandardResponse
	fmt.Fprintf(os.Stdout, "Response from `DefaultAPI.MergeMultiDocParams`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiMergeMultiDocParamsRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mergeMultiDocParamsRequest** | [**MergeMultiDocParamsRequest**](MergeMultiDocParamsRequest.md) |  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## MergeMultiDocWithTemplateParams

> StandardResponse MergeMultiDocWithTemplateParams(ctx).MergeMultiDocWithTemplateParamsRequest(mergeMultiDocWithTemplateParamsRequest).Execute()

Operation for /jobs/multi-doc-merge-job-template

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	mergeMultiDocWithTemplateParamsRequest := *openapiclient.NewMergeMultiDocWithTemplateParamsRequest([]openapiclient.DocumentSourceIdentifier{openapiclient.documentSourceIdentifier{DocumentSourceIdentifierOneOf: openapiclient.NewDocumentSourceIdentifierOneOf(int32(123), "DocumentName_example")}}, openapiclient.recipientAddressSource{RecipientAddress: openapiclient.NewRecipientAddress("FirstName_example", "LastName_example", "Address1_example", "City_example", "State_example", "Zip_example", "Country_example")}, "JobTemplate_example") // MergeMultiDocWithTemplateParamsRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DefaultAPI.MergeMultiDocWithTemplateParams(context.Background()).MergeMultiDocWithTemplateParamsRequest(mergeMultiDocWithTemplateParamsRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DefaultAPI.MergeMultiDocWithTemplateParams``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `MergeMultiDocWithTemplateParams`: StandardResponse
	fmt.Fprintf(os.Stdout, "Response from `DefaultAPI.MergeMultiDocWithTemplateParams`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiMergeMultiDocWithTemplateParamsRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mergeMultiDocWithTemplateParamsRequest** | [**MergeMultiDocWithTemplateParamsRequest**](MergeMultiDocWithTemplateParamsRequest.md) |  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## MultiPdfWithCaptureParams

> StandardResponse MultiPdfWithCaptureParams(ctx).MultiPdfWithCaptureParamsRequest(multiPdfWithCaptureParamsRequest).Execute()

Operation for /jobs/multi-pdf-address-capture

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	multiPdfWithCaptureParamsRequest := *openapiclient.NewMultiPdfWithCaptureParamsRequest([]openapiclient.AddressListPdf{*openapiclient.NewAddressListPdf(openapiclient.documentSourceIdentifier{DocumentSourceIdentifierOneOf: openapiclient.NewDocumentSourceIdentifierOneOf(int32(123), "DocumentName_example")}, "AddressListRegion_example")}, "JobTemplate_example") // MultiPdfWithCaptureParamsRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DefaultAPI.MultiPdfWithCaptureParams(context.Background()).MultiPdfWithCaptureParamsRequest(multiPdfWithCaptureParamsRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DefaultAPI.MultiPdfWithCaptureParams``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `MultiPdfWithCaptureParams`: StandardResponse
	fmt.Fprintf(os.Stdout, "Response from `DefaultAPI.MultiPdfWithCaptureParams`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiMultiPdfWithCaptureParamsRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **multiPdfWithCaptureParamsRequest** | [**MultiPdfWithCaptureParamsRequest**](MultiPdfWithCaptureParamsRequest.md) |  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SingleDocJobParams

> StandardResponse SingleDocJobParams(ctx).SingleDocJobParamsRequest(singleDocJobParamsRequest).Execute()

Operation for /jobs/single-doc

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	singleDocJobParamsRequest := *openapiclient.NewSingleDocJobParamsRequest(openapiclient.documentSourceIdentifier{DocumentSourceIdentifierOneOf: openapiclient.NewDocumentSourceIdentifierOneOf(int32(123), "DocumentName_example")}, []openapiclient.RecipientAddressSource{openapiclient.recipientAddressSource{RecipientAddress: openapiclient.NewRecipientAddress("FirstName_example", "LastName_example", "Address1_example", "City_example", "State_example", "Zip_example", "Country_example")}}, *openapiclient.NewJobOptions(openapiclient.documentClass("businessLetter"), openapiclient.layout("portrait"), openapiclient.mailclass("firstClassMail"), openapiclient.paperType("letter"), openapiclient.printOption("none"), openapiclient.envelope("flat"))) // SingleDocJobParamsRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DefaultAPI.SingleDocJobParams(context.Background()).SingleDocJobParamsRequest(singleDocJobParamsRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DefaultAPI.SingleDocJobParams``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SingleDocJobParams`: StandardResponse
	fmt.Fprintf(os.Stdout, "Response from `DefaultAPI.SingleDocJobParams`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSingleDocJobParamsRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **singleDocJobParamsRequest** | [**SingleDocJobParamsRequest**](SingleDocJobParamsRequest.md) |  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SplitPdfParams

> StandardResponse SplitPdfParams(ctx).SplitPdfParamsRequest(splitPdfParamsRequest).Execute()

Operation for /jobs/single-pdf-split

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	splitPdfParamsRequest := *openapiclient.NewSplitPdfParamsRequest(openapiclient.documentSourceIdentifier{DocumentSourceIdentifierOneOf: openapiclient.NewDocumentSourceIdentifierOneOf(int32(123), "DocumentName_example")}, []openapiclient.SplitPdfParamsRequestItemsInner{*openapiclient.NewSplitPdfParamsRequestItemsInner(*openapiclient.NewPageRange(int32(123), int32(123)), []openapiclient.RecipientAddressSource{openapiclient.recipientAddressSource{RecipientAddress: openapiclient.NewRecipientAddress("FirstName_example", "LastName_example", "Address1_example", "City_example", "State_example", "Zip_example", "Country_example")}})}) // SplitPdfParamsRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DefaultAPI.SplitPdfParams(context.Background()).SplitPdfParamsRequest(splitPdfParamsRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DefaultAPI.SplitPdfParams``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SplitPdfParams`: StandardResponse
	fmt.Fprintf(os.Stdout, "Response from `DefaultAPI.SplitPdfParams`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSplitPdfParamsRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **splitPdfParamsRequest** | [**SplitPdfParamsRequest**](SplitPdfParamsRequest.md) |  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SplitPdfWithCaptureParams

> StandardResponse SplitPdfWithCaptureParams(ctx).SplitPdfWithCaptureParamsRequest(splitPdfWithCaptureParamsRequest).Execute()

Operation for /jobs/single-pdf-split-addressCapture

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	splitPdfWithCaptureParamsRequest := *openapiclient.NewSplitPdfWithCaptureParamsRequest(openapiclient.documentSourceIdentifier{DocumentSourceIdentifierOneOf: openapiclient.NewDocumentSourceIdentifierOneOf(int32(123), "DocumentName_example")}, []openapiclient.ExtractionSpec{*openapiclient.NewExtractionSpec(int32(123), int32(123), *openapiclient.NewAddressRegion(float32(123), float32(123), float32(123), float32(123), int32(123)))}) // SplitPdfWithCaptureParamsRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DefaultAPI.SplitPdfWithCaptureParams(context.Background()).SplitPdfWithCaptureParamsRequest(splitPdfWithCaptureParamsRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DefaultAPI.SplitPdfWithCaptureParams``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SplitPdfWithCaptureParams`: StandardResponse
	fmt.Fprintf(os.Stdout, "Response from `DefaultAPI.SplitPdfWithCaptureParams`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSplitPdfWithCaptureParamsRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **splitPdfWithCaptureParamsRequest** | [**SplitPdfWithCaptureParamsRequest**](SplitPdfWithCaptureParamsRequest.md) |  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SubmitMultiDocParams

> StandardResponse SubmitMultiDocParams(ctx).SubmitMultiDocParamsRequest(submitMultiDocParamsRequest).Execute()

Operation for /jobs/multi-doc

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	submitMultiDocParamsRequest := *openapiclient.NewSubmitMultiDocParamsRequest([]openapiclient.SubmitMultiDocWithTemplateParamsRequestItemsInner{*openapiclient.NewSubmitMultiDocWithTemplateParamsRequestItemsInner(openapiclient.documentSourceIdentifier{DocumentSourceIdentifierOneOf: openapiclient.NewDocumentSourceIdentifierOneOf(int32(123), "DocumentName_example")}, openapiclient.recipientAddressSource{RecipientAddress: openapiclient.NewRecipientAddress("FirstName_example", "LastName_example", "Address1_example", "City_example", "State_example", "Zip_example", "Country_example")})}, *openapiclient.NewJobOptions(openapiclient.documentClass("businessLetter"), openapiclient.layout("portrait"), openapiclient.mailclass("firstClassMail"), openapiclient.paperType("letter"), openapiclient.printOption("none"), openapiclient.envelope("flat"))) // SubmitMultiDocParamsRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DefaultAPI.SubmitMultiDocParams(context.Background()).SubmitMultiDocParamsRequest(submitMultiDocParamsRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DefaultAPI.SubmitMultiDocParams``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SubmitMultiDocParams`: StandardResponse
	fmt.Fprintf(os.Stdout, "Response from `DefaultAPI.SubmitMultiDocParams`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSubmitMultiDocParamsRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **submitMultiDocParamsRequest** | [**SubmitMultiDocParamsRequest**](SubmitMultiDocParamsRequest.md) |  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SubmitMultiDocWithTemplateParams

> StandardResponse SubmitMultiDocWithTemplateParams(ctx).SubmitMultiDocWithTemplateParamsRequest(submitMultiDocWithTemplateParamsRequest).Execute()

Operation for /jobs/multi-docs-job-template

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	submitMultiDocWithTemplateParamsRequest := *openapiclient.NewSubmitMultiDocWithTemplateParamsRequest([]openapiclient.SubmitMultiDocWithTemplateParamsRequestItemsInner{*openapiclient.NewSubmitMultiDocWithTemplateParamsRequestItemsInner(openapiclient.documentSourceIdentifier{DocumentSourceIdentifierOneOf: openapiclient.NewDocumentSourceIdentifierOneOf(int32(123), "DocumentName_example")}, openapiclient.recipientAddressSource{RecipientAddress: openapiclient.NewRecipientAddress("FirstName_example", "LastName_example", "Address1_example", "City_example", "State_example", "Zip_example", "Country_example")})}, "JobTemplate_example", openapiclient.paymentDetails{AchPayment: openapiclient.NewAchPayment(*openapiclient.NewAchDetails("RoutingNumber_example", "AccountNumber_example", int32(123)))}) // SubmitMultiDocWithTemplateParamsRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DefaultAPI.SubmitMultiDocWithTemplateParams(context.Background()).SubmitMultiDocWithTemplateParamsRequest(submitMultiDocWithTemplateParamsRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DefaultAPI.SubmitMultiDocWithTemplateParams``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SubmitMultiDocWithTemplateParams`: StandardResponse
	fmt.Fprintf(os.Stdout, "Response from `DefaultAPI.SubmitMultiDocWithTemplateParams`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSubmitMultiDocWithTemplateParamsRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **submitMultiDocWithTemplateParamsRequest** | [**SubmitMultiDocWithTemplateParamsRequest**](SubmitMultiDocWithTemplateParamsRequest.md) |  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SubmitSingleDocWithTemplateParams

> StandardResponse SubmitSingleDocWithTemplateParams(ctx).SubmitSingleDocWithTemplateParamsRequest(submitSingleDocWithTemplateParamsRequest).Execute()

Operation for /jobs/single-doc-job-template

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	submitSingleDocWithTemplateParamsRequest := *openapiclient.NewSubmitSingleDocWithTemplateParamsRequest("JobTemplate_example") // SubmitSingleDocWithTemplateParamsRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DefaultAPI.SubmitSingleDocWithTemplateParams(context.Background()).SubmitSingleDocWithTemplateParamsRequest(submitSingleDocWithTemplateParamsRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DefaultAPI.SubmitSingleDocWithTemplateParams``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SubmitSingleDocWithTemplateParams`: StandardResponse
	fmt.Fprintf(os.Stdout, "Response from `DefaultAPI.SubmitSingleDocWithTemplateParams`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSubmitSingleDocWithTemplateParamsRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **submitSingleDocWithTemplateParamsRequest** | [**SubmitSingleDocWithTemplateParamsRequest**](SubmitSingleDocWithTemplateParamsRequest.md) |  | 

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

