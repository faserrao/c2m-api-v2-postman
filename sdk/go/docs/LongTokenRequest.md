# LongTokenRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**GrantType** | **string** | The authentication grant type | 
**ClientId** | **string** | Client identifier issued by Click2Mail | 
**ClientSecret** | Pointer to **string** | Required if using client_credentials with secret | [optional] 
**OtpCode** | Pointer to **string** | Required if your policy mandates OTP for issuance | [optional] 
**AssertionType** | Pointer to **string** | Required when grant_type&#x3D;assertion | [optional] 
**Assertion** | Pointer to **string** | Signed JWT or other accepted assertion | [optional] 
**Scopes** | Pointer to **[]string** | Scopes to assign to the long-term token | [optional] 
**TtlSeconds** | Pointer to **int32** | Requested lifetime (1 hour - 90 days). Server may clamp. | [optional] 

## Methods

### NewLongTokenRequest

`func NewLongTokenRequest(grantType string, clientId string, ) *LongTokenRequest`

NewLongTokenRequest instantiates a new LongTokenRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLongTokenRequestWithDefaults

`func NewLongTokenRequestWithDefaults() *LongTokenRequest`

NewLongTokenRequestWithDefaults instantiates a new LongTokenRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetGrantType

`func (o *LongTokenRequest) GetGrantType() string`

GetGrantType returns the GrantType field if non-nil, zero value otherwise.

### GetGrantTypeOk

`func (o *LongTokenRequest) GetGrantTypeOk() (*string, bool)`

GetGrantTypeOk returns a tuple with the GrantType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetGrantType

`func (o *LongTokenRequest) SetGrantType(v string)`

SetGrantType sets GrantType field to given value.


### GetClientId

`func (o *LongTokenRequest) GetClientId() string`

GetClientId returns the ClientId field if non-nil, zero value otherwise.

### GetClientIdOk

`func (o *LongTokenRequest) GetClientIdOk() (*string, bool)`

GetClientIdOk returns a tuple with the ClientId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetClientId

`func (o *LongTokenRequest) SetClientId(v string)`

SetClientId sets ClientId field to given value.


### GetClientSecret

`func (o *LongTokenRequest) GetClientSecret() string`

GetClientSecret returns the ClientSecret field if non-nil, zero value otherwise.

### GetClientSecretOk

`func (o *LongTokenRequest) GetClientSecretOk() (*string, bool)`

GetClientSecretOk returns a tuple with the ClientSecret field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetClientSecret

`func (o *LongTokenRequest) SetClientSecret(v string)`

SetClientSecret sets ClientSecret field to given value.

### HasClientSecret

`func (o *LongTokenRequest) HasClientSecret() bool`

HasClientSecret returns a boolean if a field has been set.

### GetOtpCode

`func (o *LongTokenRequest) GetOtpCode() string`

GetOtpCode returns the OtpCode field if non-nil, zero value otherwise.

### GetOtpCodeOk

`func (o *LongTokenRequest) GetOtpCodeOk() (*string, bool)`

GetOtpCodeOk returns a tuple with the OtpCode field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOtpCode

`func (o *LongTokenRequest) SetOtpCode(v string)`

SetOtpCode sets OtpCode field to given value.

### HasOtpCode

`func (o *LongTokenRequest) HasOtpCode() bool`

HasOtpCode returns a boolean if a field has been set.

### GetAssertionType

`func (o *LongTokenRequest) GetAssertionType() string`

GetAssertionType returns the AssertionType field if non-nil, zero value otherwise.

### GetAssertionTypeOk

`func (o *LongTokenRequest) GetAssertionTypeOk() (*string, bool)`

GetAssertionTypeOk returns a tuple with the AssertionType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAssertionType

`func (o *LongTokenRequest) SetAssertionType(v string)`

SetAssertionType sets AssertionType field to given value.

### HasAssertionType

`func (o *LongTokenRequest) HasAssertionType() bool`

HasAssertionType returns a boolean if a field has been set.

### GetAssertion

`func (o *LongTokenRequest) GetAssertion() string`

GetAssertion returns the Assertion field if non-nil, zero value otherwise.

### GetAssertionOk

`func (o *LongTokenRequest) GetAssertionOk() (*string, bool)`

GetAssertionOk returns a tuple with the Assertion field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAssertion

`func (o *LongTokenRequest) SetAssertion(v string)`

SetAssertion sets Assertion field to given value.

### HasAssertion

`func (o *LongTokenRequest) HasAssertion() bool`

HasAssertion returns a boolean if a field has been set.

### GetScopes

`func (o *LongTokenRequest) GetScopes() []string`

GetScopes returns the Scopes field if non-nil, zero value otherwise.

### GetScopesOk

`func (o *LongTokenRequest) GetScopesOk() (*[]string, bool)`

GetScopesOk returns a tuple with the Scopes field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetScopes

`func (o *LongTokenRequest) SetScopes(v []string)`

SetScopes sets Scopes field to given value.

### HasScopes

`func (o *LongTokenRequest) HasScopes() bool`

HasScopes returns a boolean if a field has been set.

### GetTtlSeconds

`func (o *LongTokenRequest) GetTtlSeconds() int32`

GetTtlSeconds returns the TtlSeconds field if non-nil, zero value otherwise.

### GetTtlSecondsOk

`func (o *LongTokenRequest) GetTtlSecondsOk() (*int32, bool)`

GetTtlSecondsOk returns a tuple with the TtlSeconds field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTtlSeconds

`func (o *LongTokenRequest) SetTtlSeconds(v int32)`

SetTtlSeconds sets TtlSeconds field to given value.

### HasTtlSeconds

`func (o *LongTokenRequest) HasTtlSeconds() bool`

HasTtlSeconds returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


