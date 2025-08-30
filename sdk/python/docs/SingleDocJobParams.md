# SingleDocJobParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_source_identifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | 
**recipient_address_sources** | [**List[RecipientAddressSource]**](RecipientAddressSource.md) |  | 
**job_options** | [**JobOptions**](JobOptions.md) |  | 
**payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from c2m_api.models.single_doc_job_params import SingleDocJobParams

# TODO update the JSON string below
json = "{}"
# create an instance of SingleDocJobParams from a JSON string
single_doc_job_params_instance = SingleDocJobParams.from_json(json)
# print the JSON string representation of the object
print(SingleDocJobParams.to_json())

# convert the object into a dict
single_doc_job_params_dict = single_doc_job_params_instance.to_dict()
# create an instance of SingleDocJobParams from a dict
single_doc_job_params_from_dict = SingleDocJobParams.from_dict(single_doc_job_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


