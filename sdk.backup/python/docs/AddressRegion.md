# AddressRegion


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**x** | **float** |  | 
**y** | **float** |  | 
**width** | **float** |  | 
**height** | **float** |  | 
**page_offset** | **int** |  | 

## Example

```python
from c2m_api.models.address_region import AddressRegion

# TODO update the JSON string below
json = "{}"
# create an instance of AddressRegion from a JSON string
address_region_instance = AddressRegion.from_json(json)
# print the JSON string representation of the object
print(AddressRegion.to_json())

# convert the object into a dict
address_region_dict = address_region_instance.to_dict()
# create an instance of AddressRegion from a dict
address_region_from_dict = AddressRegion.from_dict(address_region_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


