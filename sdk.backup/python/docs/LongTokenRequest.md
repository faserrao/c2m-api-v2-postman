# LongTokenRequest

One of several credential mechanisms must be provided.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**grant_type** | **str** | The authentication grant type | 
**client_id** | **str** | Client identifier issued by Click2Mail | 
**client_secret** | **str** | Required if using client_credentials with secret | [optional] 
**otp_code** | **str** | Required if your policy mandates OTP for issuance | [optional] 
**assertion_type** | **str** | Required when grant_type&#x3D;assertion | [optional] 
**assertion** | **str** | Signed JWT or other accepted assertion | [optional] 
**scopes** | **List[str]** | Scopes to assign to the long-term token | [optional] 
**ttl_seconds** | **int** | Requested lifetime (1 hour - 90 days). Server may clamp. | [optional] 

## Example

```python
from c2m_api.models.long_token_request import LongTokenRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LongTokenRequest from a JSON string
long_token_request_instance = LongTokenRequest.from_json(json)
# print the JSON string representation of the object
print(LongTokenRequest.to_json())

# convert the object into a dict
long_token_request_dict = long_token_request_instance.to_dict()
# create an instance of LongTokenRequest from a dict
long_token_request_from_dict = LongTokenRequest.from_dict(long_token_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


