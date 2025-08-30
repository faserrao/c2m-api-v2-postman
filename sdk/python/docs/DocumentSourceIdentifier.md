# DocumentSourceIdentifier


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**upload_request_id** | **int** |  | 
**document_name** | **str** |  | 
**zip_id** | **int** |  | 

## Example

```python
from c2m_api.models.document_source_identifier import DocumentSourceIdentifier

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentSourceIdentifier from a JSON string
document_source_identifier_instance = DocumentSourceIdentifier.from_json(json)
# print the JSON string representation of the object
print(DocumentSourceIdentifier.to_json())

# convert the object into a dict
document_source_identifier_dict = document_source_identifier_instance.to_dict()
# create an instance of DocumentSourceIdentifier from a dict
document_source_identifier_from_dict = DocumentSourceIdentifier.from_dict(document_source_identifier_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


