# C2M.Api.Model.LongTokenResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TokenType** | **string** |  | 
**AccessToken** | **string** | Long-lived token (opaque or JWT depending on deployment) | 
**ExpiresIn** | **int** | Lifetime in seconds | 
**ExpiresAt** | **DateTime** | ISO 8601 timestamp of expiration | 
**Scopes** | **List&lt;string&gt;** | Granted scopes | [optional] 
**TokenId** | **string** | Server-issued identifier for this token | [optional] 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

