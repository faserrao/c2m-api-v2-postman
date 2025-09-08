# OpenapiClient::SingleDocJobParamsRequest

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **document_source_identifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  |  |
| **recipient_address_sources** | [**Array&lt;RecipientAddressSource&gt;**](RecipientAddressSource.md) |  |  |
| **job_options** | [**JobOptions**](JobOptions.md) |  |  |
| **payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] |
| **tags** | **Array&lt;String&gt;** |  | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::SingleDocJobParamsRequest.new(
  document_source_identifier: null,
  recipient_address_sources: null,
  job_options: null,
  payment_details: null,
  tags: null
)
```

