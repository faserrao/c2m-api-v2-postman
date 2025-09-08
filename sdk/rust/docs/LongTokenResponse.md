# LongTokenResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token_type** | **String** |  | 
**access_token** | **String** | Long-lived token (opaque or JWT depending on deployment) | 
**expires_in** | **i32** | Lifetime in seconds | 
**expires_at** | **String** | ISO 8601 timestamp of expiration | 
**scopes** | Option<**Vec<String>**> | Granted scopes | [optional]
**token_id** | Option<**String**> | Server-issued identifier for this token | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


