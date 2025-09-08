# SubmitMultiDocWithTemplateParamsRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Items** | [**[]SubmitMultiDocWithTemplateParamsRequestItemsInner**](SubmitMultiDocWithTemplateParamsRequestItemsInner.md) |  | 
**JobTemplate** | **string** |  | 
**PaymentDetails** | [**PaymentDetails**](PaymentDetails.md) |  | 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewSubmitMultiDocWithTemplateParamsRequest

`func NewSubmitMultiDocWithTemplateParamsRequest(items []SubmitMultiDocWithTemplateParamsRequestItemsInner, jobTemplate string, paymentDetails PaymentDetails, ) *SubmitMultiDocWithTemplateParamsRequest`

NewSubmitMultiDocWithTemplateParamsRequest instantiates a new SubmitMultiDocWithTemplateParamsRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSubmitMultiDocWithTemplateParamsRequestWithDefaults

`func NewSubmitMultiDocWithTemplateParamsRequestWithDefaults() *SubmitMultiDocWithTemplateParamsRequest`

NewSubmitMultiDocWithTemplateParamsRequestWithDefaults instantiates a new SubmitMultiDocWithTemplateParamsRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetItems

`func (o *SubmitMultiDocWithTemplateParamsRequest) GetItems() []SubmitMultiDocWithTemplateParamsRequestItemsInner`

GetItems returns the Items field if non-nil, zero value otherwise.

### GetItemsOk

`func (o *SubmitMultiDocWithTemplateParamsRequest) GetItemsOk() (*[]SubmitMultiDocWithTemplateParamsRequestItemsInner, bool)`

GetItemsOk returns a tuple with the Items field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetItems

`func (o *SubmitMultiDocWithTemplateParamsRequest) SetItems(v []SubmitMultiDocWithTemplateParamsRequestItemsInner)`

SetItems sets Items field to given value.


### GetJobTemplate

`func (o *SubmitMultiDocWithTemplateParamsRequest) GetJobTemplate() string`

GetJobTemplate returns the JobTemplate field if non-nil, zero value otherwise.

### GetJobTemplateOk

`func (o *SubmitMultiDocWithTemplateParamsRequest) GetJobTemplateOk() (*string, bool)`

GetJobTemplateOk returns a tuple with the JobTemplate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJobTemplate

`func (o *SubmitMultiDocWithTemplateParamsRequest) SetJobTemplate(v string)`

SetJobTemplate sets JobTemplate field to given value.


### GetPaymentDetails

`func (o *SubmitMultiDocWithTemplateParamsRequest) GetPaymentDetails() PaymentDetails`

GetPaymentDetails returns the PaymentDetails field if non-nil, zero value otherwise.

### GetPaymentDetailsOk

`func (o *SubmitMultiDocWithTemplateParamsRequest) GetPaymentDetailsOk() (*PaymentDetails, bool)`

GetPaymentDetailsOk returns a tuple with the PaymentDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaymentDetails

`func (o *SubmitMultiDocWithTemplateParamsRequest) SetPaymentDetails(v PaymentDetails)`

SetPaymentDetails sets PaymentDetails field to given value.


### GetTags

`func (o *SubmitMultiDocWithTemplateParamsRequest) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *SubmitMultiDocWithTemplateParamsRequest) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *SubmitMultiDocWithTemplateParamsRequest) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *SubmitMultiDocWithTemplateParamsRequest) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


