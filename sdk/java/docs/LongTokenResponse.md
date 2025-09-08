

# LongTokenResponse


## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**tokenType** | [**TokenTypeEnum**](#TokenTypeEnum) |  |  |
|**accessToken** | **String** | Long-lived token (opaque or JWT depending on deployment) |  |
|**expiresIn** | **Integer** | Lifetime in seconds |  |
|**expiresAt** | **OffsetDateTime** | ISO 8601 timestamp of expiration |  |
|**scopes** | **List&lt;String&gt;** | Granted scopes |  [optional] |
|**tokenId** | **String** | Server-issued identifier for this token |  [optional] |



## Enum: TokenTypeEnum

| Name | Value |
|---- | -----|
| BEARER | &quot;Bearer&quot; |



