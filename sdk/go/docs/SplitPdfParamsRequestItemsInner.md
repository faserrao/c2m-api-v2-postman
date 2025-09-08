# SplitPdfParamsRequestItemsInner

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**PageRange** | [**PageRange**](PageRange.md) |  | 
**RecipientAddressSources** | [**[]RecipientAddressSource**](RecipientAddressSource.md) |  | 

## Methods

### NewSplitPdfParamsRequestItemsInner

`func NewSplitPdfParamsRequestItemsInner(pageRange PageRange, recipientAddressSources []RecipientAddressSource, ) *SplitPdfParamsRequestItemsInner`

NewSplitPdfParamsRequestItemsInner instantiates a new SplitPdfParamsRequestItemsInner object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSplitPdfParamsRequestItemsInnerWithDefaults

`func NewSplitPdfParamsRequestItemsInnerWithDefaults() *SplitPdfParamsRequestItemsInner`

NewSplitPdfParamsRequestItemsInnerWithDefaults instantiates a new SplitPdfParamsRequestItemsInner object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetPageRange

`func (o *SplitPdfParamsRequestItemsInner) GetPageRange() PageRange`

GetPageRange returns the PageRange field if non-nil, zero value otherwise.

### GetPageRangeOk

`func (o *SplitPdfParamsRequestItemsInner) GetPageRangeOk() (*PageRange, bool)`

GetPageRangeOk returns a tuple with the PageRange field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPageRange

`func (o *SplitPdfParamsRequestItemsInner) SetPageRange(v PageRange)`

SetPageRange sets PageRange field to given value.


### GetRecipientAddressSources

`func (o *SplitPdfParamsRequestItemsInner) GetRecipientAddressSources() []RecipientAddressSource`

GetRecipientAddressSources returns the RecipientAddressSources field if non-nil, zero value otherwise.

### GetRecipientAddressSourcesOk

`func (o *SplitPdfParamsRequestItemsInner) GetRecipientAddressSourcesOk() (*[]RecipientAddressSource, bool)`

GetRecipientAddressSourcesOk returns a tuple with the RecipientAddressSources field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRecipientAddressSources

`func (o *SplitPdfParamsRequestItemsInner) SetRecipientAddressSources(v []RecipientAddressSource)`

SetRecipientAddressSources sets RecipientAddressSources field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


