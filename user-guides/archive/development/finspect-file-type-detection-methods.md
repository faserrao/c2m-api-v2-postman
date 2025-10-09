# File Type Detection Methods — Comprehensive Guide

## Overview

This document provides both a general guide to file type detection techniques and specific implementation details for the finspect application. File type detection is critical for security, correct routing, compliance, and developer experience.

## Why File Type Detection Matters

- **Security:** Prevent polyglot files, mismatched extensions, disguised executables, and decompression bombs
- **Correct routing:** Choose the right parser/reader pipeline (PDF vs. image vs. plain text)
- **Compliance:** Enforce allow-lists and content policies
- **Developer Experience:** Provide clear error messages and telemetry when uploads don't match expectations
- **No Extension Trust:** File extensions are completely ignored for security

## Detection Methods Hierarchy

### 1. Filename Extension (Weak Hint)
- **Example:** `.pdf`, `.rtf`, `.txt`
- **Confidence:** 0% (not used by finspect)
- **Pros:** Free, instant
- **Cons:** Trivially spoofed; often wrong; not authoritative
- **Best Practice:** Use as hint only, never as primary validation

### 2. Declared MIME Type (Client/Transport Hint)
- **Source:** HTTP headers like `Content-Type`, multipart part headers
- **Confidence:** 0-20%
- **Pros:** Easy to read; expresses client intent
- **Cons:** Frequently inaccurate or generic (`application/octet-stream`)
- **Best Practice:** Record it, but independently verify via content inspection

### 3. Primary Method: libmagic Integration
- **Library:** `python-magic` (when available)
- **Confidence:** 100%
- **Features:**
  - Most accurate file type detection
  - Returns both MIME type and human-readable description
  - Leverages the extensive libmagic database
  - Battle-tested with wide coverage
- **Implementation:** Preferred method when library is installed

### 4. Magic Byte Signature Detection
- **Location:** `detect.py` (lines 23-61 in finspect)
- **Confidence:** 90-100% depending on signature uniqueness
- **Method:** Inspect first few bytes to identify format

#### Common Signatures Table

| Format | ASCII/Bytes | Hex Signature | MIME Type |
|--------|-------------|---------------|-----------|
| **PDF** | `%PDF-` | `25 50 44 46 2D` | `application/pdf` |
| **RTF** | `{\rtf` | `7B 5C 72 74 66` | `application/rtf` |
| **PNG** | `\x89PNG\r\n\x1a\n` | `89 50 4E 47 0D 0A 1A 0A` | `image/png` |
| **JPEG** | `\xff\xd8\xff` | `FF D8 FF` | `image/jpeg` |
| **GIF** | `GIF87a`/`GIF89a` | `47 49 46 38 37 61` | `image/gif` |
| **ZIP** | `PK\x03\x04` | `50 4B 03 04` | `application/zip` |
| **GZIP** | `\x1f\x8b` | `1F 8B` | `application/gzip` |
| **TAR** | `ustar` at 0x101 | (at offset 257) | `application/x-tar` |
| **RAR** | `Rar!\x1a\x07\x00` | `52 61 72 21 1A 07 00` | `application/x-rar` |
| **7-Zip** | `7z\xbc\xaf\x27\x1c` | `37 7A BC AF 27 1C` | `application/x-7z-compressed` |
| **MP3** | `ID3` | `49 44 33` | `audio/mpeg` |
| **MP4** | `ftyp` at offset 4 | `66 74 79 70` | `video/mp4` |
| **WAV** | `RIFF` + `WAVE` | `52 49 46 46` | `audio/wav` |
| **Ogg** | `OggS` | `4F 67 67 53` | `audio/ogg` |
| **EXE/DLL** | `MZ` | `4D 5A` | `application/x-msdownload` |
| **ELF** | `\x7fELF` | `7F 45 4C 46` | `application/x-elf` |
| **MS Office** | `\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1` | `D0 CF 11 E0` | `application/vnd.ms-office` |
| **BMP** | `BM` | `42 4D` | `image/bmp` |
| **ICO** | `\x00\x00\x01\x00` | `00 00 01 00` | `image/x-icon` |

