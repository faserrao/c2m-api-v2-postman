# SingleDocJobParamsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**documentSourceIdentifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | [default to undefined]
**recipientAddressSources** | [**Array&lt;RecipientAddressSource&gt;**](RecipientAddressSource.md) |  | [default to undefined]
**jobOptions** | [**JobOptions**](JobOptions.md) |  | [default to undefined]
**paymentDetails** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { SingleDocJobParamsRequest } from './api';

const instance: SingleDocJobParamsRequest = {
    documentSourceIdentifier,
    recipientAddressSources,
    jobOptions,
    paymentDetails,
    tags,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
