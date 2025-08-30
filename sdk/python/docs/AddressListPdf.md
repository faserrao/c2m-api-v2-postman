# AddressListPdf


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_source_identifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**address_list_region** | **str** |  | 
**delimiter** | **str** |  | [optional] 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.address_list_pdf import AddressListPdf

# TODO update the JSON string below
json = "{}"
# create an instance of AddressListPdf from a JSON string
address_list_pdf_instance = AddressListPdf.from_json(json)
# print the JSON string representation of the object
print(AddressListPdf.to_json())

# convert the object into a dict
address_list_pdf_dict = address_list_pdf_instance.to_dict()
# create an instance of AddressListPdf from a dict
address_list_pdf_from_dict = AddressListPdf.from_dict(address_list_pdf_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


