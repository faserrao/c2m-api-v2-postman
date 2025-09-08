# C2MApiV2AuthOverlay.ShortTokenResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tokenType** | **String** |  | 
**accessToken** | **String** | Short-lived JWT | 
**expiresIn** | **Number** | Lifetime in seconds (e.g., 900 for 15 minutes) | 
**expiresAt** | **Date** | ISO 8601 timestamp of expiration | 
**scopes** | **[String]** | Granted scopes | [optional] 
**tokenId** | **String** | Server-issued identifier for this token | [optional] 



## Enum: TokenTypeEnum


* `Bearer` (value: `"Bearer"`)




