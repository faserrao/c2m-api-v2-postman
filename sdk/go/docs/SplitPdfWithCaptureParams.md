# SplitPdfWithCaptureParams

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentSourceIdentifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**EmbeddedExtractionSpecs** | [**[]ExtractionSpec**](ExtractionSpec.md) |  | 
**PaymentDetails** | Pointer to [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewSplitPdfWithCaptureParams

`func NewSplitPdfWithCaptureParams(documentSourceIdentifier DocumentSourceIdentifier, embeddedExtractionSpecs []ExtractionSpec, ) *SplitPdfWithCaptureParams`

NewSplitPdfWithCaptureParams instantiates a new SplitPdfWithCaptureParams object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSplitPdfWithCaptureParamsWithDefaults

`func NewSplitPdfWithCaptureParamsWithDefaults() *SplitPdfWithCaptureParams`

NewSplitPdfWithCaptureParamsWithDefaults instantiates a new SplitPdfWithCaptureParams object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentSourceIdentifier

`func (o *SplitPdfWithCaptureParams) GetDocumentSourceIdentifier() DocumentSourceIdentifier`

GetDocumentSourceIdentifier returns the DocumentSourceIdentifier field if non-nil, zero value otherwise.

### GetDocumentSourceIdentifierOk

`func (o *SplitPdfWithCaptureParams) GetDocumentSourceIdentifierOk() (*DocumentSourceIdentifier, bool)`

GetDocumentSourceIdentifierOk returns a tuple with the DocumentSourceIdentifier field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentSourceIdentifier

`func (o *SplitPdfWithCaptureParams) SetDocumentSourceIdentifier(v DocumentSourceIdentifier)`

SetDocumentSourceIdentifier sets DocumentSourceIdentifier field to given value.


### GetEmbeddedExtractionSpecs

`func (o *SplitPdfWithCaptureParams) GetEmbeddedExtractionSpecs() []ExtractionSpec`

GetEmbeddedExtractionSpecs returns the EmbeddedExtractionSpecs field if non-nil, zero value otherwise.

### GetEmbeddedExtractionSpecsOk

`func (o *SplitPdfWithCaptureParams) GetEmbeddedExtractionSpecsOk() (*[]ExtractionSpec, bool)`

GetEmbeddedExtractionSpecsOk returns a tuple with the EmbeddedExtractionSpecs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbeddedExtractionSpecs

`func (o *SplitPdfWithCaptureParams) SetEmbeddedExtractionSpecs(v []ExtractionSpec)`

SetEmbeddedExtractionSpecs sets EmbeddedExtractionSpecs field to given value.


### GetPaymentDetails

`func (o *SplitPdfWithCaptureParams) GetPaymentDetails() PaymentDetails`

GetPaymentDetails returns the PaymentDetails field if non-nil, zero value otherwise.

### GetPaymentDetailsOk

`func (o *SplitPdfWithCaptureParams) GetPaymentDetailsOk() (*PaymentDetails, bool)`

GetPaymentDetailsOk returns a tuple with the PaymentDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaymentDetails

`func (o *SplitPdfWithCaptureParams) SetPaymentDetails(v PaymentDetails)`

SetPaymentDetails sets PaymentDetails field to given value.

### HasPaymentDetails

`func (o *SplitPdfWithCaptureParams) HasPaymentDetails() bool`

HasPaymentDetails returns a boolean if a field has been set.

### GetTags

`func (o *SplitPdfWithCaptureParams) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *SplitPdfWithCaptureParams) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *SplitPdfWithCaptureParams) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *SplitPdfWithCaptureParams) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


