# SubmitMultiDocWithTemplateParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[SubmitMultiDocWithTemplateParamsRequestItemsInner]**](SubmitMultiDocWithTemplateParamsRequestItemsInner.md) |  | 
**job_template** | **str** |  | 
**payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.submit_multi_doc_with_template_params import SubmitMultiDocWithTemplateParams

# TODO update the JSON string below
json = "{}"
# create an instance of SubmitMultiDocWithTemplateParams from a JSON string
submit_multi_doc_with_template_params_instance = SubmitMultiDocWithTemplateParams.from_json(json)
# print the JSON string representation of the object
print(SubmitMultiDocWithTemplateParams.to_json())

# convert the object into a dict
submit_multi_doc_with_template_params_dict = submit_multi_doc_with_template_params_instance.to_dict()
# create an instance of SubmitMultiDocWithTemplateParams from a dict
submit_multi_doc_with_template_params_from_dict = SubmitMultiDocWithTemplateParams.from_dict(submit_multi_doc_with_template_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


