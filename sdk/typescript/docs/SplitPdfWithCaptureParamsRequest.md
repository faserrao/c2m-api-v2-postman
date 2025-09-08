# SplitPdfWithCaptureParamsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**documentSourceIdentifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  | [default to undefined]
**embeddedExtractionSpecs** | [**Array&lt;ExtractionSpec&gt;**](ExtractionSpec.md) |  | [default to undefined]
**paymentDetails** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { SplitPdfWithCaptureParamsRequest } from './api';

const instance: SplitPdfWithCaptureParamsRequest = {
    documentSourceIdentifier,
    embeddedExtractionSpecs,
    paymentDetails,
    tags,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
