# GooglePayPayment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**google_payment_details** | **object** |  | 

## Example

```python
from c2m_api.models.google_pay_payment import GooglePayPayment

# TODO update the JSON string below
json = "{}"
# create an instance of GooglePayPayment from a JSON string
google_pay_payment_instance = GooglePayPayment.from_json(json)
# print the JSON string representation of the object
print(GooglePayPayment.to_json())

# convert the object into a dict
google_pay_payment_dict = google_pay_payment_instance.to_dict()
# create an instance of GooglePayPayment from a dict
google_pay_payment_from_dict = GooglePayPayment.from_dict(google_pay_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


