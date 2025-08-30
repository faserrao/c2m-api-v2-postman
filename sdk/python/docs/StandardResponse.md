# StandardResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] 
**message** | **str** |  | [optional] 
**job_id** | **str** |  | [optional] 

## Example

```python
from c2m_api.models.standard_response import StandardResponse

# TODO update the JSON string below
json = "{}"
# create an instance of StandardResponse from a JSON string
standard_response_instance = StandardResponse.from_json(json)
# print the JSON string representation of the object
print(StandardResponse.to_json())

# convert the object into a dict
standard_response_dict = standard_response_instance.to_dict()
# create an instance of StandardResponse from a dict
standard_response_from_dict = StandardResponse.from_dict(standard_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


