# SplitPdfParamsRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentSourceIdentifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**Items** | [**[]SplitPdfParamsRequestItemsInner**](SplitPdfParamsRequestItemsInner.md) |  | 
**PaymentDetails** | Pointer to [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewSplitPdfParamsRequest

`func NewSplitPdfParamsRequest(documentSourceIdentifier DocumentSourceIdentifier, items []SplitPdfParamsRequestItemsInner, ) *SplitPdfParamsRequest`

NewSplitPdfParamsRequest instantiates a new SplitPdfParamsRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSplitPdfParamsRequestWithDefaults

`func NewSplitPdfParamsRequestWithDefaults() *SplitPdfParamsRequest`

NewSplitPdfParamsRequestWithDefaults instantiates a new SplitPdfParamsRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentSourceIdentifier

`func (o *SplitPdfParamsRequest) GetDocumentSourceIdentifier() DocumentSourceIdentifier`

GetDocumentSourceIdentifier returns the DocumentSourceIdentifier field if non-nil, zero value otherwise.

### GetDocumentSourceIdentifierOk

`func (o *SplitPdfParamsRequest) GetDocumentSourceIdentifierOk() (*DocumentSourceIdentifier, bool)`

GetDocumentSourceIdentifierOk returns a tuple with the DocumentSourceIdentifier field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentSourceIdentifier

`func (o *SplitPdfParamsRequest) SetDocumentSourceIdentifier(v DocumentSourceIdentifier)`

SetDocumentSourceIdentifier sets DocumentSourceIdentifier field to given value.


### GetItems

`func (o *SplitPdfParamsRequest) GetItems() []SplitPdfParamsRequestItemsInner`

GetItems returns the Items field if non-nil, zero value otherwise.

### GetItemsOk

`func (o *SplitPdfParamsRequest) GetItemsOk() (*[]SplitPdfParamsRequestItemsInner, bool)`

GetItemsOk returns a tuple with the Items field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetItems

`func (o *SplitPdfParamsRequest) SetItems(v []SplitPdfParamsRequestItemsInner)`

SetItems sets Items field to given value.


### GetPaymentDetails

`func (o *SplitPdfParamsRequest) GetPaymentDetails() PaymentDetails`

GetPaymentDetails returns the PaymentDetails field if non-nil, zero value otherwise.

### GetPaymentDetailsOk

`func (o *SplitPdfParamsRequest) GetPaymentDetailsOk() (*PaymentDetails, bool)`

GetPaymentDetailsOk returns a tuple with the PaymentDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaymentDetails

`func (o *SplitPdfParamsRequest) SetPaymentDetails(v PaymentDetails)`

SetPaymentDetails sets PaymentDetails field to given value.

### HasPaymentDetails

`func (o *SplitPdfParamsRequest) HasPaymentDetails() bool`

HasPaymentDetails returns a boolean if a field has been set.

### GetTags

`func (o *SplitPdfParamsRequest) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *SplitPdfParamsRequest) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *SplitPdfParamsRequest) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *SplitPdfParamsRequest) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


