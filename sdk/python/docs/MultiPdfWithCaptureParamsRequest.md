# MultiPdfWithCaptureParamsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address_capture_pdfs** | [**List[AddressListPdf]**](AddressListPdf.md) |  | 
**job_template** | **str** |  | 
**payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.multi_pdf_with_capture_params_request import MultiPdfWithCaptureParamsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MultiPdfWithCaptureParamsRequest from a JSON string
multi_pdf_with_capture_params_request_instance = MultiPdfWithCaptureParamsRequest.from_json(json)
# print the JSON string representation of the object
print(MultiPdfWithCaptureParamsRequest.to_json())

# convert the object into a dict
multi_pdf_with_capture_params_request_dict = multi_pdf_with_capture_params_request_instance.to_dict()
# create an instance of MultiPdfWithCaptureParamsRequest from a dict
multi_pdf_with_capture_params_request_from_dict = MultiPdfWithCaptureParamsRequest.from_dict(multi_pdf_with_capture_params_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


