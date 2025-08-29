# File Type Detection Methods in finspect

## Overview

The finspect application employs a multi-layered approach to file type detection, prioritizing content-based analysis over file extensions for enhanced security and accuracy. The detection system uses a hierarchical fallback mechanism to ensure reliable file identification.

## Detection Methods Hierarchy

### 1. Primary Method: libmagic Integration
- **Library**: `python-magic` (when available)
- **Confidence**: 100%
- **Features**:
  - Most accurate file type detection
  - Returns both MIME type and human-readable description
  - Leverages the extensive libmagic database
  - Preferred method when the library is installed

### 2. Magic Byte Signature Detection
- **Location**: `detect.py` (lines 23-61)
- **Confidence**: 90-100% depending on signature uniqueness
- **Supported Formats**:

#### Document Formats
- **PDF**: Signature `%PDF-` (starts at byte 0)
- **RTF**: Signature `{\rtf` (starts at byte 0)

#### Image Formats
- **PNG**: Signature `\x89PNG\r\n\x1a\n`
- **JPEG**: Signatures `\xff\xd8\xff` (multiple variants)
- **GIF**: Signatures `GIF87a`, `GIF89a`
- **BMP**: Signature `BM`
- **ICO**: Signature `\x00\x00\x01\x00`

#### Archive Formats
- **ZIP**: Signature `PK\x03\x04` (includes OOXML, ODT, JAR)
- **GZIP**: Signature `\x1f\x8b`
- **TAR**: Signature `ustar` at offset 257
- **RAR**: Signature `Rar!\x1a\x07\x00`
- **7-Zip**: Signature `7z\xbc\xaf\x27\x1c`

#### Audio/Video Formats
- **MP3**: ID3 tag signatures (`ID3`)
- **MP4**: Signature `ftyp` at offset 4
- **WAV**: Signature `RIFF` + `WAVE` at offset 8
- **Ogg**: Signature `OggS`

#### Executable Formats
- **Windows EXE/DLL**: Signature `MZ`
- **ELF**: Signature `\x7fELF`
- **Mach-O**: Signatures for 32/64-bit variants

#### Office Formats
- **Legacy MS Office**: Signature `\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1`

### 3. Byte Order Mark (BOM) Detection
- **Location**: `detect.py` (lines 64-70)
- **Purpose**: Identify text encoding
- **Supported BOMs**:
  - UTF-8: `\xef\xbb\xbf`
  - UTF-16 LE: `\xff\xfe`
  - UTF-16 BE: `\xfe\xff`
  - UTF-32 LE: `\xff\xfe\x00\x00`
  - UTF-32 BE: `\x00\x00\xfe\xff`

### 4. Text Content Analysis
- **Function**: `_is_text_content()`
- **Method**: Statistical analysis of byte patterns
- **Confidence**: 60-90% based on printable character ratio
- **Process**:
  - Counts printable vs non-printable characters
  - Calculates ratio to determine likelihood of text
  - Higher ratio of printable characters increases confidence

### 5. Structured Text Detection
- **Function**: `_detect_structured_text()`
- **Supported Formats**:
  - **JSON**: Detects `{...}` or `[...]` patterns
  - **XML**: Detects `<?xml` declaration or tag patterns
  - **CSV**: Analyzes comma consistency across lines
- **Confidence**: Varies based on pattern strength

### 6. Container/Archive Inspection
- **Module**: `zipscan.py`
- **Features**:
  - Recursive ZIP content inspection
  - OOXML format detection (docx, xlsx, pptx)
  - ODF format detection (odt, ods, odp)
  - Security limits on file sizes and entry counts

## Detection Flow

```
1. Read file header (default: 8192 bytes)
   ↓
2. Attempt libmagic detection (if available)
   ↓ (fallback if unavailable)
3. Check against magic byte signatures
   ↓ (if no match)
4. Analyze for text content
   ↓ (if text detected)
5. Check for structured text formats
   ↓ (if still unknown)
6. Default to application/octet-stream
   ↓ (if ZIP detected)
7. Optional: Inspect container contents
```

## Key Implementation Details

### Security Features
- **No Extension Trust**: File extensions are completely ignored
- **Content-Based Only**: All detection based on actual file content
- **Size Limits**: Protection against malicious large files
- **Safe Defaults**: Unknown files default to `application/octet-stream`

### Confidence Scoring
- Each detection method returns a confidence percentage
- Higher confidence methods take precedence
- Multiple detection sources are tracked for transparency

### Performance Considerations
- Header reading limited to necessary bytes (default 8192)
- Lazy evaluation of detection methods
- Optional deep inspection for containers

## Usage Example

The detection system is typically accessed through the main detection interface:

```python
mime_type, confidence, sources = detect_file_type(file_path)
```

Where:
- `mime_type`: The detected MIME type
- `confidence`: Detection confidence (0-100%)
- `sources`: List of detection methods that contributed

## Extensibility

The modular design allows for easy addition of new detection methods:
1. Add new magic signatures to the signature dictionary
2. Implement new detection functions following the existing pattern
3. Integrate into the detection hierarchy with appropriate confidence levels

This architecture ensures finspect can accurately identify files while maintaining security and performance standards.