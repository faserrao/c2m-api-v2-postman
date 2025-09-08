# SubmitSingleDocWithTemplateParamsRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**JobTemplate** | **string** |  | 
**PaymentDetails** | Pointer to [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewSubmitSingleDocWithTemplateParamsRequest

`func NewSubmitSingleDocWithTemplateParamsRequest(jobTemplate string, ) *SubmitSingleDocWithTemplateParamsRequest`

NewSubmitSingleDocWithTemplateParamsRequest instantiates a new SubmitSingleDocWithTemplateParamsRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSubmitSingleDocWithTemplateParamsRequestWithDefaults

`func NewSubmitSingleDocWithTemplateParamsRequestWithDefaults() *SubmitSingleDocWithTemplateParamsRequest`

NewSubmitSingleDocWithTemplateParamsRequestWithDefaults instantiates a new SubmitSingleDocWithTemplateParamsRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetJobTemplate

`func (o *SubmitSingleDocWithTemplateParamsRequest) GetJobTemplate() string`

GetJobTemplate returns the JobTemplate field if non-nil, zero value otherwise.

### GetJobTemplateOk

`func (o *SubmitSingleDocWithTemplateParamsRequest) GetJobTemplateOk() (*string, bool)`

GetJobTemplateOk returns a tuple with the JobTemplate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJobTemplate

`func (o *SubmitSingleDocWithTemplateParamsRequest) SetJobTemplate(v string)`

SetJobTemplate sets JobTemplate field to given value.


### GetPaymentDetails

`func (o *SubmitSingleDocWithTemplateParamsRequest) GetPaymentDetails() PaymentDetails`

GetPaymentDetails returns the PaymentDetails field if non-nil, zero value otherwise.

### GetPaymentDetailsOk

`func (o *SubmitSingleDocWithTemplateParamsRequest) GetPaymentDetailsOk() (*PaymentDetails, bool)`

GetPaymentDetailsOk returns a tuple with the PaymentDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaymentDetails

`func (o *SubmitSingleDocWithTemplateParamsRequest) SetPaymentDetails(v PaymentDetails)`

SetPaymentDetails sets PaymentDetails field to given value.

### HasPaymentDetails

`func (o *SubmitSingleDocWithTemplateParamsRequest) HasPaymentDetails() bool`

HasPaymentDetails returns a boolean if a field has been set.

### GetTags

`func (o *SubmitSingleDocWithTemplateParamsRequest) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *SubmitSingleDocWithTemplateParamsRequest) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *SubmitSingleDocWithTemplateParamsRequest) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *SubmitSingleDocWithTemplateParamsRequest) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


