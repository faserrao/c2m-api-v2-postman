# CreditCardDetails


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**card_type** | [**CardType**](CardType.md) |  | 
**card_number** | **str** |  | 
**expiration_date** | [**ExpirationDate**](ExpirationDate.md) |  | 
**cvv** | **int** |  | 

## Example

```python
from c2m_api.models.credit_card_details import CreditCardDetails

# TODO update the JSON string below
json = "{}"
# create an instance of CreditCardDetails from a JSON string
credit_card_details_instance = CreditCardDetails.from_json(json)
# print the JSON string representation of the object
print(CreditCardDetails.to_json())

# convert the object into a dict
credit_card_details_dict = credit_card_details_instance.to_dict()
# create an instance of CreditCardDetails from a dict
credit_card_details_from_dict = CreditCardDetails.from_dict(credit_card_details_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


