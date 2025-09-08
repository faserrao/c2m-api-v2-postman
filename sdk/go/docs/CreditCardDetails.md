# CreditCardDetails

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**CardType** | [**CardType**](CardType.md) |  | 
**CardNumber** | **string** |  | 
**ExpirationDate** | [**ExpirationDate**](ExpirationDate.md) |  | 
**Cvv** | **int32** |  | 

## Methods

### NewCreditCardDetails

`func NewCreditCardDetails(cardType CardType, cardNumber string, expirationDate ExpirationDate, cvv int32, ) *CreditCardDetails`

NewCreditCardDetails instantiates a new CreditCardDetails object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCreditCardDetailsWithDefaults

`func NewCreditCardDetailsWithDefaults() *CreditCardDetails`

NewCreditCardDetailsWithDefaults instantiates a new CreditCardDetails object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetCardType

`func (o *CreditCardDetails) GetCardType() CardType`

GetCardType returns the CardType field if non-nil, zero value otherwise.

### GetCardTypeOk

`func (o *CreditCardDetails) GetCardTypeOk() (*CardType, bool)`

GetCardTypeOk returns a tuple with the CardType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCardType

`func (o *CreditCardDetails) SetCardType(v CardType)`

SetCardType sets CardType field to given value.


### GetCardNumber

`func (o *CreditCardDetails) GetCardNumber() string`

GetCardNumber returns the CardNumber field if non-nil, zero value otherwise.

### GetCardNumberOk

`func (o *CreditCardDetails) GetCardNumberOk() (*string, bool)`

GetCardNumberOk returns a tuple with the CardNumber field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCardNumber

`func (o *CreditCardDetails) SetCardNumber(v string)`

SetCardNumber sets CardNumber field to given value.


### GetExpirationDate

`func (o *CreditCardDetails) GetExpirationDate() ExpirationDate`

GetExpirationDate returns the ExpirationDate field if non-nil, zero value otherwise.

### GetExpirationDateOk

`func (o *CreditCardDetails) GetExpirationDateOk() (*ExpirationDate, bool)`

GetExpirationDateOk returns a tuple with the ExpirationDate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExpirationDate

`func (o *CreditCardDetails) SetExpirationDate(v ExpirationDate)`

SetExpirationDate sets ExpirationDate field to given value.


### GetCvv

`func (o *CreditCardDetails) GetCvv() int32`

GetCvv returns the Cvv field if non-nil, zero value otherwise.

### GetCvvOk

`func (o *CreditCardDetails) GetCvvOk() (*int32, bool)`

GetCvvOk returns a tuple with the Cvv field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCvv

`func (o *CreditCardDetails) SetCvv(v int32)`

SetCvv sets Cvv field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


