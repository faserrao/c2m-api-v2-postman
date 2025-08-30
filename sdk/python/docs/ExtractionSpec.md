# ExtractionSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**start_page** | **int** |  | 
**end_page** | **int** |  | 
**address_region** | [**AddressRegion**](AddressRegion.md) |  | 

## Example

```python
from c2m_api.models.extraction_spec import ExtractionSpec

# TODO update the JSON string below
json = "{}"
# create an instance of ExtractionSpec from a JSON string
extraction_spec_instance = ExtractionSpec.from_json(json)
# print the JSON string representation of the object
print(ExtractionSpec.to_json())

# convert the object into a dict
extraction_spec_dict = extraction_spec_instance.to_dict()
# create an instance of ExtractionSpec from a dict
extraction_spec_from_dict = ExtractionSpec.from_dict(extraction_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


