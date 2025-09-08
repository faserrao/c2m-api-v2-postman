# C2M.Api.Model.ShortTokenResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TokenType** | **string** |  | 
**AccessToken** | **string** | Short-lived JWT | 
**ExpiresIn** | **int** | Lifetime in seconds (e.g., 900 for 15 minutes) | 
**ExpiresAt** | **DateTime** | ISO 8601 timestamp of expiration | 
**Scopes** | **List&lt;string&gt;** | Granted scopes | [optional] 
**TokenId** | **string** | Server-issued identifier for this token | [optional] 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

