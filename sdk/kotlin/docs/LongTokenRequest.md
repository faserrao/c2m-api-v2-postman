
# LongTokenRequest

## Properties
| Name | Type | Description | Notes |
| ------------ | ------------- | ------------- | ------------- |
| **grantType** | [**inline**](#GrantType) | The authentication grant type |  |
| **clientId** | **kotlin.String** | Client identifier issued by Click2Mail |  |
| **clientSecret** | **kotlin.String** | Required if using client_credentials with secret |  [optional] |
| **otpCode** | **kotlin.String** | Required if your policy mandates OTP for issuance |  [optional] |
| **assertionType** | **kotlin.String** | Required when grant_type&#x3D;assertion |  [optional] |
| **assertion** | **kotlin.String** | Signed JWT or other accepted assertion |  [optional] |
| **scopes** | **kotlin.collections.List&lt;kotlin.String&gt;** | Scopes to assign to the long-term token |  [optional] |
| **ttlSeconds** | **kotlin.Int** | Requested lifetime (1 hour - 90 days). Server may clamp. |  [optional] |


<a id="GrantType"></a>
## Enum: grant_type
| Name | Value |
| ---- | ----- |
| grantType | client_credentials, assertion |



