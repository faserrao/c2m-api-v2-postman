# SubmitSingleDocWithTemplateParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_template** | **str** |  | 
**payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.submit_single_doc_with_template_params import SubmitSingleDocWithTemplateParams

# TODO update the JSON string below
json = "{}"
# create an instance of SubmitSingleDocWithTemplateParams from a JSON string
submit_single_doc_with_template_params_instance = SubmitSingleDocWithTemplateParams.from_json(json)
# print the JSON string representation of the object
print(SubmitSingleDocWithTemplateParams.to_json())

# convert the object into a dict
submit_single_doc_with_template_params_dict = submit_single_doc_with_template_params_instance.to_dict()
# create an instance of SubmitSingleDocWithTemplateParams from a dict
submit_single_doc_with_template_params_from_dict = SubmitSingleDocWithTemplateParams.from_dict(submit_single_doc_with_template_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


