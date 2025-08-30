# MultiPdfWithCaptureParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address_capture_pdfs** | [**List[AddressListPdf]**](AddressListPdf.md) |  | 
**job_template** | **str** |  | 
**payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.multi_pdf_with_capture_params import MultiPdfWithCaptureParams

# TODO update the JSON string below
json = "{}"
# create an instance of MultiPdfWithCaptureParams from a JSON string
multi_pdf_with_capture_params_instance = MultiPdfWithCaptureParams.from_json(json)
# print the JSON string representation of the object
print(MultiPdfWithCaptureParams.to_json())

# convert the object into a dict
multi_pdf_with_capture_params_dict = multi_pdf_with_capture_params_instance.to_dict()
# create an instance of MultiPdfWithCaptureParams from a dict
multi_pdf_with_capture_params_from_dict = MultiPdfWithCaptureParams.from_dict(multi_pdf_with_capture_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


