# OpenAPIClient-php

API for submitting documents with various routing options


## Installation & Usage

### Requirements

PHP 8.1 and later.

### Composer

To install the bindings via [Composer](https://getcomposer.org/), add the following to `composer.json`:

```json
{
  "repositories": [
    {
      "type": "vcs",
      "url": "https://github.com/GIT_USER_ID/GIT_REPO_ID.git"
    }
  ],
  "require": {
    "GIT_USER_ID/GIT_REPO_ID": "*@dev"
  }
}
```

Then run `composer install`

### Manual Installation

Download the files and include `autoload.php`:

```php
<?php
require_once('/path/to/OpenAPIClient-php/vendor/autoload.php');
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');



// Configure Bearer (JWT) authorization: ShortTokenAuth
$config = C2MApi\Configuration::getDefaultConfiguration()->setAccessToken('YOUR_ACCESS_TOKEN');

// Configure API key authorization: ClientKey
$config = C2MApi\Configuration::getDefaultConfiguration()->setApiKey('X-Client-Id', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = C2MApi\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-Client-Id', 'Bearer');


$apiInstance = new C2MApi\Api\AuthApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$long_token_request = {"grant_type":"client_credentials","client_id":"c2m_abc123","client_secret":"supersecret123","scopes":["jobs:submit","templates:read"],"ttl_seconds":7776000}; // \C2MApi\Model\LongTokenRequest

try {
    $result = $apiInstance->issueLongTermToken($long_token_request);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AuthApi->issueLongTermToken: ', $e->getMessage(), PHP_EOL;
}

```

## API Endpoints

All URIs are relative to *https://api.example.com/v1*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AuthApi* | [**issueLongTermToken**](docs/Api/AuthApi.md#issuelongtermtoken) | **POST** /auth/tokens/long | Issue or rotate a long-term token
*AuthApi* | [**issueShortTermToken**](docs/Api/AuthApi.md#issueshorttermtoken) | **POST** /auth/tokens/short | Issue a short-term access token
*AuthApi* | [**revokeToken**](docs/Api/AuthApi.md#revoketoken) | **POST** /auth/tokens/{tokenId}/revoke | Revoke a token
*DefaultApi* | [**mergeMultiDocParams**](docs/Api/DefaultApi.md#mergemultidocparams) | **POST** /jobs/multi-doc-merge | Operation for /jobs/multi-doc-merge
*DefaultApi* | [**mergeMultiDocWithTemplateParams**](docs/Api/DefaultApi.md#mergemultidocwithtemplateparams) | **POST** /jobs/multi-doc-merge-job-template | Operation for /jobs/multi-doc-merge-job-template
*DefaultApi* | [**multiPdfWithCaptureParams**](docs/Api/DefaultApi.md#multipdfwithcaptureparams) | **POST** /jobs/multi-pdf-address-capture | Operation for /jobs/multi-pdf-address-capture
*DefaultApi* | [**singleDocJobParams**](docs/Api/DefaultApi.md#singledocjobparams) | **POST** /jobs/single-doc | Operation for /jobs/single-doc
*DefaultApi* | [**splitPdfParams**](docs/Api/DefaultApi.md#splitpdfparams) | **POST** /jobs/single-pdf-split | Operation for /jobs/single-pdf-split
*DefaultApi* | [**splitPdfWithCaptureParams**](docs/Api/DefaultApi.md#splitpdfwithcaptureparams) | **POST** /jobs/single-pdf-split-addressCapture | Operation for /jobs/single-pdf-split-addressCapture
*DefaultApi* | [**submitMultiDocParams**](docs/Api/DefaultApi.md#submitmultidocparams) | **POST** /jobs/multi-doc | Operation for /jobs/multi-doc
*DefaultApi* | [**submitMultiDocWithTemplateParams**](docs/Api/DefaultApi.md#submitmultidocwithtemplateparams) | **POST** /jobs/multi-docs-job-template | Operation for /jobs/multi-docs-job-template
*DefaultApi* | [**submitSingleDocWithTemplateParams**](docs/Api/DefaultApi.md#submitsingledocwithtemplateparams) | **POST** /jobs/single-doc-job-template | Operation for /jobs/single-doc-job-template

## Models

- [AchDetails](docs/Model/AchDetails.md)
- [AchPayment](docs/Model/AchPayment.md)
- [AddressListPdf](docs/Model/AddressListPdf.md)
- [AddressRegion](docs/Model/AddressRegion.md)
- [ApplePayPayment](docs/Model/ApplePayPayment.md)
- [AuthError](docs/Model/AuthError.md)
- [CardType](docs/Model/CardType.md)
- [CreditAmount](docs/Model/CreditAmount.md)
- [CreditCardDetails](docs/Model/CreditCardDetails.md)
- [CreditCardPayment](docs/Model/CreditCardPayment.md)
- [Currency](docs/Model/Currency.md)
- [Digit](docs/Model/Digit.md)
- [DocumentClass](docs/Model/DocumentClass.md)
- [DocumentFormat](docs/Model/DocumentFormat.md)
- [DocumentSourceIdentifier](docs/Model/DocumentSourceIdentifier.md)
- [DocumentSourceIdentifierOneOf](docs/Model/DocumentSourceIdentifierOneOf.md)
- [DocumentSourceIdentifierOneOf1](docs/Model/DocumentSourceIdentifierOneOf1.md)
- [DocumentSourceIdentifierOneOf2](docs/Model/DocumentSourceIdentifierOneOf2.md)
- [Envelope](docs/Model/Envelope.md)
- [ExpirationDate](docs/Model/ExpirationDate.md)
- [ExtractionSpec](docs/Model/ExtractionSpec.md)
- [GooglePayPayment](docs/Model/GooglePayPayment.md)
- [InvoiceDetails](docs/Model/InvoiceDetails.md)
- [InvoicePayment](docs/Model/InvoicePayment.md)
- [JobOptions](docs/Model/JobOptions.md)
- [Layout](docs/Model/Layout.md)
- [LongTokenRequest](docs/Model/LongTokenRequest.md)
- [LongTokenResponse](docs/Model/LongTokenResponse.md)
- [Mailclass](docs/Model/Mailclass.md)
- [MergeMultiDocParams](docs/Model/MergeMultiDocParams.md)
- [MergeMultiDocParamsRequest](docs/Model/MergeMultiDocParamsRequest.md)
- [MergeMultiDocWithTemplateParams](docs/Model/MergeMultiDocWithTemplateParams.md)
- [MergeMultiDocWithTemplateParamsRequest](docs/Model/MergeMultiDocWithTemplateParamsRequest.md)
- [MultiPdfWithCaptureParams](docs/Model/MultiPdfWithCaptureParams.md)
- [MultiPdfWithCaptureParamsRequest](docs/Model/MultiPdfWithCaptureParamsRequest.md)
- [PageRange](docs/Model/PageRange.md)
- [PaperType](docs/Model/PaperType.md)
- [PaymentDetails](docs/Model/PaymentDetails.md)
- [PrintOption](docs/Model/PrintOption.md)
- [RecipientAddress](docs/Model/RecipientAddress.md)
- [RecipientAddressSource](docs/Model/RecipientAddressSource.md)
- [ShortTokenRequest](docs/Model/ShortTokenRequest.md)
- [ShortTokenResponse](docs/Model/ShortTokenResponse.md)
- [SingleDocJobParams](docs/Model/SingleDocJobParams.md)
- [SingleDocJobParamsRequest](docs/Model/SingleDocJobParamsRequest.md)
- [SplitPdfParams](docs/Model/SplitPdfParams.md)
- [SplitPdfParamsRequest](docs/Model/SplitPdfParamsRequest.md)
- [SplitPdfParamsRequestItemsInner](docs/Model/SplitPdfParamsRequestItemsInner.md)
- [SplitPdfWithCaptureParams](docs/Model/SplitPdfWithCaptureParams.md)
- [SplitPdfWithCaptureParamsRequest](docs/Model/SplitPdfWithCaptureParamsRequest.md)
- [StandardResponse](docs/Model/StandardResponse.md)
- [SubmitMultiDocParams](docs/Model/SubmitMultiDocParams.md)
- [SubmitMultiDocParamsRequest](docs/Model/SubmitMultiDocParamsRequest.md)
- [SubmitMultiDocWithTemplateParams](docs/Model/SubmitMultiDocWithTemplateParams.md)
- [SubmitMultiDocWithTemplateParamsRequest](docs/Model/SubmitMultiDocWithTemplateParamsRequest.md)
- [SubmitMultiDocWithTemplateParamsRequestItemsInner](docs/Model/SubmitMultiDocWithTemplateParamsRequestItemsInner.md)
- [SubmitSingleDocWithTemplateParams](docs/Model/SubmitSingleDocWithTemplateParams.md)
- [SubmitSingleDocWithTemplateParamsRequest](docs/Model/SubmitSingleDocWithTemplateParamsRequest.md)
- [UserCreditPayment](docs/Model/UserCreditPayment.md)

## Authorization

Authentication schemes defined for the API:
### bearerAuth

- **Type**: Bearer authentication (JWT)

### LongTokenAuth

- **Type**: Bearer authentication (JWT)

### ShortTokenAuth

- **Type**: Bearer authentication (JWT)

### ClientKey

- **Type**: API key
- **API key parameter name**: X-Client-Id
- **Location**: HTTP header


## Tests

To run the tests, use:

```bash
composer install
vendor/bin/phpunit
```

## Author



## About this package

This PHP package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: `2.0.0`
    - Generator version: `7.15.0`
- Build package: `org.openapitools.codegen.languages.PhpClientCodegen`
