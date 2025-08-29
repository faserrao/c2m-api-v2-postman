"""Tests for CLI module."""

import json
import subprocess
import sys
from pathlib import Path
from io import StringIO

import pytest

from finspect.cli import parse_args, determine_exit_code, main
from finspect.models import DetectionResult


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestArgParsing:
    """Test argument parsing."""
    
    def test_basic_args(self):
        sys.argv = ['finspect', 'test.pdf']
        args = parse_args()
        assert args.path == 'test.pdf'
        assert args.bytes == 8192
        assert args.max_depth == 1
        assert not args.json
        assert not args.strict
    
    def test_json_flag(self):
        sys.argv = ['finspect', 'test.pdf', '--json']
        args = parse_args()
        assert args.json is True
    
    def test_bytes_option(self):
        sys.argv = ['finspect', 'test.pdf', '--bytes', '4096']
        args = parse_args()
        assert args.bytes == 4096
    
    def test_max_depth_option(self):
        sys.argv = ['finspect', 'test.zip', '--max-depth', '2']
        args = parse_args()
        assert args.max_depth == 2


class TestExitCodes:
    """Test exit code determination."""
    
    def test_success_exit(self):
        result = DetectionResult(
            media_type='application/pdf',
            confidence=100
        )
        assert determine_exit_code(result, strict=False) == 0
    
    def test_file_not_found_exit(self):
        result = DetectionResult()
        result.errors.append("File not found")
        assert determine_exit_code(result, strict=False) == 2
    
    def test_unknown_type_exit(self):
        result = DetectionResult(
            media_type='application/octet-stream',
            confidence=0
        )
        assert determine_exit_code(result, strict=False) == 3
    
    def test_container_error_exit(self):
        result = DetectionResult(is_container=True)
        result.errors.append("Invalid ZIP file")
        assert determine_exit_code(result, strict=False) == 4
    
    def test_strict_mode_violation(self):
        result = DetectionResult(is_container=True)
        result.entries.append(
            type('Entry', (), {'confidence': 0, 'error': None})()
        )
        assert determine_exit_code(result, strict=True) == 6


class TestCLIIntegration:
    """Test CLI integration."""
    
    @pytest.mark.skipif(not FIXTURES_DIR.exists(), reason="Fixtures not created")
    def test_cli_pdf_detection(self):
        """Test CLI with PDF file."""
        pdf_path = FIXTURES_DIR / "sample.pdf"
        if pdf_path.exists():
            cmd = [sys.executable, '-m', 'finspect.cli', str(pdf_path), '--no-libmagic']
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0
            assert 'application/pdf' in result.stdout
    
    @pytest.mark.skipif(not FIXTURES_DIR.exists(), reason="Fixtures not created") 
    def test_cli_json_output(self):
        """Test CLI JSON output."""
        txt_path = FIXTURES_DIR / "sample.txt"
        if txt_path.exists():
            cmd = [sys.executable, '-m', 'finspect.cli', str(txt_path), '--json', '--no-libmagic']
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0
            
            # Parse JSON output
            try:
                data = json.loads(result.stdout)
                assert data['tool'] == 'finspect'
                assert 'media_type' in data
                assert 'confidence' in data
            except json.JSONDecodeError:
                pytest.fail("Invalid JSON output")
    
    @pytest.mark.skipif(not FIXTURES_DIR.exists(), reason="Fixtures not created")
    def test_cli_nonexistent_file(self):
        """Test CLI with non-existent file."""
        cmd = [sys.executable, '-m', 'finspect.cli', '/does/not/exist.txt']
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 2  # File not found