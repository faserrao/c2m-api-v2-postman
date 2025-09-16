# Finspect File Type Detection Methods

## Overview

This document describes the technical methods used by Finspect to detect and validate file types for financial documents processed through the C2M API v2 system.

## Detection Methods

### 1. Magic Number Detection

The primary method uses file magic numbers (file signatures) to identify file types:

- **PDF**: `%PDF-` (0x25504446)
- **PNG**: `\x89PNG\r\n\x1a\n`
- **JPEG**: `\xFF\xD8\xFF`
- **TIFF**: `II*\x00` or `MM\x00*`

### 2. MIME Type Analysis

Secondary validation through MIME type headers:
- Examines Content-Type headers in HTTP uploads
- Validates against expected MIME types for financial documents
- Cross-references with magic number findings

### 3. Extension Validation

Tertiary check for file extensions:
- Maps common extensions to expected file types
- Used as hint, not primary detection method
- Helps identify misnamed files

### 4. Content Structure Analysis

For text-based formats:
- XML structure validation for electronic documents
- JSON schema validation for structured data
- CSV format detection for tabular data

## Supported Financial Document Types

### Primary Formats
1. **PDF** - Most common for statements, invoices
2. **Image Formats** (PNG, JPEG, TIFF) - Scanned documents
3. **XML** - Electronic data interchange
4. **JSON** - API-based document uploads

### Special Handling

#### Multi-page Documents
- PDF page count detection
- TIFF multi-page support
- Page separation markers for batch processing

#### Encrypted Documents
- Detection of password-protected PDFs
- Encryption type identification
- Appropriate error messaging

## Integration Points

### API Upload Validation
```javascript
// Example validation flow
validateDocument(file) {
  const fileType = detectFileType(file);
  if (!isSupported(fileType)) {
    throw new ValidationError(`Unsupported file type: ${fileType}`);
  }
  return fileType;
}
```

### Preprocessing Pipeline
1. File type detection
2. Format-specific validation
3. Metadata extraction
4. Content preparation for mail processing

## Performance Considerations

- Magic number detection reads only first few bytes
- Caching of detection results for batch processing
- Async processing for large files
- Memory-efficient streaming for content analysis

## Error Handling

### Common Detection Errors
1. **Corrupted Files**: Partial magic numbers
2. **Mismatched Extensions**: File extension doesn't match content
3. **Unknown Formats**: Unrecognized file signatures
4. **Empty Files**: Zero-byte uploads

### Error Responses
The system provides specific error codes for each detection failure:
- `INVALID_FILE_TYPE`: File type not supported
- `CORRUPTED_FILE`: File structure damaged
- `DETECTION_FAILED`: Unable to determine file type
- `FILE_TOO_LARGE`: Exceeds processing limits

## Security Considerations

- Prevents execution of malicious files
- Validates against injection attacks
- Sanitizes file names and metadata
- Enforces file size limits

## Future Enhancements

Planned improvements to detection methods:
1. Machine learning-based content classification
2. OCR integration for scanned document validation
3. Blockchain verification for document authenticity
4. Advanced encryption support

---

*Technical Component of Finspect Utilities*  
*Part of C2M API v2 System*