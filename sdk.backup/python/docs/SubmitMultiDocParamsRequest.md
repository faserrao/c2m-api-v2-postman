# SubmitMultiDocParamsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[SubmitMultiDocWithTemplateParamsRequestItemsInner]**](SubmitMultiDocWithTemplateParamsRequestItemsInner.md) |  | 
**job_options** | [**JobOptions**](JobOptions.md) |  | 
**payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.submit_multi_doc_params_request import SubmitMultiDocParamsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SubmitMultiDocParamsRequest from a JSON string
submit_multi_doc_params_request_instance = SubmitMultiDocParamsRequest.from_json(json)
# print the JSON string representation of the object
print(SubmitMultiDocParamsRequest.to_json())

# convert the object into a dict
submit_multi_doc_params_request_dict = submit_multi_doc_params_request_instance.to_dict()
# create an instance of SubmitMultiDocParamsRequest from a dict
submit_multi_doc_params_request_from_dict = SubmitMultiDocParamsRequest.from_dict(submit_multi_doc_params_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


