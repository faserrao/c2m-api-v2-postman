# ApplePayPayment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**apple_payment_details** | **object** |  | 

## Example

```python
from c2m_api.models.apple_pay_payment import ApplePayPayment

# TODO update the JSON string below
json = "{}"
# create an instance of ApplePayPayment from a JSON string
apple_pay_payment_instance = ApplePayPayment.from_json(json)
# print the JSON string representation of the object
print(ApplePayPayment.to_json())

# convert the object into a dict
apple_pay_payment_dict = apple_pay_payment_instance.to_dict()
# create an instance of ApplePayPayment from a dict
apple_pay_payment_from_dict = ApplePayPayment.from_dict(apple_pay_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


