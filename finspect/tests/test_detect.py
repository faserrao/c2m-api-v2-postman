"""Tests for detection module."""

import pytest
from pathlib import Path

from finspect.detect import detect_file, detect_buffer, _check_magic_bytes, _is_text_content
from finspect.models import MimeGuess


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestMagicBytes:
    """Test magic byte detection."""
    
    def test_pdf_detection(self):
        result = _check_magic_bytes(b'%PDF-1.5\n')
        assert result is not None
        assert result.media_type == 'application/pdf'
        assert result.confidence == 100
    
    def test_png_detection(self):
        result = _check_magic_bytes(b'\x89PNG\r\n\x1a\n')
        assert result is not None
        assert result.media_type == 'image/png'
        assert result.confidence == 100
    
    def test_jpeg_detection(self):
        result = _check_magic_bytes(b'\xff\xd8\xff')
        assert result is not None
        assert result.media_type == 'image/jpeg'
        assert result.confidence == 100
    
    def test_zip_detection(self):
        result = _check_magic_bytes(b'PK\x03\x04')
        assert result is not None
        assert result.media_type == 'application/zip'
        assert result.confidence == 100
    
    def test_unknown_bytes(self):
        result = _check_magic_bytes(b'\x00\x01\x02\x03')
        assert result is None


class TestTextDetection:
    """Test text content detection."""
    
    def test_ascii_text(self):
        is_text, confidence = _is_text_content(b'Hello, World!\nThis is text.')
        assert is_text is True
        assert confidence >= 90
    
    def test_binary_data(self):
        is_text, confidence = _is_text_content(b'\x00\x01\x02\x03\x04\x05')
        assert is_text is False
    
    def test_mixed_content(self):
        data = b'Text with some \x00\x01 binary'
        is_text, confidence = _is_text_content(data)
        assert is_text is True
        assert confidence < 90


class TestFileDetection:
    """Test file detection with fixtures."""
    
    def test_pdf_file(self):
        pdf_path = FIXTURES_DIR / "sample.pdf"
        if pdf_path.exists():
            result = detect_file(pdf_path, use_libmagic=False)
            assert result.media_type == 'application/pdf'
            assert result.confidence >= 95
            assert not result.is_container
    
    def test_png_file(self):
        png_path = FIXTURES_DIR / "sample.png"
        if png_path.exists():
            result = detect_file(png_path, use_libmagic=False)
            assert result.media_type == 'image/png'
            assert result.confidence >= 95
    
    def test_text_file(self):
        txt_path = FIXTURES_DIR / "sample.txt"
        if txt_path.exists():
            result = detect_file(txt_path, use_libmagic=False)
            assert result.media_type == 'text/plain'
            assert result.confidence >= 70
    
    def test_json_file(self):
        json_path = FIXTURES_DIR / "sample.json"
        if json_path.exists():
            result = detect_file(json_path, use_libmagic=False)
            assert result.media_type in ['application/json', 'text/plain']
            assert result.confidence >= 70
    
    def test_zip_file(self):
        zip_path = FIXTURES_DIR / "archive.zip"
        if zip_path.exists():
            result = detect_file(zip_path, use_libmagic=False, max_depth=0)
            assert result.media_type == 'application/zip'
            assert result.is_container
            assert result.confidence >= 95
    
    def test_empty_file(self):
        empty_path = FIXTURES_DIR / "empty.file"
        if empty_path.exists():
            result = detect_file(empty_path, use_libmagic=False)
            assert result.media_type == 'application/octet-stream'
            assert result.description == 'Empty file'
    
    def test_nonexistent_file(self):
        result = detect_file("/path/that/does/not/exist", use_libmagic=False)
        assert len(result.errors) > 0
        assert "not found" in result.errors[0].lower()


class TestBufferDetection:
    """Test buffer detection."""
    
    def test_detect_pdf_buffer(self):
        result = detect_buffer(b'%PDF-1.5\n', use_libmagic=False)
        assert result.media_type == 'application/pdf'
        assert result.confidence >= 95
    
    def test_detect_text_buffer(self):
        result = detect_buffer(b'Plain text content\n', use_libmagic=False)
        assert result.media_type == 'text/plain'
        assert result.confidence >= 70
    
    def test_detect_json_buffer(self):
        result = detect_buffer(b'{"key": "value"}', use_libmagic=False)
        assert result.media_type in ['application/json', 'text/plain']
    
    def test_detect_empty_buffer(self):
        result = detect_buffer(b'', use_libmagic=False)
        assert result.media_type == 'application/octet-stream'
        assert result.description == 'Empty file'