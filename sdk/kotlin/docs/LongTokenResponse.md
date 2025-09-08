
# LongTokenResponse

## Properties
| Name | Type | Description | Notes |
| ------------ | ------------- | ------------- | ------------- |
| **tokenType** | [**inline**](#TokenType) |  |  |
| **accessToken** | **kotlin.String** | Long-lived token (opaque or JWT depending on deployment) |  |
| **expiresIn** | **kotlin.Int** | Lifetime in seconds |  |
| **expiresAt** | [**java.time.OffsetDateTime**](java.time.OffsetDateTime.md) | ISO 8601 timestamp of expiration |  |
| **scopes** | **kotlin.collections.List&lt;kotlin.String&gt;** | Granted scopes |  [optional] |
| **tokenId** | **kotlin.String** | Server-issued identifier for this token |  [optional] |


<a id="TokenType"></a>
## Enum: token_type
| Name | Value |
| ---- | ----- |
| tokenType | Bearer |



