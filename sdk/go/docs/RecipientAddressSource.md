# RecipientAddressSource

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**FirstName** | **string** |  | 
**LastName** | **string** |  | 
**Address1** | **string** |  | 
**City** | **string** |  | 
**State** | **string** |  | 
**Zip** | **string** |  | 
**Country** | **string** |  | 
**NickName** | Pointer to **string** |  | [optional] 
**Address2** | Pointer to **string** |  | [optional] 
**Address3** | Pointer to **string** |  | [optional] 
**PhoneNumber** | Pointer to **string** |  | [optional] 

## Methods

### NewRecipientAddressSource

`func NewRecipientAddressSource(firstName string, lastName string, address1 string, city string, state string, zip string, country string, ) *RecipientAddressSource`

NewRecipientAddressSource instantiates a new RecipientAddressSource object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewRecipientAddressSourceWithDefaults

`func NewRecipientAddressSourceWithDefaults() *RecipientAddressSource`

NewRecipientAddressSourceWithDefaults instantiates a new RecipientAddressSource object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetFirstName

`func (o *RecipientAddressSource) GetFirstName() string`

GetFirstName returns the FirstName field if non-nil, zero value otherwise.

### GetFirstNameOk

`func (o *RecipientAddressSource) GetFirstNameOk() (*string, bool)`

GetFirstNameOk returns a tuple with the FirstName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFirstName

`func (o *RecipientAddressSource) SetFirstName(v string)`

SetFirstName sets FirstName field to given value.


### GetLastName

`func (o *RecipientAddressSource) GetLastName() string`

GetLastName returns the LastName field if non-nil, zero value otherwise.

### GetLastNameOk

`func (o *RecipientAddressSource) GetLastNameOk() (*string, bool)`

GetLastNameOk returns a tuple with the LastName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLastName

`func (o *RecipientAddressSource) SetLastName(v string)`

SetLastName sets LastName field to given value.


### GetAddress1

`func (o *RecipientAddressSource) GetAddress1() string`

GetAddress1 returns the Address1 field if non-nil, zero value otherwise.

### GetAddress1Ok

`func (o *RecipientAddressSource) GetAddress1Ok() (*string, bool)`

GetAddress1Ok returns a tuple with the Address1 field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAddress1

`func (o *RecipientAddressSource) SetAddress1(v string)`

SetAddress1 sets Address1 field to given value.


### GetCity

`func (o *RecipientAddressSource) GetCity() string`

GetCity returns the City field if non-nil, zero value otherwise.

### GetCityOk

`func (o *RecipientAddressSource) GetCityOk() (*string, bool)`

GetCityOk returns a tuple with the City field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCity

`func (o *RecipientAddressSource) SetCity(v string)`

SetCity sets City field to given value.


### GetState

`func (o *RecipientAddressSource) GetState() string`

GetState returns the State field if non-nil, zero value otherwise.

### GetStateOk

`func (o *RecipientAddressSource) GetStateOk() (*string, bool)`

GetStateOk returns a tuple with the State field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetState

`func (o *RecipientAddressSource) SetState(v string)`

SetState sets State field to given value.


### GetZip

`func (o *RecipientAddressSource) GetZip() string`

GetZip returns the Zip field if non-nil, zero value otherwise.

### GetZipOk

`func (o *RecipientAddressSource) GetZipOk() (*string, bool)`

GetZipOk returns a tuple with the Zip field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetZip

`func (o *RecipientAddressSource) SetZip(v string)`

SetZip sets Zip field to given value.


### GetCountry

`func (o *RecipientAddressSource) GetCountry() string`

GetCountry returns the Country field if non-nil, zero value otherwise.

### GetCountryOk

`func (o *RecipientAddressSource) GetCountryOk() (*string, bool)`

GetCountryOk returns a tuple with the Country field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCountry

`func (o *RecipientAddressSource) SetCountry(v string)`

SetCountry sets Country field to given value.


### GetNickName

`func (o *RecipientAddressSource) GetNickName() string`

GetNickName returns the NickName field if non-nil, zero value otherwise.

### GetNickNameOk

`func (o *RecipientAddressSource) GetNickNameOk() (*string, bool)`

GetNickNameOk returns a tuple with the NickName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNickName

`func (o *RecipientAddressSource) SetNickName(v string)`

SetNickName sets NickName field to given value.

### HasNickName

`func (o *RecipientAddressSource) HasNickName() bool`

HasNickName returns a boolean if a field has been set.

### GetAddress2

`func (o *RecipientAddressSource) GetAddress2() string`

GetAddress2 returns the Address2 field if non-nil, zero value otherwise.

### GetAddress2Ok

`func (o *RecipientAddressSource) GetAddress2Ok() (*string, bool)`

GetAddress2Ok returns a tuple with the Address2 field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAddress2

`func (o *RecipientAddressSource) SetAddress2(v string)`

SetAddress2 sets Address2 field to given value.

### HasAddress2

`func (o *RecipientAddressSource) HasAddress2() bool`

HasAddress2 returns a boolean if a field has been set.

### GetAddress3

`func (o *RecipientAddressSource) GetAddress3() string`

GetAddress3 returns the Address3 field if non-nil, zero value otherwise.

### GetAddress3Ok

`func (o *RecipientAddressSource) GetAddress3Ok() (*string, bool)`

GetAddress3Ok returns a tuple with the Address3 field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAddress3

`func (o *RecipientAddressSource) SetAddress3(v string)`

SetAddress3 sets Address3 field to given value.

### HasAddress3

`func (o *RecipientAddressSource) HasAddress3() bool`

HasAddress3 returns a boolean if a field has been set.

### GetPhoneNumber

`func (o *RecipientAddressSource) GetPhoneNumber() string`

GetPhoneNumber returns the PhoneNumber field if non-nil, zero value otherwise.

### GetPhoneNumberOk

`func (o *RecipientAddressSource) GetPhoneNumberOk() (*string, bool)`

GetPhoneNumberOk returns a tuple with the PhoneNumber field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPhoneNumber

`func (o *RecipientAddressSource) SetPhoneNumber(v string)`

SetPhoneNumber sets PhoneNumber field to given value.

### HasPhoneNumber

`func (o *RecipientAddressSource) HasPhoneNumber() bool`

HasPhoneNumber returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


