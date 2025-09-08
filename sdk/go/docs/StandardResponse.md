# StandardResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Status** | Pointer to **string** |  | [optional] 
**Message** | Pointer to **string** |  | [optional] 
**JobId** | Pointer to **string** |  | [optional] 

## Methods

### NewStandardResponse

`func NewStandardResponse() *StandardResponse`

NewStandardResponse instantiates a new StandardResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStandardResponseWithDefaults

`func NewStandardResponseWithDefaults() *StandardResponse`

NewStandardResponseWithDefaults instantiates a new StandardResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetStatus

`func (o *StandardResponse) GetStatus() string`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *StandardResponse) GetStatusOk() (*string, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *StandardResponse) SetStatus(v string)`

SetStatus sets Status field to given value.

### HasStatus

`func (o *StandardResponse) HasStatus() bool`

HasStatus returns a boolean if a field has been set.

### GetMessage

`func (o *StandardResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *StandardResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *StandardResponse) SetMessage(v string)`

SetMessage sets Message field to given value.

### HasMessage

`func (o *StandardResponse) HasMessage() bool`

HasMessage returns a boolean if a field has been set.

### GetJobId

`func (o *StandardResponse) GetJobId() string`

GetJobId returns the JobId field if non-nil, zero value otherwise.

### GetJobIdOk

`func (o *StandardResponse) GetJobIdOk() (*string, bool)`

GetJobIdOk returns a tuple with the JobId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJobId

`func (o *StandardResponse) SetJobId(v string)`

SetJobId sets JobId field to given value.

### HasJobId

`func (o *StandardResponse) HasJobId() bool`

HasJobId returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


