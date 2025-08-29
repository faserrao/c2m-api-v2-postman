"""Core file type detection module with libmagic and fallback."""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Tuple, Dict, Union
import warnings

from .models import DetectionResult, MimeGuess
from .limits import Ceilings, DEFAULT_CEILINGS

# Try to import python-magic
try:
    import magic
    HAS_LIBMAGIC = True
except ImportError:
    HAS_LIBMAGIC = False
    magic = None


# Magic byte signatures for common formats
MAGIC_SIGNATURES = {
    # Document formats
    b'%PDF-': ('application/pdf', 'PDF document', 100),
    b'{\rtf': ('text/rtf', 'Rich Text Format', 95),
    
    # Image formats
    b'\x89PNG\r\n\x1a\n': ('image/png', 'PNG image', 100),
    b'\xff\xd8\xff': ('image/jpeg', 'JPEG image', 100),
    b'GIF87a': ('image/gif', 'GIF image (87a)', 100),
    b'GIF89a': ('image/gif', 'GIF image (89a)', 100),
    b'BM': ('image/bmp', 'BMP image', 90),
    b'\x00\x00\x01\x00': ('image/x-icon', 'ICO icon', 90),
    
    # Archive formats
    b'PK\x03\x04': ('application/zip', 'ZIP archive', 100),
    b'PK\x05\x06': ('application/zip', 'ZIP archive (empty)', 100),
    b'PK\x07\x08': ('application/zip', 'ZIP archive (spanned)', 100),
    b'\x1f\x8b': ('application/gzip', 'GZIP compressed', 100),
    b'ustar': ('application/x-tar', 'TAR archive', 95),  # at offset 257
    b'Rar!\x1a\x07\x00': ('application/x-rar-compressed', 'RAR archive', 100),
    b'7z\xbc\xaf\x27\x1c': ('application/x-7z-compressed', '7-Zip archive', 100),
    
    # Audio/Video formats
    b'ID3': ('audio/mpeg', 'MP3 audio (ID3)', 95),
    b'\xff\xfb': ('audio/mpeg', 'MP3 audio', 90),
    b'\xff\xfa': ('audio/mpeg', 'MP3 audio', 90),
    b'ftyp': ('video/mp4', 'MP4 video', 95),  # at offset 4
    b'RIFF': ('audio/wav', 'WAV audio', 90),  # needs WAVE at offset 8
    b'OggS': ('application/ogg', 'Ogg container', 95),
    
    # Executables
    b'MZ': ('application/x-msdownload', 'MS-DOS/Windows executable', 90),
    b'\x7fELF': ('application/x-executable', 'ELF executable', 100),
    b'\xca\xfe\xba\xbe': ('application/x-mach-binary', 'Mach-O binary', 100),
    b'\xfe\xed\xfa\xce': ('application/x-mach-binary', 'Mach-O binary', 100),
    
    # Office formats (older)
    b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': ('application/vnd.ms-office', 'MS Office document', 90),
}

# UTF BOMs
BOMS = {
    b'\xef\xbb\xbf': 'utf-8-sig',
    b'\xff\xfe': 'utf-16-le',
    b'\xfe\xff': 'utf-16-be',
    b'\xff\xfe\x00\x00': 'utf-32-le',
    b'\x00\x00\xfe\xff': 'utf-32-be',
}


def _check_magic_bytes(data: bytes) -> Optional[MimeGuess]:
    """Check data against known magic byte signatures."""
    # Check BOMs first
    for bom, encoding in BOMS.items():
        if data.startswith(bom):
            return MimeGuess(
                media_type='text/plain',
                description=f'Plain text ({encoding})',
                confidence=90,
                source='bom',
                magic_bytes=bom.hex()
            )
    
    # Check magic signatures
    for magic, (mime, desc, conf) in MAGIC_SIGNATURES.items():
        if data.startswith(magic):
            return MimeGuess(
                media_type=mime,
                description=desc,
                confidence=conf,
                source='magic_bytes',
                magic_bytes=magic.hex()
            )
    
    # Special cases that need offset checks
    if len(data) > 8 and data[4:8] == b'ftyp':
        return MimeGuess(
            media_type='video/mp4',
            description='MP4 video',
            confidence=95,
            source='magic_bytes',
            magic_bytes='ftyp'
        )
    
    if len(data) > 12 and data[:4] == b'RIFF' and data[8:12] == b'WAVE':
        return MimeGuess(
            media_type='audio/wav',
            description='WAV audio',
            confidence=95,
            source='magic_bytes',
            magic_bytes='RIFF...WAVE'
        )
    
    # TAR at offset 257
    if len(data) > 262 and data[257:262] == b'ustar':
        return MimeGuess(
            media_type='application/x-tar',
            description='TAR archive',
            confidence=95,
            source='magic_bytes',
            magic_bytes='ustar@257'
        )
    
    return None


def _is_text_content(data: bytes) -> Tuple[bool, int]:
    """Heuristic to determine if content is text."""
    if not data:
        return False, 0
    
    # Count printable vs non-printable
    printable = 0
    non_printable = 0
    
    for byte in data[:1000]:  # Sample first 1KB
        if 0x20 <= byte <= 0x7E or byte in (0x09, 0x0A, 0x0D):  # ASCII printable + tab/newline
            printable += 1
        elif byte < 0x20 or byte > 0x7F:
            non_printable += 1
    
    total = printable + non_printable
    if total == 0:
        return False, 0
    
    ratio = printable / total
    if ratio > 0.95:
        return True, 90
    elif ratio > 0.80:
        return True, 75
    elif ratio > 0.60:
        return True, 60
    
    return False, 0


