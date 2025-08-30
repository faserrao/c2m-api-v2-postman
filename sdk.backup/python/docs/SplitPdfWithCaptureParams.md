# SplitPdfWithCaptureParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_source_identifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**embedded_extraction_specs** | [**List[ExtractionSpec]**](ExtractionSpec.md) |  | 
**payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.split_pdf_with_capture_params import SplitPdfWithCaptureParams

# TODO update the JSON string below
json = "{}"
# create an instance of SplitPdfWithCaptureParams from a JSON string
split_pdf_with_capture_params_instance = SplitPdfWithCaptureParams.from_json(json)
# print the JSON string representation of the object
print(SplitPdfWithCaptureParams.to_json())

# convert the object into a dict
split_pdf_with_capture_params_dict = split_pdf_with_capture_params_instance.to_dict()
# create an instance of SplitPdfWithCaptureParams from a dict
split_pdf_with_capture_params_from_dict = SplitPdfWithCaptureParams.from_dict(split_pdf_with_capture_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


