# LongTokenRequest

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**grantType** | **String** | The authentication grant type | 
**clientId** | **String** | Client identifier issued by Click2Mail | 
**clientSecret** | **String** | Required if using client_credentials with secret | [optional] 
**otpCode** | **String** | Required if your policy mandates OTP for issuance | [optional] 
**assertionType** | **String** | Required when grant_type&#x3D;assertion | [optional] 
**assertion** | **String** | Signed JWT or other accepted assertion | [optional] 
**scopes** | **[String]** | Scopes to assign to the long-term token | [optional] 
**ttlSeconds** | **Int** | Requested lifetime (1 hour - 90 days). Server may clamp. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


