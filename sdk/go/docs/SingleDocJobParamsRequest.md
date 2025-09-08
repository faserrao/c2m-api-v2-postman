# SingleDocJobParamsRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentSourceIdentifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**RecipientAddressSources** | [**[]RecipientAddressSource**](RecipientAddressSource.md) |  | 
**JobOptions** | [**JobOptions**](JobOptions.md) |  | 
**PaymentDetails** | Pointer to [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewSingleDocJobParamsRequest

`func NewSingleDocJobParamsRequest(documentSourceIdentifier DocumentSourceIdentifier, recipientAddressSources []RecipientAddressSource, jobOptions JobOptions, ) *SingleDocJobParamsRequest`

NewSingleDocJobParamsRequest instantiates a new SingleDocJobParamsRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSingleDocJobParamsRequestWithDefaults

`func NewSingleDocJobParamsRequestWithDefaults() *SingleDocJobParamsRequest`

NewSingleDocJobParamsRequestWithDefaults instantiates a new SingleDocJobParamsRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentSourceIdentifier

`func (o *SingleDocJobParamsRequest) GetDocumentSourceIdentifier() DocumentSourceIdentifier`

GetDocumentSourceIdentifier returns the DocumentSourceIdentifier field if non-nil, zero value otherwise.

### GetDocumentSourceIdentifierOk

`func (o *SingleDocJobParamsRequest) GetDocumentSourceIdentifierOk() (*DocumentSourceIdentifier, bool)`

GetDocumentSourceIdentifierOk returns a tuple with the DocumentSourceIdentifier field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentSourceIdentifier

`func (o *SingleDocJobParamsRequest) SetDocumentSourceIdentifier(v DocumentSourceIdentifier)`

SetDocumentSourceIdentifier sets DocumentSourceIdentifier field to given value.


### GetRecipientAddressSources

`func (o *SingleDocJobParamsRequest) GetRecipientAddressSources() []RecipientAddressSource`

GetRecipientAddressSources returns the RecipientAddressSources field if non-nil, zero value otherwise.

### GetRecipientAddressSourcesOk

`func (o *SingleDocJobParamsRequest) GetRecipientAddressSourcesOk() (*[]RecipientAddressSource, bool)`

GetRecipientAddressSourcesOk returns a tuple with the RecipientAddressSources field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRecipientAddressSources

`func (o *SingleDocJobParamsRequest) SetRecipientAddressSources(v []RecipientAddressSource)`

SetRecipientAddressSources sets RecipientAddressSources field to given value.


### GetJobOptions

`func (o *SingleDocJobParamsRequest) GetJobOptions() JobOptions`

GetJobOptions returns the JobOptions field if non-nil, zero value otherwise.

### GetJobOptionsOk

`func (o *SingleDocJobParamsRequest) GetJobOptionsOk() (*JobOptions, bool)`

GetJobOptionsOk returns a tuple with the JobOptions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJobOptions

`func (o *SingleDocJobParamsRequest) SetJobOptions(v JobOptions)`

SetJobOptions sets JobOptions field to given value.


### GetPaymentDetails

`func (o *SingleDocJobParamsRequest) GetPaymentDetails() PaymentDetails`

GetPaymentDetails returns the PaymentDetails field if non-nil, zero value otherwise.

### GetPaymentDetailsOk

`func (o *SingleDocJobParamsRequest) GetPaymentDetailsOk() (*PaymentDetails, bool)`

GetPaymentDetailsOk returns a tuple with the PaymentDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaymentDetails

`func (o *SingleDocJobParamsRequest) SetPaymentDetails(v PaymentDetails)`

SetPaymentDetails sets PaymentDetails field to given value.

### HasPaymentDetails

`func (o *SingleDocJobParamsRequest) HasPaymentDetails() bool`

HasPaymentDetails returns a boolean if a field has been set.

### GetTags

`func (o *SingleDocJobParamsRequest) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *SingleDocJobParamsRequest) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *SingleDocJobParamsRequest) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *SingleDocJobParamsRequest) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