### 5. Byte Order Mark (BOM) Detection
- **Location:** `detect.py` (lines 64-70 in finspect)
- **Purpose:** Identify text encoding
- **Confidence:** 95% for text files
- **Supported BOMs:**
  - UTF-8: `\xef\xbb\xbf`
  - UTF-16 LE: `\xff\xfe`
  - UTF-16 BE: `\xfe\xff`
  - UTF-32 LE: `\xff\xfe\x00\x00`
  - UTF-32 BE: `\x00\x00\xfe\xff`

### 6. Text Content Analysis
- **Function:** `_is_text_content()` in finspect
- **Method:** Statistical analysis of byte patterns
- **Confidence:** 60-90% based on printable character ratio
- **Process:**
  - Counts printable vs non-printable characters
  - Calculates ratio to determine likelihood of text
  - Higher ratio of printable characters increases confidence
  - Detects null bytes as binary indicator

### 7. Structured Text Detection
- **Function:** `_detect_structured_text()` in finspect
- **Confidence:** 85-90% when patterns match
- **Supported Formats:**
  - **JSON:** Detects `{...}` or `[...]` patterns after whitespace trim
  - **XML:** Detects `<?xml` declaration or `<` tag patterns
  - **CSV:** Analyzes comma/delimiter consistency across lines
  - **HTML:** Checks for common HTML tags

### 8. Container/Archive Inspection
- **Module:** `zipscan.py` in finspect
- **Features:**
  - Recursive ZIP content inspection
  - Security limits on file sizes and entry counts
  - Encrypted entry detection
- **Container-specific detection:**
  - **OOXML** (docx/xlsx/pptx): ZIP with `[Content_Types].xml` and specific folders:
    - `word/` → DOCX → `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
    - `xl/` → XLSX → `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
    - `ppt/` → PPTX → `application/vnd.openxmlformats-officedocument.presentationml.presentation`
  - **ODF** (odt/ods/odp): ZIP with root `mimetype` file containing exact media type

## Detection Flow

```
┌───────────────┐
│ Read N KB     │ (default: 8192 bytes)
└───────┬───────┘
        │
        v
┌─────────────────┐  yes  ┌──────────────┐
│ libmagic avail? ├──────►│ Use result   │
└────────┬────────┘       └──────┬───────┘
         │ no                    │
         v                       v
┌─────────────────────┐  ┌─────────────────┐
│ Check magic bytes   │  │ Merge results   │
└────────┬────────────┘  └─────────────────┘
         │ no match
         v
┌──────────────────┐
│ Analyze for text │
└────────┬─────────┘
         │ if text
         v
┌────────────────────────┐
│ Check structured text  │
└────────┬───────────────┘
         │
         v
┌──────────────────┐  yes  ┌─────────────────────┐
│ Container (ZIP)? ├──────►│ Inspect entries     │
└────────┬─────────┘       │ Apply OOXML/ODF     │
         │ no              │ rules               │
         v                 └──────────┬──────────┘
┌─────────────────────┐              │
│ Default to          │              v
│ octet-stream        │    ┌─────────────────────┐
└─────────────────────┘    │ Final result +      │
                          │ confidence + sources │
                          └─────────────────────┘
```

## Implementation Examples

### Python (finspect/FastAPI pattern)
```python
import magic
from typing import Tuple, List

ALLOWED_TYPES = {"application/pdf", "text/plain", "application/zip"}

def detect_file_type(file_path: str) -> Tuple[str, int, List[str]]:
    """
    Returns: (mime_type, confidence, detection_sources)
    """
    with open(file_path, 'rb') as f:
        header = f.read(8192)
    
    sources = []
    
    # Try libmagic first
    if magic_available:
        mime_type = magic.from_buffer(header, mime=True)
        return mime_type, 100, ['libmagic']
    
    # Fall back to magic bytes
    mime_type = check_magic_signatures(header)
    if mime_type:
        return mime_type, 95, ['magic_bytes']
    
    # Check if text
    if is_text_content(header):
        structured = detect_structured_text(header)
        if structured:
            return structured, 85, ['structured_text']
        return 'text/plain', 70, ['text_heuristic']
    
    return 'application/octet-stream', 0, ['unknown']
```

