# C2M.Api.Model.LongTokenRequest
One of several credential mechanisms must be provided.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**GrantType** | **string** | The authentication grant type | 
**ClientId** | **string** | Client identifier issued by Click2Mail | 
**ClientSecret** | **string** | Required if using client_credentials with secret | [optional] 
**OtpCode** | **string** | Required if your policy mandates OTP for issuance | [optional] 
**AssertionType** | **string** | Required when grant_type&#x3D;assertion | [optional] 
**Assertion** | **string** | Signed JWT or other accepted assertion | [optional] 
**Scopes** | **List&lt;string&gt;** | Scopes to assign to the long-term token | [optional] 
**TtlSeconds** | **int** | Requested lifetime (1 hour - 90 days). Server may clamp. | [optional] 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

