# MergeMultiDocParamsRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentsToMerge** | [**[]DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**RecipientAddressSource** | [**RecipientAddressSource**](RecipientAddressSource.md) |  | 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewMergeMultiDocParamsRequest

`func NewMergeMultiDocParamsRequest(documentsToMerge []DocumentSourceIdentifier, recipientAddressSource RecipientAddressSource, ) *MergeMultiDocParamsRequest`

NewMergeMultiDocParamsRequest instantiates a new MergeMultiDocParamsRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMergeMultiDocParamsRequestWithDefaults

`func NewMergeMultiDocParamsRequestWithDefaults() *MergeMultiDocParamsRequest`

NewMergeMultiDocParamsRequestWithDefaults instantiates a new MergeMultiDocParamsRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentsToMerge

`func (o *MergeMultiDocParamsRequest) GetDocumentsToMerge() []DocumentSourceIdentifier`

GetDocumentsToMerge returns the DocumentsToMerge field if non-nil, zero value otherwise.

### GetDocumentsToMergeOk

`func (o *MergeMultiDocParamsRequest) GetDocumentsToMergeOk() (*[]DocumentSourceIdentifier, bool)`

GetDocumentsToMergeOk returns a tuple with the DocumentsToMerge field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentsToMerge

`func (o *MergeMultiDocParamsRequest) SetDocumentsToMerge(v []DocumentSourceIdentifier)`

SetDocumentsToMerge sets DocumentsToMerge field to given value.


### GetRecipientAddressSource

`func (o *MergeMultiDocParamsRequest) GetRecipientAddressSource() RecipientAddressSource`

GetRecipientAddressSource returns the RecipientAddressSource field if non-nil, zero value otherwise.

### GetRecipientAddressSourceOk

`func (o *MergeMultiDocParamsRequest) GetRecipientAddressSourceOk() (*RecipientAddressSource, bool)`

GetRecipientAddressSourceOk returns a tuple with the RecipientAddressSource field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRecipientAddressSource

`func (o *MergeMultiDocParamsRequest) SetRecipientAddressSource(v RecipientAddressSource)`

SetRecipientAddressSource sets RecipientAddressSource field to given value.


### GetTags

`func (o *MergeMultiDocParamsRequest) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *MergeMultiDocParamsRequest) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *MergeMultiDocParamsRequest) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *MergeMultiDocParamsRequest) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


