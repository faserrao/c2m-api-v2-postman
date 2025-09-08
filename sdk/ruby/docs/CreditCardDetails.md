# OpenapiClient::CreditCardDetails

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **card_type** | [**CardType**](CardType.md) |  |  |
| **card_number** | **String** |  |  |
| **expiration_date** | [**ExpirationDate**](ExpirationDate.md) |  |  |
| **cvv** | **Integer** |  |  |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::CreditCardDetails.new(
  card_type: null,
  card_number: null,
  expiration_date: null,
  cvv: null
)
```

