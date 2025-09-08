# MergeMultiDocWithTemplateParams

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentsToMerge** | [**[]DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**RecipientAddressSource** | [**RecipientAddressSource**](RecipientAddressSource.md) |  | 
**JobTemplate** | **string** |  | 
**PaymentDetails** | Pointer to [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewMergeMultiDocWithTemplateParams

`func NewMergeMultiDocWithTemplateParams(documentsToMerge []DocumentSourceIdentifier, recipientAddressSource RecipientAddressSource, jobTemplate string, ) *MergeMultiDocWithTemplateParams`

NewMergeMultiDocWithTemplateParams instantiates a new MergeMultiDocWithTemplateParams object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMergeMultiDocWithTemplateParamsWithDefaults

`func NewMergeMultiDocWithTemplateParamsWithDefaults() *MergeMultiDocWithTemplateParams`

NewMergeMultiDocWithTemplateParamsWithDefaults instantiates a new MergeMultiDocWithTemplateParams object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentsToMerge

`func (o *MergeMultiDocWithTemplateParams) GetDocumentsToMerge() []DocumentSourceIdentifier`

GetDocumentsToMerge returns the DocumentsToMerge field if non-nil, zero value otherwise.

### GetDocumentsToMergeOk

`func (o *MergeMultiDocWithTemplateParams) GetDocumentsToMergeOk() (*[]DocumentSourceIdentifier, bool)`

GetDocumentsToMergeOk returns a tuple with the DocumentsToMerge field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentsToMerge

`func (o *MergeMultiDocWithTemplateParams) SetDocumentsToMerge(v []DocumentSourceIdentifier)`

SetDocumentsToMerge sets DocumentsToMerge field to given value.


### GetRecipientAddressSource

`func (o *MergeMultiDocWithTemplateParams) GetRecipientAddressSource() RecipientAddressSource`

GetRecipientAddressSource returns the RecipientAddressSource field if non-nil, zero value otherwise.

### GetRecipientAddressSourceOk

`func (o *MergeMultiDocWithTemplateParams) GetRecipientAddressSourceOk() (*RecipientAddressSource, bool)`

GetRecipientAddressSourceOk returns a tuple with the RecipientAddressSource field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRecipientAddressSource

`func (o *MergeMultiDocWithTemplateParams) SetRecipientAddressSource(v RecipientAddressSource)`

SetRecipientAddressSource sets RecipientAddressSource field to given value.


### GetJobTemplate

`func (o *MergeMultiDocWithTemplateParams) GetJobTemplate() string`

GetJobTemplate returns the JobTemplate field if non-nil, zero value otherwise.

### GetJobTemplateOk

`func (o *MergeMultiDocWithTemplateParams) GetJobTemplateOk() (*string, bool)`

GetJobTemplateOk returns a tuple with the JobTemplate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJobTemplate

`func (o *MergeMultiDocWithTemplateParams) SetJobTemplate(v string)`

SetJobTemplate sets JobTemplate field to given value.


### GetPaymentDetails

`func (o *MergeMultiDocWithTemplateParams) GetPaymentDetails() PaymentDetails`

GetPaymentDetails returns the PaymentDetails field if non-nil, zero value otherwise.

### GetPaymentDetailsOk

`func (o *MergeMultiDocWithTemplateParams) GetPaymentDetailsOk() (*PaymentDetails, bool)`

GetPaymentDetailsOk returns a tuple with the PaymentDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaymentDetails

`func (o *MergeMultiDocWithTemplateParams) SetPaymentDetails(v PaymentDetails)`

SetPaymentDetails sets PaymentDetails field to given value.

### HasPaymentDetails

`func (o *MergeMultiDocWithTemplateParams) HasPaymentDetails() bool`

HasPaymentDetails returns a boolean if a field has been set.

### GetTags

`func (o *MergeMultiDocWithTemplateParams) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *MergeMultiDocWithTemplateParams) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *MergeMultiDocWithTemplateParams) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *MergeMultiDocWithTemplateParams) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


