# JobOptions

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentClass** | [**DocumentClass**](DocumentClass.md) |  | 
**Layout** | [**Layout**](Layout.md) |  | 
**Mailclass** | [**Mailclass**](Mailclass.md) |  | 
**PaperType** | [**PaperType**](PaperType.md) |  | 
**PrintOption** | [**PrintOption**](PrintOption.md) |  | 
**Envelope** | [**Envelope**](Envelope.md) |  | 

## Methods

### NewJobOptions

`func NewJobOptions(documentClass DocumentClass, layout Layout, mailclass Mailclass, paperType PaperType, printOption PrintOption, envelope Envelope, ) *JobOptions`

NewJobOptions instantiates a new JobOptions object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewJobOptionsWithDefaults

`func NewJobOptionsWithDefaults() *JobOptions`

NewJobOptionsWithDefaults instantiates a new JobOptions object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentClass

`func (o *JobOptions) GetDocumentClass() DocumentClass`

GetDocumentClass returns the DocumentClass field if non-nil, zero value otherwise.

### GetDocumentClassOk

`func (o *JobOptions) GetDocumentClassOk() (*DocumentClass, bool)`

GetDocumentClassOk returns a tuple with the DocumentClass field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentClass

`func (o *JobOptions) SetDocumentClass(v DocumentClass)`

SetDocumentClass sets DocumentClass field to given value.


### GetLayout

`func (o *JobOptions) GetLayout() Layout`

GetLayout returns the Layout field if non-nil, zero value otherwise.

### GetLayoutOk

`func (o *JobOptions) GetLayoutOk() (*Layout, bool)`

GetLayoutOk returns a tuple with the Layout field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLayout

`func (o *JobOptions) SetLayout(v Layout)`

SetLayout sets Layout field to given value.


### GetMailclass

`func (o *JobOptions) GetMailclass() Mailclass`

GetMailclass returns the Mailclass field if non-nil, zero value otherwise.

### GetMailclassOk

`func (o *JobOptions) GetMailclassOk() (*Mailclass, bool)`

GetMailclassOk returns a tuple with the Mailclass field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMailclass

`func (o *JobOptions) SetMailclass(v Mailclass)`

SetMailclass sets Mailclass field to given value.


### GetPaperType

`func (o *JobOptions) GetPaperType() PaperType`

GetPaperType returns the PaperType field if non-nil, zero value otherwise.

### GetPaperTypeOk

`func (o *JobOptions) GetPaperTypeOk() (*PaperType, bool)`

GetPaperTypeOk returns a tuple with the PaperType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaperType

`func (o *JobOptions) SetPaperType(v PaperType)`

SetPaperType sets PaperType field to given value.


### GetPrintOption

`func (o *JobOptions) GetPrintOption() PrintOption`

GetPrintOption returns the PrintOption field if non-nil, zero value otherwise.

### GetPrintOptionOk

`func (o *JobOptions) GetPrintOptionOk() (*PrintOption, bool)`

GetPrintOptionOk returns a tuple with the PrintOption field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPrintOption

`func (o *JobOptions) SetPrintOption(v PrintOption)`

SetPrintOption sets PrintOption field to given value.


### GetEnvelope

`func (o *JobOptions) GetEnvelope() Envelope`

GetEnvelope returns the Envelope field if non-nil, zero value otherwise.

### GetEnvelopeOk

`func (o *JobOptions) GetEnvelopeOk() (*Envelope, bool)`

GetEnvelopeOk returns a tuple with the Envelope field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEnvelope

`func (o *JobOptions) SetEnvelope(v Envelope)`

SetEnvelope sets Envelope field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


