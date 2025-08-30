# PaymentDetails


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**credit_card_details** | [**CreditCardDetails**](CreditCardDetails.md) |  | 
**invoice_details** | [**InvoiceDetails**](InvoiceDetails.md) |  | 
**ach_details** | [**AchDetails**](AchDetails.md) |  | 
**credit_amount** | [**CreditAmount**](CreditAmount.md) |  | 
**apple_payment_details** | **object** |  | 
**google_payment_details** | **object** |  | 

## Example

```python
from c2m_api.models.payment_details import PaymentDetails

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentDetails from a JSON string
payment_details_instance = PaymentDetails.from_json(json)
# print the JSON string representation of the object
print(PaymentDetails.to_json())

# convert the object into a dict
payment_details_dict = payment_details_instance.to_dict()
# create an instance of PaymentDetails from a dict
payment_details_from_dict = PaymentDetails.from_dict(payment_details_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


