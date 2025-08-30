# SplitPdfParamsRequestItemsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**page_range** | [**PageRange**](PageRange.md) |  | 
**recipient_address_sources** | [**List[RecipientAddressSource]**](RecipientAddressSource.md) |  | 

## Example

```python
from c2m_api.models.split_pdf_params_request_items_inner import SplitPdfParamsRequestItemsInner

# TODO update the JSON string below
json = "{}"
# create an instance of SplitPdfParamsRequestItemsInner from a JSON string
split_pdf_params_request_items_inner_instance = SplitPdfParamsRequestItemsInner.from_json(json)
# print the JSON string representation of the object
print(SplitPdfParamsRequestItemsInner.to_json())

# convert the object into a dict
split_pdf_params_request_items_inner_dict = split_pdf_params_request_items_inner_instance.to_dict()
# create an instance of SplitPdfParamsRequestItemsInner from a dict
split_pdf_params_request_items_inner_from_dict = SplitPdfParamsRequestItemsInner.from_dict(split_pdf_params_request_items_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


