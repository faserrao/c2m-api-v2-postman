# AchDetails

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**RoutingNumber** | **string** |  | 
**AccountNumber** | **string** |  | 
**CheckDigit** | **int32** |  | 

## Methods

### NewAchDetails

`func NewAchDetails(routingNumber string, accountNumber string, checkDigit int32, ) *AchDetails`

NewAchDetails instantiates a new AchDetails object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAchDetailsWithDefaults

`func NewAchDetailsWithDefaults() *AchDetails`

NewAchDetailsWithDefaults instantiates a new AchDetails object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetRoutingNumber

`func (o *AchDetails) GetRoutingNumber() string`

GetRoutingNumber returns the RoutingNumber field if non-nil, zero value otherwise.

### GetRoutingNumberOk

`func (o *AchDetails) GetRoutingNumberOk() (*string, bool)`

GetRoutingNumberOk returns a tuple with the RoutingNumber field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRoutingNumber

`func (o *AchDetails) SetRoutingNumber(v string)`

SetRoutingNumber sets RoutingNumber field to given value.


### GetAccountNumber

`func (o *AchDetails) GetAccountNumber() string`

GetAccountNumber returns the AccountNumber field if non-nil, zero value otherwise.

### GetAccountNumberOk

`func (o *AchDetails) GetAccountNumberOk() (*string, bool)`

GetAccountNumberOk returns a tuple with the AccountNumber field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAccountNumber

`func (o *AchDetails) SetAccountNumber(v string)`

SetAccountNumber sets AccountNumber field to given value.


### GetCheckDigit

`func (o *AchDetails) GetCheckDigit() int32`

GetCheckDigit returns the CheckDigit field if non-nil, zero value otherwise.

### GetCheckDigitOk

`func (o *AchDetails) GetCheckDigitOk() (*int32, bool)`

GetCheckDigitOk returns a tuple with the CheckDigit field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCheckDigit

`func (o *AchDetails) SetCheckDigit(v int32)`

SetCheckDigit sets CheckDigit field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


