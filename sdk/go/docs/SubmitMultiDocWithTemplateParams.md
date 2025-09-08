# SubmitMultiDocWithTemplateParams

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Items** | [**[]SubmitMultiDocWithTemplateParamsRequestItemsInner**](SubmitMultiDocWithTemplateParamsRequestItemsInner.md) |  | 
**JobTemplate** | **string** |  | 
**PaymentDetails** | [**PaymentDetails**](PaymentDetails.md) |  | 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewSubmitMultiDocWithTemplateParams

`func NewSubmitMultiDocWithTemplateParams(items []SubmitMultiDocWithTemplateParamsRequestItemsInner, jobTemplate string, paymentDetails PaymentDetails, ) *SubmitMultiDocWithTemplateParams`

NewSubmitMultiDocWithTemplateParams instantiates a new SubmitMultiDocWithTemplateParams object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSubmitMultiDocWithTemplateParamsWithDefaults

`func NewSubmitMultiDocWithTemplateParamsWithDefaults() *SubmitMultiDocWithTemplateParams`

NewSubmitMultiDocWithTemplateParamsWithDefaults instantiates a new SubmitMultiDocWithTemplateParams object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetItems

`func (o *SubmitMultiDocWithTemplateParams) GetItems() []SubmitMultiDocWithTemplateParamsRequestItemsInner`

GetItems returns the Items field if non-nil, zero value otherwise.

### GetItemsOk

`func (o *SubmitMultiDocWithTemplateParams) GetItemsOk() (*[]SubmitMultiDocWithTemplateParamsRequestItemsInner, bool)`

GetItemsOk returns a tuple with the Items field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetItems

`func (o *SubmitMultiDocWithTemplateParams) SetItems(v []SubmitMultiDocWithTemplateParamsRequestItemsInner)`

SetItems sets Items field to given value.


### GetJobTemplate

`func (o *SubmitMultiDocWithTemplateParams) GetJobTemplate() string`

GetJobTemplate returns the JobTemplate field if non-nil, zero value otherwise.

### GetJobTemplateOk

`func (o *SubmitMultiDocWithTemplateParams) GetJobTemplateOk() (*string, bool)`

GetJobTemplateOk returns a tuple with the JobTemplate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJobTemplate

`func (o *SubmitMultiDocWithTemplateParams) SetJobTemplate(v string)`

SetJobTemplate sets JobTemplate field to given value.


### GetPaymentDetails

`func (o *SubmitMultiDocWithTemplateParams) GetPaymentDetails() PaymentDetails`

GetPaymentDetails returns the PaymentDetails field if non-nil, zero value otherwise.

### GetPaymentDetailsOk

`func (o *SubmitMultiDocWithTemplateParams) GetPaymentDetailsOk() (*PaymentDetails, bool)`

GetPaymentDetailsOk returns a tuple with the PaymentDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaymentDetails

`func (o *SubmitMultiDocWithTemplateParams) SetPaymentDetails(v PaymentDetails)`

SetPaymentDetails sets PaymentDetails field to given value.


### GetTags

`func (o *SubmitMultiDocWithTemplateParams) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *SubmitMultiDocWithTemplateParams) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *SubmitMultiDocWithTemplateParams) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *SubmitMultiDocWithTemplateParams) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


