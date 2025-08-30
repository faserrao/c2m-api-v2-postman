# AchPayment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ach_details** | [**AchDetails**](AchDetails.md) |  | 

## Example

```python
from c2m_api.models.ach_payment import AchPayment

# TODO update the JSON string below
json = "{}"
# create an instance of AchPayment from a JSON string
ach_payment_instance = AchPayment.from_json(json)
# print the JSON string representation of the object
print(AchPayment.to_json())

# convert the object into a dict
ach_payment_dict = ach_payment_instance.to_dict()
# create an instance of AchPayment from a dict
ach_payment_from_dict = AchPayment.from_dict(ach_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


