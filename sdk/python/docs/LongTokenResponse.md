# LongTokenResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token_type** | **str** |  | 
**access_token** | **str** | Long-lived token (opaque or JWT depending on deployment) | 
**expires_in** | **int** | Lifetime in seconds | 
**expires_at** | **datetime** | ISO 8601 timestamp of expiration | 
**scopes** | **List[str]** | Granted scopes | [optional] 
**token_id** | **str** | Server-issued identifier for this token | [optional] 

## Example

```python
from c2m_api.models.long_token_response import LongTokenResponse

# TODO update the JSON string below
json = "{}"
# create an instance of LongTokenResponse from a JSON string
long_token_response_instance = LongTokenResponse.from_json(json)
# print the JSON string representation of the object
print(LongTokenResponse.to_json())

# convert the object into a dict
long_token_response_dict = long_token_response_instance.to_dict()
# create an instance of LongTokenResponse from a dict
long_token_response_from_dict = LongTokenResponse.from_dict(long_token_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


