# LongTokenRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**grant_type** | **String** | The authentication grant type | 
**client_id** | **String** | Client identifier issued by Click2Mail | 
**client_secret** | Option<**String**> | Required if using client_credentials with secret | [optional]
**otp_code** | Option<**String**> | Required if your policy mandates OTP for issuance | [optional]
**assertion_type** | Option<**String**> | Required when grant_type=assertion | [optional]
**assertion** | Option<**String**> | Signed JWT or other accepted assertion | [optional]
**scopes** | Option<**Vec<String>**> | Scopes to assign to the long-term token | [optional]
**ttl_seconds** | Option<**i32**> | Requested lifetime (1 hour - 90 days). Server may clamp. | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


