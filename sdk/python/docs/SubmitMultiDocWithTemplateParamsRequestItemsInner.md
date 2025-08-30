# SubmitMultiDocWithTemplateParamsRequestItemsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_source_identifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**recipient_address_source** | [**RecipientAddressSource**](RecipientAddressSource.md) |  | 

## Example

```python
from c2m_api.models.submit_multi_doc_with_template_params_request_items_inner import SubmitMultiDocWithTemplateParamsRequestItemsInner

# TODO update the JSON string below
json = "{}"
# create an instance of SubmitMultiDocWithTemplateParamsRequestItemsInner from a JSON string
submit_multi_doc_with_template_params_request_items_inner_instance = SubmitMultiDocWithTemplateParamsRequestItemsInner.from_json(json)
# print the JSON string representation of the object
print(SubmitMultiDocWithTemplateParamsRequestItemsInner.to_json())

# convert the object into a dict
submit_multi_doc_with_template_params_request_items_inner_dict = submit_multi_doc_with_template_params_request_items_inner_instance.to_dict()
# create an instance of SubmitMultiDocWithTemplateParamsRequestItemsInner from a dict
submit_multi_doc_with_template_params_request_items_inner_from_dict = SubmitMultiDocWithTemplateParamsRequestItemsInner.from_dict(submit_multi_doc_with_template_params_request_items_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


