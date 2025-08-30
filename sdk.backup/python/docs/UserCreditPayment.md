# UserCreditPayment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**credit_amount** | [**CreditAmount**](CreditAmount.md) |  | 

## Example

```python
from c2m_api.models.user_credit_payment import UserCreditPayment

# TODO update the JSON string below
json = "{}"
# create an instance of UserCreditPayment from a JSON string
user_credit_payment_instance = UserCreditPayment.from_json(json)
# print the JSON string representation of the object
print(UserCreditPayment.to_json())

# convert the object into a dict
user_credit_payment_dict = user_credit_payment_instance.to_dict()
# create an instance of UserCreditPayment from a dict
user_credit_payment_from_dict = UserCreditPayment.from_dict(user_credit_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


