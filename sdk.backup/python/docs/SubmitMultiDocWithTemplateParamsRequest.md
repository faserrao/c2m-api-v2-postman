# SubmitMultiDocWithTemplateParamsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[SubmitMultiDocWithTemplateParamsRequestItemsInner]**](SubmitMultiDocWithTemplateParamsRequestItemsInner.md) |  | 
**job_template** | **str** |  | 
**payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.submit_multi_doc_with_template_params_request import SubmitMultiDocWithTemplateParamsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SubmitMultiDocWithTemplateParamsRequest from a JSON string
submit_multi_doc_with_template_params_request_instance = SubmitMultiDocWithTemplateParamsRequest.from_json(json)
# print the JSON string representation of the object
print(SubmitMultiDocWithTemplateParamsRequest.to_json())

# convert the object into a dict
submit_multi_doc_with_template_params_request_dict = submit_multi_doc_with_template_params_request_instance.to_dict()
# create an instance of SubmitMultiDocWithTemplateParamsRequest from a dict
submit_multi_doc_with_template_params_request_from_dict = SubmitMultiDocWithTemplateParamsRequest.from_dict(submit_multi_doc_with_template_params_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


