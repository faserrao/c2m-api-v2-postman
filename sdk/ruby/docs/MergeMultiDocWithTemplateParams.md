# OpenapiClient::MergeMultiDocWithTemplateParams

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **documents_to_merge** | [**Array&lt;DocumentSourceIdentifier&gt;**](DocumentSourceIdentifier.md) |  |  |
| **recipient_address_source** | [**RecipientAddressSource**](RecipientAddressSource.md) |  |  |
| **job_template** | **String** |  |  |
| **payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] |
| **tags** | **Array&lt;String&gt;** |  | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::MergeMultiDocWithTemplateParams.new(
  documents_to_merge: null,
  recipient_address_source: null,
  job_template: null,
  payment_details: null,
  tags: null
)
```

