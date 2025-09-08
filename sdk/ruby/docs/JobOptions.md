# OpenapiClient::JobOptions

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **document_class** | [**DocumentClass**](DocumentClass.md) |  |  |
| **layout** | [**Layout**](Layout.md) |  |  |
| **mailclass** | [**Mailclass**](Mailclass.md) |  |  |
| **paper_type** | [**PaperType**](PaperType.md) |  |  |
| **print_option** | [**PrintOption**](PrintOption.md) |  |  |
| **envelope** | [**Envelope**](Envelope.md) |  |  |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::JobOptions.new(
  document_class: null,
  layout: null,
  mailclass: null,
  paper_type: null,
  print_option: null,
  envelope: null
)
```

