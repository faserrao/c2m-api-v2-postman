# # LongTokenRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**grant_type** | **string** | The authentication grant type |
**client_id** | **string** | Client identifier issued by Click2Mail |
**client_secret** | **string** | Required if using client_credentials with secret | [optional]
**otp_code** | **string** | Required if your policy mandates OTP for issuance | [optional]
**assertion_type** | **string** | Required when grant_type&#x3D;assertion | [optional]
**assertion** | **string** | Signed JWT or other accepted assertion | [optional]
**scopes** | **string[]** | Scopes to assign to the long-term token | [optional]
**ttl_seconds** | **int** | Requested lifetime (1 hour - 90 days). Server may clamp. | [optional]

[[Back to Model list]](../../README.md#models) [[Back to API list]](../../README.md#endpoints) [[Back to README]](../../README.md)
