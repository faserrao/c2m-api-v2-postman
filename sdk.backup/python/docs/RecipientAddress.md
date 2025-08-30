# RecipientAddress


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** |  | 
**last_name** | **str** |  | 
**address1** | **str** |  | 
**city** | **str** |  | 
**state** | **str** |  | 
**zip** | **str** |  | 
**country** | **str** |  | 
**nick_name** | **str** |  | [optional] 
**address2** | **str** |  | [optional] 
**address3** | **str** |  | [optional] 
**phone_number** | **str** |  | [optional] 

## Example

```python
from c2m_api.models.recipient_address import RecipientAddress

# TODO update the JSON string below
json = "{}"
# create an instance of RecipientAddress from a JSON string
recipient_address_instance = RecipientAddress.from_json(json)
# print the JSON string representation of the object
print(RecipientAddress.to_json())

# convert the object into a dict
recipient_address_dict = recipient_address_instance.to_dict()
# create an instance of RecipientAddress from a dict
recipient_address_from_dict = RecipientAddress.from_dict(recipient_address_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


