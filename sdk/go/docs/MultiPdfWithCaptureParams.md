# MultiPdfWithCaptureParams

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**AddressCapturePdfs** | [**[]AddressListPdf**](AddressListPdf.md) |  | 
**JobTemplate** | **string** |  | 
**PaymentDetails** | Pointer to [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**Tags** | Pointer to **[]string** |  | [optional] 

## Methods

### NewMultiPdfWithCaptureParams

`func NewMultiPdfWithCaptureParams(addressCapturePdfs []AddressListPdf, jobTemplate string, ) *MultiPdfWithCaptureParams`

NewMultiPdfWithCaptureParams instantiates a new MultiPdfWithCaptureParams object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMultiPdfWithCaptureParamsWithDefaults

`func NewMultiPdfWithCaptureParamsWithDefaults() *MultiPdfWithCaptureParams`

NewMultiPdfWithCaptureParamsWithDefaults instantiates a new MultiPdfWithCaptureParams object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetAddressCapturePdfs

`func (o *MultiPdfWithCaptureParams) GetAddressCapturePdfs() []AddressListPdf`

GetAddressCapturePdfs returns the AddressCapturePdfs field if non-nil, zero value otherwise.

### GetAddressCapturePdfsOk

`func (o *MultiPdfWithCaptureParams) GetAddressCapturePdfsOk() (*[]AddressListPdf, bool)`

GetAddressCapturePdfsOk returns a tuple with the AddressCapturePdfs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAddressCapturePdfs

`func (o *MultiPdfWithCaptureParams) SetAddressCapturePdfs(v []AddressListPdf)`

SetAddressCapturePdfs sets AddressCapturePdfs field to given value.


### GetJobTemplate

`func (o *MultiPdfWithCaptureParams) GetJobTemplate() string`

GetJobTemplate returns the JobTemplate field if non-nil, zero value otherwise.

### GetJobTemplateOk

`func (o *MultiPdfWithCaptureParams) GetJobTemplateOk() (*string, bool)`

GetJobTemplateOk returns a tuple with the JobTemplate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJobTemplate

`func (o *MultiPdfWithCaptureParams) SetJobTemplate(v string)`

SetJobTemplate sets JobTemplate field to given value.


### GetPaymentDetails

`func (o *MultiPdfWithCaptureParams) GetPaymentDetails() PaymentDetails`

GetPaymentDetails returns the PaymentDetails field if non-nil, zero value otherwise.

### GetPaymentDetailsOk

`func (o *MultiPdfWithCaptureParams) GetPaymentDetailsOk() (*PaymentDetails, bool)`

GetPaymentDetailsOk returns a tuple with the PaymentDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaymentDetails

`func (o *MultiPdfWithCaptureParams) SetPaymentDetails(v PaymentDetails)`

SetPaymentDetails sets PaymentDetails field to given value.

### HasPaymentDetails

`func (o *MultiPdfWithCaptureParams) HasPaymentDetails() bool`

HasPaymentDetails returns a boolean if a field has been set.

### GetTags

`func (o *MultiPdfWithCaptureParams) GetTags() []string`

GetTags returns the Tags field if non-nil, zero value otherwise.

### GetTagsOk

`func (o *MultiPdfWithCaptureParams) GetTagsOk() (*[]string, bool)`

GetTagsOk returns a tuple with the Tags field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTags

`func (o *MultiPdfWithCaptureParams) SetTags(v []string)`

SetTags sets Tags field to given value.

### HasTags

`func (o *MultiPdfWithCaptureParams) HasTags() bool`

HasTags returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


