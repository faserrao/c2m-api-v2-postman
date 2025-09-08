

# LongTokenRequest

One of several credential mechanisms must be provided.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**grantType** | [**GrantTypeEnum**](#GrantTypeEnum) | The authentication grant type |  |
|**clientId** | **String** | Client identifier issued by Click2Mail |  |
|**clientSecret** | **String** | Required if using client_credentials with secret |  [optional] |
|**otpCode** | **String** | Required if your policy mandates OTP for issuance |  [optional] |
|**assertionType** | **String** | Required when grant_type&#x3D;assertion |  [optional] |
|**assertion** | **String** | Signed JWT or other accepted assertion |  [optional] |
|**scopes** | **List&lt;String&gt;** | Scopes to assign to the long-term token |  [optional] |
|**ttlSeconds** | **Integer** | Requested lifetime (1 hour - 90 days). Server may clamp. |  [optional] |



## Enum: GrantTypeEnum

| Name | Value |
|---- | -----|
| CLIENT_CREDENTIALS | &quot;client_credentials&quot; |
| ASSERTION | &quot;assertion&quot; |



