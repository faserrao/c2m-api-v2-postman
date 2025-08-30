# MergeMultiDocParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**documents_to_merge** | [**List[DocumentSourceIdentifier]**](DocumentSourceIdentifier.md) |  | 
**recipient_address_source** | [**RecipientAddressSource**](RecipientAddressSource.md) |  | 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.merge_multi_doc_params import MergeMultiDocParams

# TODO update the JSON string below
json = "{}"
# create an instance of MergeMultiDocParams from a JSON string
merge_multi_doc_params_instance = MergeMultiDocParams.from_json(json)
# print the JSON string representation of the object
print(MergeMultiDocParams.to_json())

# convert the object into a dict
merge_multi_doc_params_dict = merge_multi_doc_params_instance.to_dict()
# create an instance of MergeMultiDocParams from a dict
merge_multi_doc_params_from_dict = MergeMultiDocParams.from_dict(merge_multi_doc_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


