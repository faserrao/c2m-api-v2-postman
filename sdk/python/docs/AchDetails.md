# AchDetails


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**routing_number** | **str** |  | 
**account_number** | **str** |  | 
**check_digit** | **int** |  | 

## Example

```python
from c2m_api.models.ach_details import AchDetails

# TODO update the JSON string below
json = "{}"
# create an instance of AchDetails from a JSON string
ach_details_instance = AchDetails.from_json(json)
# print the JSON string representation of the object
print(AchDetails.to_json())

# convert the object into a dict
ach_details_dict = ach_details_instance.to_dict()
# create an instance of AchDetails from a dict
ach_details_from_dict = AchDetails.from_dict(ach_details_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


