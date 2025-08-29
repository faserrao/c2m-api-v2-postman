"""File Type Inspector CLI - A secure, fast tool for detecting true file types."""

from .detect import detect_file, detect_bytes
from .zipscan import inspect_zip
from .models import DetectionResult, EntryResult, MimeGuess

__version__ = "1.0.0"
__all__ = ["detect_file", "detect_bytes", "inspect_zip", "DetectionResult", "EntryResult", "MimeGuess"]