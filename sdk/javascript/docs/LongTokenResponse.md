# C2MApiV2AuthOverlay.LongTokenResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tokenType** | **String** |  | 
**accessToken** | **String** | Long-lived token (opaque or JWT depending on deployment) | 
**expiresIn** | **Number** | Lifetime in seconds | 
**expiresAt** | **Date** | ISO 8601 timestamp of expiration | 
**scopes** | **[String]** | Granted scopes | [optional] 
**tokenId** | **String** | Server-issued identifier for this token | [optional] 



## Enum: TokenTypeEnum


* `Bearer` (value: `"Bearer"`)




