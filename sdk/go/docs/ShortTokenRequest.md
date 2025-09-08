# ShortTokenRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**LongToken** | Pointer to **string** | Optional if the long-term token is provided in Authorization header | [optional] 
**Scopes** | Pointer to **[]string** | Optional scope narrowing; defaults to the long-term token&#39;s scopes | [optional] 

## Methods

### NewShortTokenRequest

`func NewShortTokenRequest() *ShortTokenRequest`

NewShortTokenRequest instantiates a new ShortTokenRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewShortTokenRequestWithDefaults

`func NewShortTokenRequestWithDefaults() *ShortTokenRequest`

NewShortTokenRequestWithDefaults instantiates a new ShortTokenRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetLongToken

`func (o *ShortTokenRequest) GetLongToken() string`

GetLongToken returns the LongToken field if non-nil, zero value otherwise.

### GetLongTokenOk

`func (o *ShortTokenRequest) GetLongTokenOk() (*string, bool)`

GetLongTokenOk returns a tuple with the LongToken field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLongToken

`func (o *ShortTokenRequest) SetLongToken(v string)`

SetLongToken sets LongToken field to given value.

### HasLongToken

`func (o *ShortTokenRequest) HasLongToken() bool`

HasLongToken returns a boolean if a field has been set.

### GetScopes

`func (o *ShortTokenRequest) GetScopes() []string`

GetScopes returns the Scopes field if non-nil, zero value otherwise.

### GetScopesOk

`func (o *ShortTokenRequest) GetScopesOk() (*[]string, bool)`

GetScopesOk returns a tuple with the Scopes field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetScopes

`func (o *ShortTokenRequest) SetScopes(v []string)`

SetScopes sets Scopes field to given value.

### HasScopes

`func (o *ShortTokenRequest) HasScopes() bool`

HasScopes returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


