# OpenapiClient::DefaultApi

All URIs are relative to *https://api.example.com/v1*

| Method | HTTP request | Description |
| ------ | ------------ | ----------- |
| [**merge_multi_doc_params**](DefaultApi.md#merge_multi_doc_params) | **POST** /jobs/multi-doc-merge | Operation for /jobs/multi-doc-merge |
| [**merge_multi_doc_with_template_params**](DefaultApi.md#merge_multi_doc_with_template_params) | **POST** /jobs/multi-doc-merge-job-template | Operation for /jobs/multi-doc-merge-job-template |
| [**multi_pdf_with_capture_params**](DefaultApi.md#multi_pdf_with_capture_params) | **POST** /jobs/multi-pdf-address-capture | Operation for /jobs/multi-pdf-address-capture |
| [**single_doc_job_params**](DefaultApi.md#single_doc_job_params) | **POST** /jobs/single-doc | Operation for /jobs/single-doc |
| [**split_pdf_params**](DefaultApi.md#split_pdf_params) | **POST** /jobs/single-pdf-split | Operation for /jobs/single-pdf-split |
| [**split_pdf_with_capture_params**](DefaultApi.md#split_pdf_with_capture_params) | **POST** /jobs/single-pdf-split-addressCapture | Operation for /jobs/single-pdf-split-addressCapture |
| [**submit_multi_doc_params**](DefaultApi.md#submit_multi_doc_params) | **POST** /jobs/multi-doc | Operation for /jobs/multi-doc |
| [**submit_multi_doc_with_template_params**](DefaultApi.md#submit_multi_doc_with_template_params) | **POST** /jobs/multi-docs-job-template | Operation for /jobs/multi-docs-job-template |
| [**submit_single_doc_with_template_params**](DefaultApi.md#submit_single_doc_with_template_params) | **POST** /jobs/single-doc-job-template | Operation for /jobs/single-doc-job-template |


## merge_multi_doc_params

> <StandardResponse> merge_multi_doc_params(merge_multi_doc_params_request)

Operation for /jobs/multi-doc-merge

### Examples

```ruby
require 'time'
require 'openapi_client'
# setup authorization
OpenapiClient.configure do |config|
  # Configure Bearer authorization (JWT): bearerAuth
  config.access_token = 'YOUR_BEARER_TOKEN'
end

api_instance = OpenapiClient::DefaultApi.new
merge_multi_doc_params_request = OpenapiClient::MergeMultiDocParamsRequest.new({documents_to_merge: [OpenapiClient::DocumentSourceIdentifierOneOf.new({upload_request_id: 37, document_name: 'document_name_example'})], recipient_address_source: nil}) # MergeMultiDocParamsRequest | 

begin
  # Operation for /jobs/multi-doc-merge
  result = api_instance.merge_multi_doc_params(merge_multi_doc_params_request)
  p result
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->merge_multi_doc_params: #{e}"
end
```

#### Using the merge_multi_doc_params_with_http_info variant

This returns an Array which contains the response data, status code and headers.

> <Array(<StandardResponse>, Integer, Hash)> merge_multi_doc_params_with_http_info(merge_multi_doc_params_request)

```ruby
begin
  # Operation for /jobs/multi-doc-merge
  data, status_code, headers = api_instance.merge_multi_doc_params_with_http_info(merge_multi_doc_params_request)
  p status_code # => 2xx
  p headers # => { ... }
  p data # => <StandardResponse>
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->merge_multi_doc_params_with_http_info: #{e}"
end
```

### Parameters

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **merge_multi_doc_params_request** | [**MergeMultiDocParamsRequest**](MergeMultiDocParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## merge_multi_doc_with_template_params

> <StandardResponse> merge_multi_doc_with_template_params(merge_multi_doc_with_template_params_request)

Operation for /jobs/multi-doc-merge-job-template

### Examples

```ruby
require 'time'
require 'openapi_client'
# setup authorization
OpenapiClient.configure do |config|
  # Configure Bearer authorization (JWT): bearerAuth
  config.access_token = 'YOUR_BEARER_TOKEN'
end

api_instance = OpenapiClient::DefaultApi.new
merge_multi_doc_with_template_params_request = OpenapiClient::MergeMultiDocWithTemplateParamsRequest.new({documents_to_merge: [OpenapiClient::DocumentSourceIdentifierOneOf.new({upload_request_id: 37, document_name: 'document_name_example'})], recipient_address_source: nil, job_template: 'job_template_example'}) # MergeMultiDocWithTemplateParamsRequest | 

begin
  # Operation for /jobs/multi-doc-merge-job-template
  result = api_instance.merge_multi_doc_with_template_params(merge_multi_doc_with_template_params_request)
  p result
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->merge_multi_doc_with_template_params: #{e}"
end
```

#### Using the merge_multi_doc_with_template_params_with_http_info variant

This returns an Array which contains the response data, status code and headers.

> <Array(<StandardResponse>, Integer, Hash)> merge_multi_doc_with_template_params_with_http_info(merge_multi_doc_with_template_params_request)

```ruby
begin
  # Operation for /jobs/multi-doc-merge-job-template
  data, status_code, headers = api_instance.merge_multi_doc_with_template_params_with_http_info(merge_multi_doc_with_template_params_request)
  p status_code # => 2xx
  p headers # => { ... }
  p data # => <StandardResponse>
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->merge_multi_doc_with_template_params_with_http_info: #{e}"
end
```

### Parameters

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **merge_multi_doc_with_template_params_request** | [**MergeMultiDocWithTemplateParamsRequest**](MergeMultiDocWithTemplateParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## multi_pdf_with_capture_params

> <StandardResponse> multi_pdf_with_capture_params(multi_pdf_with_capture_params_request)

Operation for /jobs/multi-pdf-address-capture

### Examples

```ruby
require 'time'
require 'openapi_client'
# setup authorization
OpenapiClient.configure do |config|
  # Configure Bearer authorization (JWT): bearerAuth
  config.access_token = 'YOUR_BEARER_TOKEN'
end

api_instance = OpenapiClient::DefaultApi.new
multi_pdf_with_capture_params_request = OpenapiClient::MultiPdfWithCaptureParamsRequest.new({address_capture_pdfs: [OpenapiClient::AddressListPdf.new({document_source_identifier: OpenapiClient::DocumentSourceIdentifierOneOf.new({upload_request_id: 37, document_name: 'document_name_example'}), address_list_region: 'address_list_region_example'})], job_template: 'job_template_example'}) # MultiPdfWithCaptureParamsRequest | 

begin
  # Operation for /jobs/multi-pdf-address-capture
  result = api_instance.multi_pdf_with_capture_params(multi_pdf_with_capture_params_request)
  p result
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->multi_pdf_with_capture_params: #{e}"
end
```

#### Using the multi_pdf_with_capture_params_with_http_info variant

This returns an Array which contains the response data, status code and headers.

> <Array(<StandardResponse>, Integer, Hash)> multi_pdf_with_capture_params_with_http_info(multi_pdf_with_capture_params_request)

```ruby
begin
  # Operation for /jobs/multi-pdf-address-capture
  data, status_code, headers = api_instance.multi_pdf_with_capture_params_with_http_info(multi_pdf_with_capture_params_request)
  p status_code # => 2xx
  p headers # => { ... }
  p data # => <StandardResponse>
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->multi_pdf_with_capture_params_with_http_info: #{e}"
end
```

### Parameters

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **multi_pdf_with_capture_params_request** | [**MultiPdfWithCaptureParamsRequest**](MultiPdfWithCaptureParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## single_doc_job_params

> <StandardResponse> single_doc_job_params(single_doc_job_params_request)

Operation for /jobs/single-doc

### Examples

```ruby
require 'time'
require 'openapi_client'
# setup authorization
OpenapiClient.configure do |config|
  # Configure Bearer authorization (JWT): bearerAuth
  config.access_token = 'YOUR_BEARER_TOKEN'
end

api_instance = OpenapiClient::DefaultApi.new
single_doc_job_params_request = OpenapiClient::SingleDocJobParamsRequest.new({document_source_identifier: OpenapiClient::DocumentSourceIdentifierOneOf.new({upload_request_id: 37, document_name: 'document_name_example'}), recipient_address_sources: [nil], job_options: OpenapiClient::JobOptions.new({document_class: OpenapiClient::DocumentClass::BUSINESS_LETTER, layout: OpenapiClient::Layout::PORTRAIT, mailclass: OpenapiClient::Mailclass::FIRST_CLASS_MAIL, paper_type: OpenapiClient::PaperType::LETTER, print_option: OpenapiClient::PrintOption::NONE, envelope: OpenapiClient::Envelope::FLAT})}) # SingleDocJobParamsRequest | 

begin
  # Operation for /jobs/single-doc
  result = api_instance.single_doc_job_params(single_doc_job_params_request)
  p result
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->single_doc_job_params: #{e}"
end
```

#### Using the single_doc_job_params_with_http_info variant

This returns an Array which contains the response data, status code and headers.

> <Array(<StandardResponse>, Integer, Hash)> single_doc_job_params_with_http_info(single_doc_job_params_request)

```ruby
begin
  # Operation for /jobs/single-doc
  data, status_code, headers = api_instance.single_doc_job_params_with_http_info(single_doc_job_params_request)
  p status_code # => 2xx
  p headers # => { ... }
  p data # => <StandardResponse>
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->single_doc_job_params_with_http_info: #{e}"
end
```

### Parameters

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **single_doc_job_params_request** | [**SingleDocJobParamsRequest**](SingleDocJobParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## split_pdf_params

> <StandardResponse> split_pdf_params(split_pdf_params_request)

Operation for /jobs/single-pdf-split

### Examples

```ruby
require 'time'
require 'openapi_client'
# setup authorization
OpenapiClient.configure do |config|
  # Configure Bearer authorization (JWT): bearerAuth
  config.access_token = 'YOUR_BEARER_TOKEN'
end

api_instance = OpenapiClient::DefaultApi.new
split_pdf_params_request = OpenapiClient::SplitPdfParamsRequest.new({document_source_identifier: OpenapiClient::DocumentSourceIdentifierOneOf.new({upload_request_id: 37, document_name: 'document_name_example'}), items: [OpenapiClient::SplitPdfParamsRequestItemsInner.new({page_range: OpenapiClient::PageRange.new({start_page: 37, end_page: 37}), recipient_address_sources: [nil]})]}) # SplitPdfParamsRequest | 

begin
  # Operation for /jobs/single-pdf-split
  result = api_instance.split_pdf_params(split_pdf_params_request)
  p result
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->split_pdf_params: #{e}"
end
```

#### Using the split_pdf_params_with_http_info variant

This returns an Array which contains the response data, status code and headers.

> <Array(<StandardResponse>, Integer, Hash)> split_pdf_params_with_http_info(split_pdf_params_request)

```ruby
begin
  # Operation for /jobs/single-pdf-split
  data, status_code, headers = api_instance.split_pdf_params_with_http_info(split_pdf_params_request)
  p status_code # => 2xx
  p headers # => { ... }
  p data # => <StandardResponse>
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->split_pdf_params_with_http_info: #{e}"
end
```

### Parameters

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **split_pdf_params_request** | [**SplitPdfParamsRequest**](SplitPdfParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## split_pdf_with_capture_params

> <StandardResponse> split_pdf_with_capture_params(split_pdf_with_capture_params_request)

Operation for /jobs/single-pdf-split-addressCapture

### Examples

```ruby
require 'time'
require 'openapi_client'
# setup authorization
OpenapiClient.configure do |config|
  # Configure Bearer authorization (JWT): bearerAuth
  config.access_token = 'YOUR_BEARER_TOKEN'
end

api_instance = OpenapiClient::DefaultApi.new
split_pdf_with_capture_params_request = OpenapiClient::SplitPdfWithCaptureParamsRequest.new({document_source_identifier: OpenapiClient::DocumentSourceIdentifierOneOf.new({upload_request_id: 37, document_name: 'document_name_example'}), embedded_extraction_specs: [OpenapiClient::ExtractionSpec.new({start_page: 37, end_page: 37, address_region: OpenapiClient::AddressRegion.new({x: 3.56, y: 3.56, width: 3.56, height: 3.56, page_offset: 37})})]}) # SplitPdfWithCaptureParamsRequest | 

begin
  # Operation for /jobs/single-pdf-split-addressCapture
  result = api_instance.split_pdf_with_capture_params(split_pdf_with_capture_params_request)
  p result
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->split_pdf_with_capture_params: #{e}"
end
```

#### Using the split_pdf_with_capture_params_with_http_info variant

This returns an Array which contains the response data, status code and headers.

> <Array(<StandardResponse>, Integer, Hash)> split_pdf_with_capture_params_with_http_info(split_pdf_with_capture_params_request)

```ruby
begin
  # Operation for /jobs/single-pdf-split-addressCapture
  data, status_code, headers = api_instance.split_pdf_with_capture_params_with_http_info(split_pdf_with_capture_params_request)
  p status_code # => 2xx
  p headers # => { ... }
  p data # => <StandardResponse>
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->split_pdf_with_capture_params_with_http_info: #{e}"
end
```

### Parameters

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **split_pdf_with_capture_params_request** | [**SplitPdfWithCaptureParamsRequest**](SplitPdfWithCaptureParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## submit_multi_doc_params

> <StandardResponse> submit_multi_doc_params(submit_multi_doc_params_request)

Operation for /jobs/multi-doc

### Examples

```ruby
require 'time'
require 'openapi_client'
# setup authorization
OpenapiClient.configure do |config|
  # Configure Bearer authorization (JWT): bearerAuth
  config.access_token = 'YOUR_BEARER_TOKEN'
end

api_instance = OpenapiClient::DefaultApi.new
submit_multi_doc_params_request = OpenapiClient::SubmitMultiDocParamsRequest.new({items: [OpenapiClient::SubmitMultiDocWithTemplateParamsRequestItemsInner.new({document_source_identifier: OpenapiClient::DocumentSourceIdentifierOneOf.new({upload_request_id: 37, document_name: 'document_name_example'}), recipient_address_source: nil})], job_options: OpenapiClient::JobOptions.new({document_class: OpenapiClient::DocumentClass::BUSINESS_LETTER, layout: OpenapiClient::Layout::PORTRAIT, mailclass: OpenapiClient::Mailclass::FIRST_CLASS_MAIL, paper_type: OpenapiClient::PaperType::LETTER, print_option: OpenapiClient::PrintOption::NONE, envelope: OpenapiClient::Envelope::FLAT})}) # SubmitMultiDocParamsRequest | 

begin
  # Operation for /jobs/multi-doc
  result = api_instance.submit_multi_doc_params(submit_multi_doc_params_request)
  p result
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->submit_multi_doc_params: #{e}"
end
```

#### Using the submit_multi_doc_params_with_http_info variant

This returns an Array which contains the response data, status code and headers.

> <Array(<StandardResponse>, Integer, Hash)> submit_multi_doc_params_with_http_info(submit_multi_doc_params_request)

```ruby
begin
  # Operation for /jobs/multi-doc
  data, status_code, headers = api_instance.submit_multi_doc_params_with_http_info(submit_multi_doc_params_request)
  p status_code # => 2xx
  p headers # => { ... }
  p data # => <StandardResponse>
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->submit_multi_doc_params_with_http_info: #{e}"
end
```

### Parameters

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **submit_multi_doc_params_request** | [**SubmitMultiDocParamsRequest**](SubmitMultiDocParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## submit_multi_doc_with_template_params

> <StandardResponse> submit_multi_doc_with_template_params(submit_multi_doc_with_template_params_request)

Operation for /jobs/multi-docs-job-template

### Examples

```ruby
require 'time'
require 'openapi_client'
# setup authorization
OpenapiClient.configure do |config|
  # Configure Bearer authorization (JWT): bearerAuth
  config.access_token = 'YOUR_BEARER_TOKEN'
end

api_instance = OpenapiClient::DefaultApi.new
submit_multi_doc_with_template_params_request = OpenapiClient::SubmitMultiDocWithTemplateParamsRequest.new({items: [OpenapiClient::SubmitMultiDocWithTemplateParamsRequestItemsInner.new({document_source_identifier: OpenapiClient::DocumentSourceIdentifierOneOf.new({upload_request_id: 37, document_name: 'document_name_example'}), recipient_address_source: nil})], job_template: 'job_template_example', payment_details: OpenapiClient::AchPayment.new({ach_details: OpenapiClient::AchDetails.new({routing_number: 'routing_number_example', account_number: 'account_number_example', check_digit: 37})})}) # SubmitMultiDocWithTemplateParamsRequest | 

begin
  # Operation for /jobs/multi-docs-job-template
  result = api_instance.submit_multi_doc_with_template_params(submit_multi_doc_with_template_params_request)
  p result
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->submit_multi_doc_with_template_params: #{e}"
end
```

#### Using the submit_multi_doc_with_template_params_with_http_info variant

This returns an Array which contains the response data, status code and headers.

> <Array(<StandardResponse>, Integer, Hash)> submit_multi_doc_with_template_params_with_http_info(submit_multi_doc_with_template_params_request)

```ruby
begin
  # Operation for /jobs/multi-docs-job-template
  data, status_code, headers = api_instance.submit_multi_doc_with_template_params_with_http_info(submit_multi_doc_with_template_params_request)
  p status_code # => 2xx
  p headers # => { ... }
  p data # => <StandardResponse>
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->submit_multi_doc_with_template_params_with_http_info: #{e}"
end
```

### Parameters

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **submit_multi_doc_with_template_params_request** | [**SubmitMultiDocWithTemplateParamsRequest**](SubmitMultiDocWithTemplateParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


## submit_single_doc_with_template_params

> <StandardResponse> submit_single_doc_with_template_params(submit_single_doc_with_template_params_request)

Operation for /jobs/single-doc-job-template

### Examples

```ruby
require 'time'
require 'openapi_client'
# setup authorization
OpenapiClient.configure do |config|
  # Configure Bearer authorization (JWT): bearerAuth
  config.access_token = 'YOUR_BEARER_TOKEN'
end

api_instance = OpenapiClient::DefaultApi.new
submit_single_doc_with_template_params_request = OpenapiClient::SubmitSingleDocWithTemplateParamsRequest.new({job_template: 'job_template_example'}) # SubmitSingleDocWithTemplateParamsRequest | 

begin
  # Operation for /jobs/single-doc-job-template
  result = api_instance.submit_single_doc_with_template_params(submit_single_doc_with_template_params_request)
  p result
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->submit_single_doc_with_template_params: #{e}"
end
```

#### Using the submit_single_doc_with_template_params_with_http_info variant

This returns an Array which contains the response data, status code and headers.

> <Array(<StandardResponse>, Integer, Hash)> submit_single_doc_with_template_params_with_http_info(submit_single_doc_with_template_params_request)

```ruby
begin
  # Operation for /jobs/single-doc-job-template
  data, status_code, headers = api_instance.submit_single_doc_with_template_params_with_http_info(submit_single_doc_with_template_params_request)
  p status_code # => 2xx
  p headers # => { ... }
  p data # => <StandardResponse>
rescue OpenapiClient::ApiError => e
  puts "Error when calling DefaultApi->submit_single_doc_with_template_params_with_http_info: #{e}"
end
```

### Parameters

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **submit_single_doc_with_template_params_request** | [**SubmitSingleDocWithTemplateParamsRequest**](SubmitSingleDocWithTemplateParamsRequest.md) |  |  |

### Return type

[**StandardResponse**](StandardResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

