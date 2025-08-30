# SubmitMultiDocParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[SubmitMultiDocWithTemplateParamsRequestItemsInner]**](SubmitMultiDocWithTemplateParamsRequestItemsInner.md) |  | 
**job_options** | [**JobOptions**](JobOptions.md) |  | 
**payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.submit_multi_doc_params import SubmitMultiDocParams

# TODO update the JSON string below
json = "{}"
# create an instance of SubmitMultiDocParams from a JSON string
submit_multi_doc_params_instance = SubmitMultiDocParams.from_json(json)
# print the JSON string representation of the object
print(SubmitMultiDocParams.to_json())

# convert the object into a dict
submit_multi_doc_params_dict = submit_multi_doc_params_instance.to_dict()
# create an instance of SubmitMultiDocParams from a dict
submit_multi_doc_params_from_dict = SubmitMultiDocParams.from_dict(submit_multi_doc_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


