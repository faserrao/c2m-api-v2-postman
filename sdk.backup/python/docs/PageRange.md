# PageRange


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**start_page** | **int** |  | 
**end_page** | **int** |  | 

## Example

```python
from c2m_api.models.page_range import PageRange

# TODO update the JSON string below
json = "{}"
# create an instance of PageRange from a JSON string
page_range_instance = PageRange.from_json(json)
# print the JSON string representation of the object
print(PageRange.to_json())

# convert the object into a dict
page_range_dict = page_range_instance.to_dict()
# create an instance of PageRange from a dict
page_range_from_dict = PageRange.from_dict(page_range_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


