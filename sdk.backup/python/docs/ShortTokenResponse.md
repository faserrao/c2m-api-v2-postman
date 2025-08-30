# ShortTokenResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token_type** | **str** |  | 
**access_token** | **str** | Short-lived JWT | 
**expires_in** | **int** | Lifetime in seconds (e.g., 900 for 15 minutes) | 
**expires_at** | **datetime** | ISO 8601 timestamp of expiration | 
**scopes** | **List[str]** | Granted scopes | [optional] 
**token_id** | **str** | Server-issued identifier for this token | [optional] 

## Example

```python
from c2m_api.models.short_token_response import ShortTokenResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ShortTokenResponse from a JSON string
short_token_response_instance = ShortTokenResponse.from_json(json)
# print the JSON string representation of the object
print(ShortTokenResponse.to_json())

# convert the object into a dict
short_token_response_dict = short_token_response_instance.to_dict()
# create an instance of ShortTokenResponse from a dict
short_token_response_from_dict = ShortTokenResponse.from_dict(short_token_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


