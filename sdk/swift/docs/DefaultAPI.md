# DefaultAPI

All URIs are relative to *https://api.example.com/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**mergeMultiDocParams**](DefaultAPI.md#mergemultidocparams) | **POST** /jobs/multi-doc-merge | Operation for /jobs/multi-doc-merge
[**mergeMultiDocWithTemplateParams**](DefaultAPI.md#mergemultidocwithtemplateparams) | **POST** /jobs/multi-doc-merge-job-template | Operation for /jobs/multi-doc-merge-job-template
[**multiPdfWithCaptureParams**](DefaultAPI.md#multipdfwithcaptureparams) | **POST** /jobs/multi-pdf-address-capture | Operation for /jobs/multi-pdf-address-capture
[**singleDocJobParams**](DefaultAPI.md#singledocjobparams) | **POST** /jobs/single-doc | Operation for /jobs/single-doc
[**splitPdfParams**](DefaultAPI.md#splitpdfparams) | **POST** /jobs/single-pdf-split | Operation for /jobs/single-pdf-split
[**splitPdfWithCaptureParams**](DefaultAPI.md#splitpdfwithcaptureparams) | **POST** /jobs/single-pdf-split-addressCapture | Operation for /jobs/single-pdf-split-addressCapture
[**submitMultiDocParams**](DefaultAPI.md#submitmultidocparams) | **POST** /jobs/multi-doc | Operation for /jobs/multi-doc
[**submitMultiDocWithTemplateParams**](DefaultAPI.md#submitmultidocwithtemplateparams) | **POST** /jobs/multi-docs-job-template | Operation for /jobs/multi-docs-job-template
[**submitSingleDocWithTemplateParams**](DefaultAPI.md#submitsingledocwithtemplateparams) | **POST** /jobs/single-doc-job-template | Operation for /jobs/single-doc-job-template


# **mergeMultiDocParams**
```swift
    open class func mergeMultiDocParams(mergeMultiDocParamsRequest: MergeMultiDocParamsRequest, completion: @escaping (_ data: StandardResponse?, _ error: Error?) -> Void)
```

Operation for /jobs/multi-doc-merge

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OpenAPIClient

let mergeMultiDocParamsRequest = mergeMultiDocParams_request(documentsToMerge: [documentSourceIdentifier(uploadRequestId: 123, documentName: "documentName_example", zipId: 123)], recipientAddressSource: recipientAddressSource(firstName: "firstName_example", lastName: "lastName_example", address1: "address1_example", city: "city_example", state: "state_example", zip: "zip_example", country: "country_example", nickName: "nickName_example", address2: "address2_example", address3: "address3_example", phoneNumber: "phoneNumber_example"), tags: ["tags_example"]) // MergeMultiDocParamsRequest | 

// Operation for /jobs/multi-doc-merge
DefaultAPI.mergeMultiDocParams(mergeMultiDocParamsRequest: mergeMultiDocParamsRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **mergeMultiDocWithTemplateParams**
```swift
    open class func mergeMultiDocWithTemplateParams(mergeMultiDocWithTemplateParamsRequest: MergeMultiDocWithTemplateParamsRequest, completion: @escaping (_ data: StandardResponse?, _ error: Error?) -> Void)
```

Operation for /jobs/multi-doc-merge-job-template

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OpenAPIClient

let mergeMultiDocWithTemplateParamsRequest = mergeMultiDocWithTemplateParams_request(documentsToMerge: [documentSourceIdentifier(uploadRequestId: 123, documentName: "documentName_example", zipId: 123)], recipientAddressSource: recipientAddressSource(firstName: "firstName_example", lastName: "lastName_example", address1: "address1_example", city: "city_example", state: "state_example", zip: "zip_example", country: "country_example", nickName: "nickName_example", address2: "address2_example", address3: "address3_example", phoneNumber: "phoneNumber_example"), jobTemplate: "jobTemplate_example", paymentDetails: paymentDetails(creditCardDetails: creditCardDetails(cardType: cardType(), cardNumber: "cardNumber_example", expirationDate: expirationDate(month: 123, year: 123), cvv: 123), invoiceDetails: invoiceDetails(invoiceNumber: "invoiceNumber_example", amountDue: 123), achDetails: achDetails(routingNumber: "routingNumber_example", accountNumber: "accountNumber_example", checkDigit: 123), creditAmount: creditAmount(amount: 123, currency: currency()), applePaymentDetails: 123, googlePaymentDetails: 123), tags: ["tags_example"]) // MergeMultiDocWithTemplateParamsRequest | 

// Operation for /jobs/multi-doc-merge-job-template
DefaultAPI.mergeMultiDocWithTemplateParams(mergeMultiDocWithTemplateParamsRequest: mergeMultiDocWithTemplateParamsRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **multiPdfWithCaptureParams**
```swift
    open class func multiPdfWithCaptureParams(multiPdfWithCaptureParamsRequest: MultiPdfWithCaptureParamsRequest, completion: @escaping (_ data: StandardResponse?, _ error: Error?) -> Void)
```

Operation for /jobs/multi-pdf-address-capture

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OpenAPIClient

let multiPdfWithCaptureParamsRequest = multiPdfWithCaptureParams_request(addressCapturePdfs: [addressListPdf(documentSourceIdentifier: documentSourceIdentifier(uploadRequestId: 123, documentName: "documentName_example", zipId: 123), addressListRegion: "addressListRegion_example", delimiter: "delimiter_example", tags: ["tags_example"])], jobTemplate: "jobTemplate_example", paymentDetails: paymentDetails(creditCardDetails: creditCardDetails(cardType: cardType(), cardNumber: "cardNumber_example", expirationDate: expirationDate(month: 123, year: 123), cvv: 123), invoiceDetails: invoiceDetails(invoiceNumber: "invoiceNumber_example", amountDue: 123), achDetails: achDetails(routingNumber: "routingNumber_example", accountNumber: "accountNumber_example", checkDigit: 123), creditAmount: creditAmount(amount: 123, currency: currency()), applePaymentDetails: 123, googlePaymentDetails: 123), tags: ["tags_example"]) // MultiPdfWithCaptureParamsRequest | 

// Operation for /jobs/multi-pdf-address-capture
DefaultAPI.multiPdfWithCaptureParams(multiPdfWithCaptureParamsRequest: multiPdfWithCaptureParamsRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **singleDocJobParams**
```swift
    open class func singleDocJobParams(singleDocJobParamsRequest: SingleDocJobParamsRequest, completion: @escaping (_ data: StandardResponse?, _ error: Error?) -> Void)
```

Operation for /jobs/single-doc

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OpenAPIClient

let singleDocJobParamsRequest = singleDocJobParams_request(documentSourceIdentifier: documentSourceIdentifier(uploadRequestId: 123, documentName: "documentName_example", zipId: 123), recipientAddressSources: [recipientAddressSource(firstName: "firstName_example", lastName: "lastName_example", address1: "address1_example", city: "city_example", state: "state_example", zip: "zip_example", country: "country_example", nickName: "nickName_example", address2: "address2_example", address3: "address3_example", phoneNumber: "phoneNumber_example")], jobOptions: jobOptions(documentClass: documentClass(), layout: layout(), mailclass: mailclass(), paperType: paperType(), printOption: printOption(), envelope: envelope()), paymentDetails: paymentDetails(creditCardDetails: creditCardDetails(cardType: cardType(), cardNumber: "cardNumber_example", expirationDate: expirationDate(month: 123, year: 123), cvv: 123), invoiceDetails: invoiceDetails(invoiceNumber: "invoiceNumber_example", amountDue: 123), achDetails: achDetails(routingNumber: "routingNumber_example", accountNumber: "accountNumber_example", checkDigit: 123), creditAmount: creditAmount(amount: 123, currency: currency()), applePaymentDetails: 123, googlePaymentDetails: 123), tags: ["tags_example"]) // SingleDocJobParamsRequest | 

// Operation for /jobs/single-doc
DefaultAPI.singleDocJobParams(singleDocJobParamsRequest: singleDocJobParamsRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **splitPdfParams**
```swift
    open class func splitPdfParams(splitPdfParamsRequest: SplitPdfParamsRequest, completion: @escaping (_ data: StandardResponse?, _ error: Error?) -> Void)
```

Operation for /jobs/single-pdf-split

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OpenAPIClient

let splitPdfParamsRequest = splitPdfParams_request(documentSourceIdentifier: documentSourceIdentifier(uploadRequestId: 123, documentName: "documentName_example", zipId: 123), items: [splitPdfParams_request_items_inner(pageRange: pageRange(startPage: 123, endPage: 123), recipientAddressSources: [recipientAddressSource(firstName: "firstName_example", lastName: "lastName_example", address1: "address1_example", city: "city_example", state: "state_example", zip: "zip_example", country: "country_example", nickName: "nickName_example", address2: "address2_example", address3: "address3_example", phoneNumber: "phoneNumber_example")])], paymentDetails: paymentDetails(creditCardDetails: creditCardDetails(cardType: cardType(), cardNumber: "cardNumber_example", expirationDate: expirationDate(month: 123, year: 123), cvv: 123), invoiceDetails: invoiceDetails(invoiceNumber: "invoiceNumber_example", amountDue: 123), achDetails: achDetails(routingNumber: "routingNumber_example", accountNumber: "accountNumber_example", checkDigit: 123), creditAmount: creditAmount(amount: 123, currency: currency()), applePaymentDetails: 123, googlePaymentDetails: 123), tags: ["tags_example"]) // SplitPdfParamsRequest | 

// Operation for /jobs/single-pdf-split
DefaultAPI.splitPdfParams(splitPdfParamsRequest: splitPdfParamsRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **splitPdfWithCaptureParams**
```swift
    open class func splitPdfWithCaptureParams(splitPdfWithCaptureParamsRequest: SplitPdfWithCaptureParamsRequest, completion: @escaping (_ data: StandardResponse?, _ error: Error?) -> Void)
```

Operation for /jobs/single-pdf-split-addressCapture

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OpenAPIClient

let splitPdfWithCaptureParamsRequest = splitPdfWithCaptureParams_request(documentSourceIdentifier: documentSourceIdentifier(uploadRequestId: 123, documentName: "documentName_example", zipId: 123), embeddedExtractionSpecs: [extractionSpec(startPage: 123, endPage: 123, addressRegion: addressRegion(x: 123, y: 123, width: 123, height: 123, pageOffset: 123))], paymentDetails: paymentDetails(creditCardDetails: creditCardDetails(cardType: cardType(), cardNumber: "cardNumber_example", expirationDate: expirationDate(month: 123, year: 123), cvv: 123), invoiceDetails: invoiceDetails(invoiceNumber: "invoiceNumber_example", amountDue: 123), achDetails: achDetails(routingNumber: "routingNumber_example", accountNumber: "accountNumber_example", checkDigit: 123), creditAmount: creditAmount(amount: 123, currency: currency()), applePaymentDetails: 123, googlePaymentDetails: 123), tags: ["tags_example"]) // SplitPdfWithCaptureParamsRequest | 

// Operation for /jobs/single-pdf-split-addressCapture
DefaultAPI.splitPdfWithCaptureParams(splitPdfWithCaptureParamsRequest: splitPdfWithCaptureParamsRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **submitMultiDocParams**
```swift
    open class func submitMultiDocParams(submitMultiDocParamsRequest: SubmitMultiDocParamsRequest, completion: @escaping (_ data: StandardResponse?, _ error: Error?) -> Void)
```

Operation for /jobs/multi-doc

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OpenAPIClient

let submitMultiDocParamsRequest = submitMultiDocParams_request(items: [submitMultiDocWithTemplateParams_request_items_inner(documentSourceIdentifier: documentSourceIdentifier(uploadRequestId: 123, documentName: "documentName_example", zipId: 123), recipientAddressSource: recipientAddressSource(firstName: "firstName_example", lastName: "lastName_example", address1: "address1_example", city: "city_example", state: "state_example", zip: "zip_example", country: "country_example", nickName: "nickName_example", address2: "address2_example", address3: "address3_example", phoneNumber: "phoneNumber_example"))], jobOptions: jobOptions(documentClass: documentClass(), layout: layout(), mailclass: mailclass(), paperType: paperType(), printOption: printOption(), envelope: envelope()), paymentDetails: paymentDetails(creditCardDetails: creditCardDetails(cardType: cardType(), cardNumber: "cardNumber_example", expirationDate: expirationDate(month: 123, year: 123), cvv: 123), invoiceDetails: invoiceDetails(invoiceNumber: "invoiceNumber_example", amountDue: 123), achDetails: achDetails(routingNumber: "routingNumber_example", accountNumber: "accountNumber_example", checkDigit: 123), creditAmount: creditAmount(amount: 123, currency: currency()), applePaymentDetails: 123, googlePaymentDetails: 123), tags: ["tags_example"]) // SubmitMultiDocParamsRequest | 

// Operation for /jobs/multi-doc
DefaultAPI.submitMultiDocParams(submitMultiDocParamsRequest: submitMultiDocParamsRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **submitMultiDocWithTemplateParams**
```swift
    open class func submitMultiDocWithTemplateParams(submitMultiDocWithTemplateParamsRequest: SubmitMultiDocWithTemplateParamsRequest, completion: @escaping (_ data: StandardResponse?, _ error: Error?) -> Void)
```

Operation for /jobs/multi-docs-job-template

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OpenAPIClient

let submitMultiDocWithTemplateParamsRequest = submitMultiDocWithTemplateParams_request(items: [submitMultiDocWithTemplateParams_request_items_inner(documentSourceIdentifier: documentSourceIdentifier(uploadRequestId: 123, documentName: "documentName_example", zipId: 123), recipientAddressSource: recipientAddressSource(firstName: "firstName_example", lastName: "lastName_example", address1: "address1_example", city: "city_example", state: "state_example", zip: "zip_example", country: "country_example", nickName: "nickName_example", address2: "address2_example", address3: "address3_example", phoneNumber: "phoneNumber_example"))], jobTemplate: "jobTemplate_example", paymentDetails: paymentDetails(creditCardDetails: creditCardDetails(cardType: cardType(), cardNumber: "cardNumber_example", expirationDate: expirationDate(month: 123, year: 123), cvv: 123), invoiceDetails: invoiceDetails(invoiceNumber: "invoiceNumber_example", amountDue: 123), achDetails: achDetails(routingNumber: "routingNumber_example", accountNumber: "accountNumber_example", checkDigit: 123), creditAmount: creditAmount(amount: 123, currency: currency()), applePaymentDetails: 123, googlePaymentDetails: 123), tags: ["tags_example"]) // SubmitMultiDocWithTemplateParamsRequest | 

// Operation for /jobs/multi-docs-job-template
DefaultAPI.submitMultiDocWithTemplateParams(submitMultiDocWithTemplateParamsRequest: submitMultiDocWithTemplateParamsRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **submitSingleDocWithTemplateParams**
```swift
    open class func submitSingleDocWithTemplateParams(submitSingleDocWithTemplateParamsRequest: SubmitSingleDocWithTemplateParamsRequest, completion: @escaping (_ data: StandardResponse?, _ error: Error?) -> Void)
```

Operation for /jobs/single-doc-job-template

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OpenAPIClient

let submitSingleDocWithTemplateParamsRequest = submitSingleDocWithTemplateParams_request(jobTemplate: "jobTemplate_example", paymentDetails: paymentDetails(creditCardDetails: creditCardDetails(cardType: cardType(), cardNumber: "cardNumber_example", expirationDate: expirationDate(month: 123, year: 123), cvv: 123), invoiceDetails: invoiceDetails(invoiceNumber: "invoiceNumber_example", amountDue: 123), achDetails: achDetails(routingNumber: "routingNumber_example", accountNumber: "accountNumber_example", checkDigit: 123), creditAmount: creditAmount(amount: 123, currency: currency()), applePaymentDetails: 123, googlePaymentDetails: 123), tags: ["tags_example"]) // SubmitSingleDocWithTemplateParamsRequest | 

// Operation for /jobs/single-doc-job-template
DefaultAPI.submitSingleDocWithTemplateParams(submitSingleDocWithTemplateParamsRequest: submitSingleDocWithTemplateParamsRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

