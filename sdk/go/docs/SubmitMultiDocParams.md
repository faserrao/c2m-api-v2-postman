# SubmitMultiDocParams

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Items** | [**[]SubmitMultiDocWithTemplateParamsRequestItemsInner**](SubmitMultiDocWithTemplateParamsRequestItemsInner.md) |  | 
**JobOptions** | [**JobOptions**](JobOptions.md) |  | 
**PaymentDetails** | Pointer to [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewSubmitMultiDocParams

`func NewSubmitMultiDocParams(items []SubmitMultiDocWithTemplateParamsRequestItemsInner, jobOptions JobOptions, ) *SubmitMultiDocParams`

NewSubmitMultiDocParams instantiates a new SubmitMultiDocParams object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSubmitMultiDocParamsWithDefaults

`func NewSubmitMultiDocParamsWithDefaults() *SubmitMultiDocParams`

NewSubmitMultiDocParamsWithDefaults instantiates a new SubmitMultiDocParams object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetItems

`func (o *SubmitMultiDocParams) GetItems() []SubmitMultiDocWithTemplateParamsRequestItemsInner`

GetItems returns the Items field if non-nil, zero value otherwise.

### GetItemsOk

`func (o *SubmitMultiDocParams) GetItemsOk() (*[]SubmitMultiDocWithTemplateParamsRequestItemsInner, bool)`

GetItemsOk returns a tuple with the Items field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetItems

`func (o *SubmitMultiDocParams) SetItems(v []SubmitMultiDocWithTemplateParamsRequestItemsInner)`

SetItems sets Items field to given value.


### GetJobOptions

`func (o *SubmitMultiDocParams) GetJobOptions() JobOptions`

GetJobOptions returns the JobOptions field if non-nil, zero value otherwise.

### GetJobOptionsOk

`func (o *SubmitMultiDocParams) GetJobOptionsOk() (*JobOptions, bool)`

GetJobOptionsOk returns a tuple with the JobOptions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJobOptions

`func (o *SubmitMultiDocParams) SetJobOptions(v JobOptions)`

SetJobOptions sets JobOptions field to given value.


### GetPaymentDetails

`func (o *SubmitMultiDocParams) GetPaymentDetails() PaymentDetails`

GetPaymentDetails returns the PaymentDetails field if non-nil, zero value otherwise.

### GetPaymentDetailsOk

`func (o *SubmitMultiDocParams) GetPaymentDetailsOk() (*PaymentDetails, bool)`

GetPaymentDetailsOk returns a tuple with the PaymentDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaymentDetails

`func (o *SubmitMultiDocParams) SetPaymentDetails(v PaymentDetails)`

SetPaymentDetails sets PaymentDetails field to given value.

### HasPaymentDetails

`func (o *SubmitMultiDocParams) HasPaymentDetails() bool`

HasPaymentDetails returns a boolean if a field has been set.

### GetTags

`func (o *SubmitMultiDocParams) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *SubmitMultiDocParams) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *SubmitMultiDocParams) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *SubmitMultiDocParams) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