### API Boundary Pattern
```python
async def upload_endpoint(file: UploadFile):
    # Read header for detection
    header = await file.read(8192)
    await file.seek(0)
    
    # Detect type
    sniffed_type, confidence, sources = detect_file_type_from_buffer(header)
    declared_type = file.content_type or "application/octet-stream"
    
    # Log for telemetry
    logger.info({
        "declared": declared_type,
        "sniffed": sniffed_type,
        "confidence": confidence,
        "sources": sources
    })
    
    # Enforce allow-list
    if sniffed_type not in ALLOWED_TYPES:
        raise HTTPException(415, f"Unsupported type: {sniffed_type}")
    
    # Handle mismatches
    if declared_type != sniffed_type and confidence > 80:
        logger.warning("MIME mismatch", extra={
            "declared": declared_type,
            "sniffed": sniffed_type
        })
    
    return {"mediaType": sniffed_type, "confidence": confidence}
```

## Security Considerations

### Resource Limits
- **Header read limit:** Default 8192 bytes, configurable
- **ZIP entry limits:** Max entries, max size per entry
- **Time limits:** Timeout on streaming reads
- **Memory limits:** Stream processing, never load full files

### Security Features
- **No extension trust:** Extensions completely ignored
- **Content-based only:** All detection based on actual content
- **Safe defaults:** Unknown files default to `application/octet-stream`
- **ZIP bomb protection:** Entry count and size limits
- **Encrypted content:** Detection and policy-based handling

### Best Practices
1. Never execute uploaded content
2. Don't shell out with file paths
3. Treat all uploads as untrusted
4. Log mismatches for security monitoring
5. Implement strict resource ceilings
6. Use allow-lists, not deny-lists

## Confidence Scoring Guide

| Detection Method | Confidence Range |
|-----------------|-----------------|
| libmagic exact match | 100% |
| Exact magic byte match | 95-100% |
| Container inspection match | 90-95% |
| Structural parse success | 85-90% |
| Text heuristic match | 70-85% |
| BOM-only detection | 60-70% |
| Unknown/ambiguous | 0% |

## Testing Strategy

Create test fixtures for:
- **Basic formats:** PDF, PNG, JPEG, GIF, plain text
- **Structured text:** Valid JSON, XML, CSV files
- **Office formats:** DOCX, XLSX, PPTX (OOXML)
- **Open formats:** ODT, ODS, ODP (ODF)
- **Archives:** ZIP, TAR, GZIP with various contents
- **Edge cases:**
  - Empty files
  - Truncated files
  - Encrypted ZIPs
  - Files with wrong extensions
  - Polyglot files
  - ZIP bombs (for limit testing)

## Library References

### Python
- `python-magic`: libmagic bindings
- `zipfile`: Standard library ZIP handling
- `chardet`: Character encoding detection

### Node.js
- `file-type`: Pure JS magic byte detection
- `mmmagic`: libmagic bindings
- `yauzl`: ZIP parsing without extraction

### Go
- `net/http.DetectContentType`: Basic built-in
- `h2non/filetype`: Extended detection
- `archive/zip`: Standard library

### Other Tools
- **Apache Tika:** Java-based, comprehensive
- **Unix file command:** Reference implementation
- **TrID:** File identifier with extensive database

## Extensibility

To add new file type detection:

1. **Add magic signature** to the signature dictionary:
   ```python
   SIGNATURES = {
       b'\x89PNG': ('image/png', 100),
       b'%PDF-': ('application/pdf', 100),
       # Add new signature here
   }
   ```

2. **Implement detection function** if needed:
   ```python
   def detect_custom_format(data: bytes) -> Optional[str]:
       # Custom detection logic
       pass
   ```

3. **Integrate into hierarchy** with appropriate confidence level

4. **Add test cases** for the new format

## Quick Reference Checklist

- [ ] Don't trust extensions or client headers alone
- [ ] Use libmagic when available
- [ ] Implement magic byte detection as fallback
- [ ] Add structured text detection for common formats
- [ ] Set resource limits for all operations
- [ ] Log all detections and mismatches
- [ ] Enforce allow-lists at boundaries
- [ ] Handle container formats specially
- [ ] Test with malicious inputs
- [ ] Document confidence levels

This architecture ensures accurate file identification while maintaining security and performance standards.