# MergeMultiDocParams

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentsToMerge** | [**[]DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**RecipientAddressSource** | [**RecipientAddressSource**](RecipientAddressSource.md) |  | 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewMergeMultiDocParams

`func NewMergeMultiDocParams(documentsToMerge []DocumentSourceIdentifier, recipientAddressSource RecipientAddressSource, ) *MergeMultiDocParams`

NewMergeMultiDocParams instantiates a new MergeMultiDocParams object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMergeMultiDocParamsWithDefaults

`func NewMergeMultiDocParamsWithDefaults() *MergeMultiDocParams`

NewMergeMultiDocParamsWithDefaults instantiates a new MergeMultiDocParams object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentsToMerge

`func (o *MergeMultiDocParams) GetDocumentsToMerge() []DocumentSourceIdentifier`

GetDocumentsToMerge returns the DocumentsToMerge field if non-nil, zero value otherwise.

### GetDocumentsToMergeOk

`func (o *MergeMultiDocParams) GetDocumentsToMergeOk() (*[]DocumentSourceIdentifier, bool)`

GetDocumentsToMergeOk returns a tuple with the DocumentsToMerge field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentsToMerge

`func (o *MergeMultiDocParams) SetDocumentsToMerge(v []DocumentSourceIdentifier)`

SetDocumentsToMerge sets DocumentsToMerge field to given value.


### GetRecipientAddressSource

`func (o *MergeMultiDocParams) GetRecipientAddressSource() RecipientAddressSource`

GetRecipientAddressSource returns the RecipientAddressSource field if non-nil, zero value otherwise.

### GetRecipientAddressSourceOk

`func (o *MergeMultiDocParams) GetRecipientAddressSourceOk() (*RecipientAddressSource, bool)`

GetRecipientAddressSourceOk returns a tuple with the RecipientAddressSource field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRecipientAddressSource

`func (o *MergeMultiDocParams) SetRecipientAddressSource(v RecipientAddressSource)`

SetRecipientAddressSource sets RecipientAddressSource field to given value.


### GetTags

`func (o *MergeMultiDocParams) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *MergeMultiDocParams) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *MergeMultiDocParams) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *MergeMultiDocParams) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


