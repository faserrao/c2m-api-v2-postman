# \AuthAPI

All URIs are relative to *https://api.example.com/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**IssueLongTermToken**](AuthAPI.md#IssueLongTermToken) | **Post** /auth/tokens/long | Issue or rotate a long-term token
[**IssueShortTermToken**](AuthAPI.md#IssueShortTermToken) | **Post** /auth/tokens/short | Issue a short-term access token
[**RevokeToken**](AuthAPI.md#RevokeToken) | **Post** /auth/tokens/{tokenId}/revoke | Revoke a token



## IssueLongTermToken

> LongTokenResponse IssueLongTermToken(ctx).LongTokenRequest(longTokenRequest).Execute()

Issue or rotate a long-term token



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	longTokenRequest := *openapiclient.NewLongTokenRequest("GrantType_example", "ClientId_example") // LongTokenRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthAPI.IssueLongTermToken(context.Background()).LongTokenRequest(longTokenRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthAPI.IssueLongTermToken``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `IssueLongTermToken`: LongTokenResponse
	fmt.Fprintf(os.Stdout, "Response from `AuthAPI.IssueLongTermToken`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiIssueLongTermTokenRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **longTokenRequest** | [**LongTokenRequest**](LongTokenRequest.md) |  | 

### Return type

[**LongTokenResponse**](LongTokenResponse.md)

### Authorization

[ShortTokenAuth](../README.md#ShortTokenAuth), [ClientKey](../README.md#ClientKey)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## IssueShortTermToken

> ShortTokenResponse IssueShortTermToken(ctx).ShortTokenRequest(shortTokenRequest).Execute()

Issue a short-term access token



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	shortTokenRequest := *openapiclient.NewShortTokenRequest() // ShortTokenRequest |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthAPI.IssueShortTermToken(context.Background()).ShortTokenRequest(shortTokenRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthAPI.IssueShortTermToken``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `IssueShortTermToken`: ShortTokenResponse
	fmt.Fprintf(os.Stdout, "Response from `AuthAPI.IssueShortTermToken`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiIssueShortTermTokenRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortTokenRequest** | [**ShortTokenRequest**](ShortTokenRequest.md) |  | 

### Return type

[**ShortTokenResponse**](ShortTokenResponse.md)

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RevokeToken

> RevokeToken(ctx, tokenId).Execute()

Revoke a token



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	tokenId := "tokenId_example" // string | The token ID to revoke

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.AuthAPI.RevokeToken(context.Background(), tokenId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthAPI.RevokeToken``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**tokenId** | **string** | The token ID to revoke | 

### Other Parameters

Other parameters are passed through a pointer to a apiRevokeTokenRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

 (empty response body)

### Authorization

[LongTokenAuth](../README.md#LongTokenAuth), [ShortTokenAuth](../README.md#ShortTokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

