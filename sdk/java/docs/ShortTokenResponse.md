

# ShortTokenResponse


## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**tokenType** | [**TokenTypeEnum**](#TokenTypeEnum) |  |  |
|**accessToken** | **String** | Short-lived JWT |  |
|**expiresIn** | **Integer** | Lifetime in seconds (e.g., 900 for 15 minutes) |  |
|**expiresAt** | **OffsetDateTime** | ISO 8601 timestamp of expiration |  |
|**scopes** | **List&lt;String&gt;** | Granted scopes |  [optional] |
|**tokenId** | **String** | Server-issued identifier for this token |  [optional] |



## Enum: TokenTypeEnum

| Name | Value |
|---- | -----|
| BEARER | &quot;Bearer&quot; |



