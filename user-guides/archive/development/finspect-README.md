# finspect - File Type Inspector CLI

A secure, fast CLI tool that detects the true file type by inspecting magic bytes and content heuristics, not just file extensions.

## Features

- **True file type detection** using libmagic and fallback signatures
- **Container inspection** - looks inside ZIP archives (including DOCX, XLSX, ODT)
- **Directory processing** - analyze entire directories with HTML/JSON reports
- **Human-readable and JSON output** formats
- **Security-first design** - safe limits, no extraction to disk
- **Fast operation** - reads only file headers (8KB by default)
- **Cross-platform** - works on Linux, macOS, and Windows

## Installation

### From source

```bash
cd finspect
pip install -e .
```

### With development dependencies

```bash
pip install -e ".[dev]"
```

## Quick Start

```bash
# Inspect a single file
finspect document.pdf

# Inspect a ZIP archive
finspect archive.zip

# JSON output
finspect mystery.bin --json

# Show detection sources
finspect file.dat --show-sources

# Skip libmagic (use fallback)
finspect file.bin --no-libmagic

# Process current directory
finspect .

# Process directory recursively
finspect . --recursive
```

## Usage

```
finspect <path> [options]

Options:
  --json                Output machine-readable JSON (single files only)
  --bytes N             Number of bytes to sniff (default: 8192)
  --max-depth D         Recursion depth for containers (default: 1)
  --follow-symlinks     Follow symbolic links
  --show-sources        Include detection evidence
  --strict              Exit non-zero if any container entry is unknown
  --timeout MS          Soft per-file read timeout
  --no-libmagic         Force fallback detector

Directory Options:
  --recursive, -r       Process directories recursively
  --include-hidden      Include hidden files (starting with .)
  --report-format TYPE  Report format: json, html, or both (default: both)
  --quiet, -q           Suppress progress output
```

## Examples

### Basic file detection

```bash
$ finspect invoice.pdf
File: invoice.pdf
Type: application/pdf (PDF document)
Confidence: 100
Size: 245.3 KB
```

### Container inspection

```bash
$ finspect report.docx
File: report.docx
Type: application/zip (ZIP archive)
Confidence: 100
Size: 1.2 MB

Container: application/zip (ZIP archive)
Inferred container format: application/vnd.openxmlformats-officedocument.wordprocessingml.document

Entries:
  - [Content_Types].xml                   -> application/xml (confidence 90)
  - _rels/.rels                          -> application/xml (confidence 90)
  - word/document.xml                    -> application/xml (confidence 90)
  - word/styles.xml                      -> application/xml (confidence 90)
```

### JSON output

```bash
$ finspect archive.zip --json
{
  "tool": "finspect",
  "version": "1.0.0",
  "path": "archive.zip",
  "size_bytes": 45678,
  "is_container": true,
  "media_type": "application/zip",
  "description": "ZIP archive",
  "confidence": 100,
  "sources": {
    "libmagic": "application/zip",
    "magic_bytes": "504b0304"
  },
  "entries": [
    {"name": "document.pdf", "media_type": "application/pdf", "confidence": 100},
    {"name": "image.png", "media_type": "image/png", "confidence": 100}
  ],
  "warnings": [],
  "errors": []
}
```

### Directory processing

```bash
# Process all files in a directory
$ finspect /path/to/directory
Processing 42 files in /path/to/directory...
  ✓ document.pdf: application/pdf
  ✓ image.png: image/png
  ✓ data.json: application/json
  ...

Processed 42 files
Reports generated:
  - /path/to/directory/finspect_report_20240115_143022.json
  - /path/to/directory/finspect_report_20240115_143022.html

# Process directory recursively
$ finspect /path/to/directory --recursive

# Process only specific report format
$ finspect /path/to/directory --report-format html

# Include hidden files
$ finspect /path/to/directory --include-hidden

# Quiet mode (no progress output)
$ finspect /path/to/directory --quiet
```

The HTML report provides:
- Summary statistics with file type distribution
- High/low confidence counts
- Container file detection
- Detailed table with all files and their detected types
- Visual confidence indicators

## Supported Formats

### Binary Formats
- PDF documents
- Images: PNG, JPEG, GIF, BMP, ICO
- Archives: ZIP, GZIP, TAR, RAR, 7Z
- Audio/Video: MP3, MP4, WAV, OGG
- Executables: EXE, ELF, Mach-O

### Text Formats
- Plain text (with encoding detection)
- JSON documents
- XML documents
- CSV files
- RTF documents

### Container Formats
- ZIP archives
- Microsoft Office (DOCX, XLSX, PPTX)
- OpenDocument (ODT, ODS, ODP)

## Exit Codes

- `0` - Success
- `2` - File not found or unreadable
- `3` - Unknown file type (top-level)
- `4` - Container read error
- `5` - Timeout or partial read failure
- `6` - Strict mode violation

## Security Features

- **No file extraction** - reads only in memory
- **Size limits** - configurable byte limits
- **Entry limits** - max 10,000 ZIP entries
- **No symlink following** by default
- **Timeout support** for large files
- **ZIP bomb protection** - limited decompression

## Python API

```python
from finspect import detect_file, detect_bytes

# Detect from file path
result = detect_file("/path/to/file.pdf")
print(f"Type: {result.media_type}")
print(f"Confidence: {result.confidence}")

# Detect from bytes
with open("file.bin", "rb") as f:
    data = f.read(8192)
result = detect_bytes(data)
```

## Development

### Running tests

```bash
pytest tests/
```

### Code formatting

```bash
black finspect/
ruff check finspect/
```

### Type checking

```bash
mypy finspect/
```

## License

MIT License - see LICENSE file for details.