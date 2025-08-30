# CreditCardPayment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**credit_card_details** | [**CreditCardDetails**](CreditCardDetails.md) |  | 

## Example

```python
from c2m_api.models.credit_card_payment import CreditCardPayment

# TODO update the JSON string below
json = "{}"
# create an instance of CreditCardPayment from a JSON string
credit_card_payment_instance = CreditCardPayment.from_json(json)
# print the JSON string representation of the object
print(CreditCardPayment.to_json())

# convert the object into a dict
credit_card_payment_dict = credit_card_payment_instance.to_dict()
# create an instance of CreditCardPayment from a dict
credit_card_payment_from_dict = CreditCardPayment.from_dict(credit_card_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


