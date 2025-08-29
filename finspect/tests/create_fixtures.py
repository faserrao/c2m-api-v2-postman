#!/usr/bin/env python3
"""Create test fixtures for finspect tests."""

import os
import json
import zipfile
from pathlib import Path


def create_fixtures():
    """Create test fixture files."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    
    # PDF file (minimal header)
    with open(fixtures_dir / "sample.pdf", "wb") as f:
        f.write(b"%PDF-1.5\n%\xE2\xE3\xCF\xD3\n")
        f.write(b"1 0 obj\n<< /Type /Catalog >>\nendobj\n")
        f.write(b"xref\n0 2\n0000000000 65535 f\n")
        f.write(b"trailer\n<< /Size 2 >>\nstartxref\n9\n%%EOF\n")
    
    # PNG file (minimal valid PNG)
    png_data = (
        b'\x89PNG\r\n\x1a\n'  # PNG signature
        b'\x00\x00\x00\rIHDR'  # IHDR chunk
        b'\x00\x00\x00\x01\x00\x00\x00\x01'  # 1x1 pixel
        b'\x08\x02\x00\x00\x00'  # 8-bit RGB
        b'\x90wS\xde'  # CRC
        b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05'  # IDAT chunk
        b'\x00\x00\x00\x00IEND\xaeB`\x82'  # IEND chunk
    )
    with open(fixtures_dir / "sample.png", "wb") as f:
        f.write(png_data)
    
    # JPEG file (minimal JPEG)
    jpeg_data = (
        b'\xff\xd8\xff\xe0'  # SOI + APP0
        b'\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07'
        b'\xff\xd9'  # EOI
    )
    with open(fixtures_dir / "sample.jpg", "wb") as f:
        f.write(jpeg_data)
    
    # Plain text file
    with open(fixtures_dir / "sample.txt", "w", encoding="utf-8") as f:
        f.write("This is a plain text file.\nIt contains ASCII text.\n")
    
    # JSON file
    data = {"name": "test", "value": 42, "items": ["a", "b", "c"]}
    with open(fixtures_dir / "sample.json", "w") as f:
        json.dump(data, f, indent=2)
    
    # XML file
    with open(fixtures_dir / "sample.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<root>\n  <item>Test</item>\n</root>\n')
    
    # RTF file
    with open(fixtures_dir / "sample.rtf", "w") as f:
        f.write(r'{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}')
        f.write(r'\f0\fs24 Hello, World!\par}')
    
    # ZIP archive with multiple files
    with zipfile.ZipFile(fixtures_dir / "archive.zip", "w") as zf:
        zf.writestr("test.txt", "Hello from ZIP")
        zf.write(fixtures_dir / "sample.pdf", "sample.pdf")
        zf.write(fixtures_dir / "sample.png", "sample.png")
    
    # Empty file
    (fixtures_dir / "empty.file").touch()
    
    # Binary file with no clear signature
    with open(fixtures_dir / "binary.dat", "wb") as f:
        f.write(b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f' * 16)
    
    print(f"Created fixtures in {fixtures_dir}")


if __name__ == "__main__":
    create_fixtures()