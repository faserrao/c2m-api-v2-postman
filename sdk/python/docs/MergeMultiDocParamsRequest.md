# MergeMultiDocParamsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**documents_to_merge** | [**List[DocumentSourceIdentifier]**](DocumentSourceIdentifier.md) |  | 
**recipient_address_source** | [**RecipientAddressSource**](RecipientAddressSource.md) |  | 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.merge_multi_doc_params_request import MergeMultiDocParamsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MergeMultiDocParamsRequest from a JSON string
merge_multi_doc_params_request_instance = MergeMultiDocParamsRequest.from_json(json)
# print the JSON string representation of the object
print(MergeMultiDocParamsRequest.to_json())

# convert the object into a dict
merge_multi_doc_params_request_dict = merge_multi_doc_params_request_instance.to_dict()
# create an instance of MergeMultiDocParamsRequest from a dict
merge_multi_doc_params_request_from_dict = MergeMultiDocParamsRequest.from_dict(merge_multi_doc_params_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


