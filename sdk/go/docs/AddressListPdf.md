# AddressListPdf

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentSourceIdentifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**AddressListRegion** | **string** |  | 
**Delimiter** | Pointer to **string** |  | [optional] 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewAddressListPdf

`func NewAddressListPdf(documentSourceIdentifier DocumentSourceIdentifier, addressListRegion string, ) *AddressListPdf`

NewAddressListPdf instantiates a new AddressListPdf object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAddressListPdfWithDefaults

`func NewAddressListPdfWithDefaults() *AddressListPdf`

NewAddressListPdfWithDefaults instantiates a new AddressListPdf object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentSourceIdentifier

`func (o *AddressListPdf) GetDocumentSourceIdentifier() DocumentSourceIdentifier`

GetDocumentSourceIdentifier returns the DocumentSourceIdentifier field if non-nil, zero value otherwise.

### GetDocumentSourceIdentifierOk

`func (o *AddressListPdf) GetDocumentSourceIdentifierOk() (*DocumentSourceIdentifier, bool)`

GetDocumentSourceIdentifierOk returns a tuple with the DocumentSourceIdentifier field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentSourceIdentifier

`func (o *AddressListPdf) SetDocumentSourceIdentifier(v DocumentSourceIdentifier)`

SetDocumentSourceIdentifier sets DocumentSourceIdentifier field to given value.


### GetAddressListRegion

`func (o *AddressListPdf) GetAddressListRegion() string`

GetAddressListRegion returns the AddressListRegion field if non-nil, zero value otherwise.

### GetAddressListRegionOk

`func (o *AddressListPdf) GetAddressListRegionOk() (*string, bool)`

GetAddressListRegionOk returns a tuple with the AddressListRegion field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAddressListRegion

`func (o *AddressListPdf) SetAddressListRegion(v string)`

SetAddressListRegion sets AddressListRegion field to given value.


### GetDelimiter

`func (o *AddressListPdf) GetDelimiter() string`

GetDelimiter returns the Delimiter field if non-nil, zero value otherwise.

### GetDelimiterOk

`func (o *AddressListPdf) GetDelimiterOk() (*string, bool)`

GetDelimiterOk returns a tuple with the Delimiter field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDelimiter

`func (o *AddressListPdf) SetDelimiter(v string)`

SetDelimiter sets Delimiter field to given value.

### HasDelimiter

`func (o *AddressListPdf) HasDelimiter() bool`

HasDelimiter returns a boolean if a field has been set.

### GetTags

`func (o *AddressListPdf) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *AddressListPdf) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *AddressListPdf) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *AddressListPdf) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


