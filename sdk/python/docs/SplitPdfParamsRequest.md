# SplitPdfParamsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_source_identifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**items** | [**List[SplitPdfParamsRequestItemsInner]**](SplitPdfParamsRequestItemsInner.md) |  | 
**payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.split_pdf_params_request import SplitPdfParamsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SplitPdfParamsRequest from a JSON string
split_pdf_params_request_instance = SplitPdfParamsRequest.from_json(json)
# print the JSON string representation of the object
print(SplitPdfParamsRequest.to_json())

# convert the object into a dict
split_pdf_params_request_dict = split_pdf_params_request_instance.to_dict()
# create an instance of SplitPdfParamsRequest from a dict
split_pdf_params_request_from_dict = SplitPdfParamsRequest.from_dict(split_pdf_params_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


