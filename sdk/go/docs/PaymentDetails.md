# PaymentDetails

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**CreditCardDetails** | [**CreditCardDetails**](CreditCardDetails.md) |  | 
**InvoiceDetails** | [**InvoiceDetails**](InvoiceDetails.md) |  | 
**AchDetails** | [**AchDetails**](AchDetails.md) |  | 
**CreditAmount** | [**CreditAmount**](CreditAmount.md) |  | 
**ApplePaymentDetails** | **map[string]interface{}** |  | 
**GooglePaymentDetails** | **map[string]interface{}** |  | 

## Methods

### NewPaymentDetails

`func NewPaymentDetails(creditCardDetails CreditCardDetails, invoiceDetails InvoiceDetails, achDetails AchDetails, creditAmount CreditAmount, applePaymentDetails map[string]interface{}, googlePaymentDetails map[string]interface{}, ) *PaymentDetails`

NewPaymentDetails instantiates a new PaymentDetails object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewPaymentDetailsWithDefaults

`func NewPaymentDetailsWithDefaults() *PaymentDetails`

NewPaymentDetailsWithDefaults instantiates a new PaymentDetails object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetCreditCardDetails

`func (o *PaymentDetails) GetCreditCardDetails() CreditCardDetails`

GetCreditCardDetails returns the CreditCardDetails field if non-nil, zero value otherwise.

### GetCreditCardDetailsOk

`func (o *PaymentDetails) GetCreditCardDetailsOk() (*CreditCardDetails, bool)`

GetCreditCardDetailsOk returns a tuple with the CreditCardDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreditCardDetails

`func (o *PaymentDetails) SetCreditCardDetails(v CreditCardDetails)`

SetCreditCardDetails sets CreditCardDetails field to given value.


### GetInvoiceDetails

`func (o *PaymentDetails) GetInvoiceDetails() InvoiceDetails`

GetInvoiceDetails returns the InvoiceDetails field if non-nil, zero value otherwise.

### GetInvoiceDetailsOk

`func (o *PaymentDetails) GetInvoiceDetailsOk() (*InvoiceDetails, bool)`

GetInvoiceDetailsOk returns a tuple with the InvoiceDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetInvoiceDetails

`func (o *PaymentDetails) SetInvoiceDetails(v InvoiceDetails)`

SetInvoiceDetails sets InvoiceDetails field to given value.


### GetAchDetails

`func (o *PaymentDetails) GetAchDetails() AchDetails`

GetAchDetails returns the AchDetails field if non-nil, zero value otherwise.

### GetAchDetailsOk

`func (o *PaymentDetails) GetAchDetailsOk() (*AchDetails, bool)`

GetAchDetailsOk returns a tuple with the AchDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAchDetails

`func (o *PaymentDetails) SetAchDetails(v AchDetails)`

SetAchDetails sets AchDetails field to given value.


### GetCreditAmount

`func (o *PaymentDetails) GetCreditAmount() CreditAmount`

GetCreditAmount returns the CreditAmount field if non-nil, zero value otherwise.

### GetCreditAmountOk

`func (o *PaymentDetails) GetCreditAmountOk() (*CreditAmount, bool)`

GetCreditAmountOk returns a tuple with the CreditAmount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreditAmount

`func (o *PaymentDetails) SetCreditAmount(v CreditAmount)`

SetCreditAmount sets CreditAmount field to given value.


### GetApplePaymentDetails

`func (o *PaymentDetails) GetApplePaymentDetails() map[string]interface{}`

GetApplePaymentDetails returns the ApplePaymentDetails field if non-nil, zero value otherwise.

### GetApplePaymentDetailsOk

`func (o *PaymentDetails) GetApplePaymentDetailsOk() (*map[string]interface{}, bool)`

GetApplePaymentDetailsOk returns a tuple with the ApplePaymentDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApplePaymentDetails

`func (o *PaymentDetails) SetApplePaymentDetails(v map[string]interface{})`

SetApplePaymentDetails sets ApplePaymentDetails field to given value.


### GetGooglePaymentDetails

`func (o *PaymentDetails) GetGooglePaymentDetails() map[string]interface{}`

GetGooglePaymentDetails returns the GooglePaymentDetails field if non-nil, zero value otherwise.

### GetGooglePaymentDetailsOk

`func (o *PaymentDetails) GetGooglePaymentDetailsOk() (*map[string]interface{}, bool)`

GetGooglePaymentDetailsOk returns a tuple with the GooglePaymentDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetGooglePaymentDetails

`func (o *PaymentDetails) SetGooglePaymentDetails(v map[string]interface{})`

SetGooglePaymentDetails sets GooglePaymentDetails field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


