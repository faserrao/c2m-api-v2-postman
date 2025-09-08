# MergeMultiDocWithTemplateParamsRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentsToMerge** | [**[]DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**RecipientAddressSource** | [**RecipientAddressSource**](RecipientAddressSource.md) |  | 
**JobTemplate** | **string** |  | 
**PaymentDetails** | Pointer to [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewMergeMultiDocWithTemplateParamsRequest

`func NewMergeMultiDocWithTemplateParamsRequest(documentsToMerge []DocumentSourceIdentifier, recipientAddressSource RecipientAddressSource, jobTemplate string, ) *MergeMultiDocWithTemplateParamsRequest`

NewMergeMultiDocWithTemplateParamsRequest instantiates a new MergeMultiDocWithTemplateParamsRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMergeMultiDocWithTemplateParamsRequestWithDefaults

`func NewMergeMultiDocWithTemplateParamsRequestWithDefaults() *MergeMultiDocWithTemplateParamsRequest`

NewMergeMultiDocWithTemplateParamsRequestWithDefaults instantiates a new MergeMultiDocWithTemplateParamsRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentsToMerge

`func (o *MergeMultiDocWithTemplateParamsRequest) GetDocumentsToMerge() []DocumentSourceIdentifier`

GetDocumentsToMerge returns the DocumentsToMerge field if non-nil, zero value otherwise.

### GetDocumentsToMergeOk

`func (o *MergeMultiDocWithTemplateParamsRequest) GetDocumentsToMergeOk() (*[]DocumentSourceIdentifier, bool)`

GetDocumentsToMergeOk returns a tuple with the DocumentsToMerge field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentsToMerge

`func (o *MergeMultiDocWithTemplateParamsRequest) SetDocumentsToMerge(v []DocumentSourceIdentifier)`

SetDocumentsToMerge sets DocumentsToMerge field to given value.


### GetRecipientAddressSource

`func (o *MergeMultiDocWithTemplateParamsRequest) GetRecipientAddressSource() RecipientAddressSource`

GetRecipientAddressSource returns the RecipientAddressSource field if non-nil, zero value otherwise.

### GetRecipientAddressSourceOk

`func (o *MergeMultiDocWithTemplateParamsRequest) GetRecipientAddressSourceOk() (*RecipientAddressSource, bool)`

GetRecipientAddressSourceOk returns a tuple with the RecipientAddressSource field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRecipientAddressSource

`func (o *MergeMultiDocWithTemplateParamsRequest) SetRecipientAddressSource(v RecipientAddressSource)`

SetRecipientAddressSource sets RecipientAddressSource field to given value.


### GetJobTemplate

`func (o *MergeMultiDocWithTemplateParamsRequest) GetJobTemplate() string`

GetJobTemplate returns the JobTemplate field if non-nil, zero value otherwise.

### GetJobTemplateOk

`func (o *MergeMultiDocWithTemplateParamsRequest) GetJobTemplateOk() (*string, bool)`

GetJobTemplateOk returns a tuple with the JobTemplate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJobTemplate

`func (o *MergeMultiDocWithTemplateParamsRequest) SetJobTemplate(v string)`

SetJobTemplate sets JobTemplate field to given value.


### GetPaymentDetails

`func (o *MergeMultiDocWithTemplateParamsRequest) GetPaymentDetails() PaymentDetails`

GetPaymentDetails returns the PaymentDetails field if non-nil, zero value otherwise.

### GetPaymentDetailsOk

`func (o *MergeMultiDocWithTemplateParamsRequest) GetPaymentDetailsOk() (*PaymentDetails, bool)`

GetPaymentDetailsOk returns a tuple with the PaymentDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaymentDetails

`func (o *MergeMultiDocWithTemplateParamsRequest) SetPaymentDetails(v PaymentDetails)`

SetPaymentDetails sets PaymentDetails field to given value.

### HasPaymentDetails

`func (o *MergeMultiDocWithTemplateParamsRequest) HasPaymentDetails() bool`

HasPaymentDetails returns a boolean if a field has been set.

### GetTags

`func (o *MergeMultiDocWithTemplateParamsRequest) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *MergeMultiDocWithTemplateParamsRequest) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *MergeMultiDocWithTemplateParamsRequest) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *MergeMultiDocWithTemplateParamsRequest) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


