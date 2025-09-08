# MergeMultiDocWithTemplateParamsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**documentsToMerge** | [**Array&lt;DocumentSourceIdentifier&gt;**](DocumentSourceIdentifier.md) |  | [default to undefined]
**recipientAddressSource** | [**RecipientAddressSource**](RecipientAddressSource.md) |  | [default to undefined]
**jobTemplate** | **string** |  | [default to undefined]
**paymentDetails** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { MergeMultiDocWithTemplateParamsRequest } from './api';

const instance: MergeMultiDocWithTemplateParamsRequest = {
    documentsToMerge,
    recipientAddressSource,
    jobTemplate,
    paymentDetails,
    tags,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
