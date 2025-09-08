
# ShortTokenResponse

## Properties
| Name | Type | Description | Notes |
| ------------ | ------------- | ------------- | ------------- |
| **tokenType** | [**inline**](#TokenType) |  |  |
| **accessToken** | **kotlin.String** | Short-lived JWT |  |
| **expiresIn** | **kotlin.Int** | Lifetime in seconds (e.g., 900 for 15 minutes) |  |
| **expiresAt** | [**java.time.OffsetDateTime**](java.time.OffsetDateTime.md) | ISO 8601 timestamp of expiration |  |
| **scopes** | **kotlin.collections.List&lt;kotlin.String&gt;** | Granted scopes |  [optional] |
| **tokenId** | **kotlin.String** | Server-issued identifier for this token |  [optional] |


<a id="TokenType"></a>
## Enum: token_type
| Name | Value |
| ---- | ----- |
| tokenType | Bearer |



