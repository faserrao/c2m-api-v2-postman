# ShortTokenRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**long_token** | **str** | Optional if the long-term token is provided in Authorization header | [optional] 
**scopes** | **List[str]** | Optional scope narrowing; defaults to the long-term token&#39;s scopes | [optional] 

## Example

```python
from c2m_api.models.short_token_request import ShortTokenRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ShortTokenRequest from a JSON string
short_token_request_instance = ShortTokenRequest.from_json(json)
# print the JSON string representation of the object
print(ShortTokenRequest.to_json())

# convert the object into a dict
short_token_request_dict = short_token_request_instance.to_dict()
# create an instance of ShortTokenRequest from a dict
short_token_request_from_dict = ShortTokenRequest.from_dict(short_token_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