def _detect_structured_text(data: bytes) -> Optional[MimeGuess]:
    """Detect JSON, XML, and other structured text formats."""
    try:
        text = data.decode('utf-8', errors='ignore').strip()
        if not text:
            return None
        
        # JSON detection
        if text[0] in '{[' and text[-1] in '}]':
            try:
                json.loads(text[:1000])  # Try parsing first 1KB
                return MimeGuess(
                    media_type='application/json',
                    description='JSON document',
                    confidence=85,
                    source='structure'
                )
            except:
                pass
        
        # XML detection
        if text.startswith('<?xml') or (text[0] == '<' and '>' in text[:100]):
            return MimeGuess(
                media_type='application/xml',
                description='XML document',
                confidence=80,
                source='structure'
            )
        
        # CSV detection (simple heuristic)
        lines = text[:500].split('\n')
        if len(lines) > 1:
            first_commas = lines[0].count(',')
            if first_commas > 0 and all(line.count(',') == first_commas for line in lines[1:3] if line):
                return MimeGuess(
                    media_type='text/csv',
                    description='CSV document',
                    confidence=70,
                    source='structure'
                )
    except:
        pass
    
    return None


def detect_buffer(buf: bytes, use_libmagic: bool = True) -> MimeGuess:
    """Detect MIME type from a buffer."""
    if not buf:
        return MimeGuess(
            media_type='application/octet-stream',
            description='Empty file',
            confidence=100,
            source='empty'
        )
    
    # Try libmagic first if available and requested
    if use_libmagic and HAS_LIBMAGIC:
        try:
            mime_magic = magic.Magic(mime=True)
            desc_magic = magic.Magic()
            
            mime_type = mime_magic.from_buffer(buf)
            description = desc_magic.from_buffer(buf)
            
            return MimeGuess(
                media_type=mime_type,
                description=description,
                confidence=100,
                source='libmagic'
            )
        except Exception as e:
            warnings.warn(f"libmagic failed: {e}")
    
    # Fallback detection
    # 1. Check magic bytes
    magic_guess = _check_magic_bytes(buf)
    if magic_guess:
        return magic_guess
    
    # 2. Check if text
    is_text, text_conf = _is_text_content(buf)
    if is_text:
        # Try to detect structured text
        struct_guess = _detect_structured_text(buf)
        if struct_guess:
            return struct_guess
        
        # Plain text
        return MimeGuess(
            media_type='text/plain',
            description='Plain text',
            confidence=text_conf,
            source='heuristic'
        )
    
    # 3. Unknown binary
    return MimeGuess(
        media_type='application/octet-stream',
        description='Binary data',
        confidence=50,
        source='fallback'
    )


def detect_file(
    path: Union[str, Path],
    max_bytes: int = 8192,
    max_depth: int = 1,
    use_libmagic: bool = True,
    follow_symlinks: bool = False,
    ceilings: Optional[Ceilings] = None
) -> DetectionResult:
    """Detect file type for a given path."""
    if ceilings is None:
        ceilings = DEFAULT_CEILINGS
    
    path = Path(path)
    result = DetectionResult(path=str(path))
    
    # Check if file exists
    if not path.exists():
        result.errors.append("File not found")
        return result
    
    # Handle symlinks
    if path.is_symlink() and not follow_symlinks:
        result.errors.append("Symlink not followed (use --follow-symlinks)")
        return result
    
    # Get file stats
    try:
        stat = path.stat()
        result.size_bytes = stat.st_size
    except Exception as e:
        result.errors.append(f"Cannot stat file: {e}")
        return result
    
    # Check size limits
    if stat.st_size > ceilings.max_file_size:
        result.warnings.append(f"File exceeds size limit ({ceilings.max_file_size} bytes)")
    
    # Read file header
    try:
        bytes_to_read = min(max_bytes, stat.st_size, ceilings.max_bytes_per_file)
        with open(path, 'rb') as f:
            header = f.read(bytes_to_read)
    except Exception as e:
        result.errors.append(f"Cannot read file: {e}")
        return result
    
    # Detect MIME type
    mime_guess = detect_buffer(header, use_libmagic)
    result.media_type = mime_guess.media_type
    result.description = mime_guess.description
    result.confidence = mime_guess.confidence
    
    if mime_guess.source:
        result.sources[mime_guess.source] = mime_guess.media_type
    if mime_guess.magic_bytes:
        result.sources['magic_bytes'] = mime_guess.magic_bytes
    
    # Check if container
    if is_container_zip(mime_guess.media_type, header):
        result.is_container = True
        if max_depth > 0:
            # Import here to avoid circular dependency
            from .zipscan import inspect_zip
            try:
                entries, container_type = inspect_zip(
                    path,
                    bytes_hint=max_bytes,
                    use_libmagic=use_libmagic,
                    ceilings=ceilings
                )
                result.entries = entries
                if container_type:
                    result.container_inference = container_type
            except Exception as e:
                result.errors.append(f"Error inspecting container: {e}")
    
    return result


def detect_bytes(
    data: bytes,
    use_libmagic: bool = True
) -> DetectionResult:
    """Detect file type from bytes."""
    result = DetectionResult()
    result.size_bytes = len(data)
    
    mime_guess = detect_buffer(data, use_libmagic)
    result.media_type = mime_guess.media_type
    result.description = mime_guess.description
    result.confidence = mime_guess.confidence
    
    if mime_guess.source:
        result.sources[mime_guess.source] = mime_guess.media_type
    if mime_guess.magic_bytes:
        result.sources['magic_bytes'] = mime_guess.magic_bytes
    
    return result


def is_container_zip(mime_type: str, header: bytes) -> bool:
    """Check if file is a ZIP container."""
    return (
        mime_type == 'application/zip' or
        header.startswith(b'PK\x03\x04') or
        header.startswith(b'PK\x05\x06') or
        header.startswith(b'PK\x07\x08')
    )