"""ZIP container inspection and OOXML/ODF detection."""

import zipfile
from pathlib import Path
from typing import List, Tuple, Optional, Union
import io

from .models import EntryResult
from .detect import detect_buffer
from .limits import Ceilings, DEFAULT_CEILINGS


# OOXML content types
OOXML_TYPES = {
    'word/': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xl/': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'ppt/': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
}

# ODF MIME types (found in mimetype file)
ODF_TYPES = {
    'application/vnd.oasis.opendocument.text': 'ODT document',
    'application/vnd.oasis.opendocument.spreadsheet': 'ODS spreadsheet',
    'application/vnd.oasis.opendocument.presentation': 'ODP presentation',
    'application/vnd.oasis.opendocument.graphics': 'ODG graphics',
}


def _infer_ooxml_type(entries: List[str]) -> Optional[str]:
    """Infer OOXML document type from entry names."""
    has_content_types = '[Content_Types].xml' in entries
    
    if not has_content_types:
        return None
    
    for prefix, mime_type in OOXML_TYPES.items():
        if any(entry.startswith(prefix) for entry in entries):
            return mime_type
    
    return None


def _check_odf_type(zip_file: zipfile.ZipFile) -> Optional[str]:
    """Check for ODF mimetype file."""
    try:
        # ODF stores mimetype as first file, uncompressed
        if 'mimetype' in zip_file.namelist():
            info = zip_file.getinfo('mimetype')
            if info.compress_type == zipfile.ZIP_STORED:  # Uncompressed
                mimetype = zip_file.read('mimetype').decode('ascii').strip()
                if mimetype in ODF_TYPES:
                    return mimetype
    except:
        pass
    
    return None


def inspect_zip(
    path_or_bytes: Union[str, Path, bytes],
    bytes_hint: int = 8192,
    use_libmagic: bool = True,
    ceilings: Optional[Ceilings] = None
) -> Tuple[List[EntryResult], Optional[str]]:
    """
    Inspect ZIP archive contents.
    
    Returns:
        Tuple of (entries list, container type inference)
    """
    if ceilings is None:
        ceilings = DEFAULT_CEILINGS
    
    entries = []
    container_type = None
    bytes_scanned = 0
    
    try:
        # Open ZIP file
        if isinstance(path_or_bytes, bytes):
            zip_buffer = io.BytesIO(path_or_bytes)
            zip_file = zipfile.ZipFile(zip_buffer, 'r')
        else:
            zip_file = zipfile.ZipFile(path_or_bytes, 'r')
        
        # Get entry list
        entry_names = zip_file.namelist()
        
        # Check for ODF first (has specific mimetype file)
        odf_type = _check_odf_type(zip_file)
        if odf_type:
            container_type = odf_type
        
        # Enforce entry count ceiling
        if len(entry_names) > ceilings.max_zip_entries:
            entries.append(
                EntryResult(
                    name=f"[WARNING: {len(entry_names)} entries exceed limit of {ceilings.max_zip_entries}]",
                    media_type="",
                    confidence=0,
                    error="Too many entries"
                )
            )
            entry_names = entry_names[:ceilings.max_zip_entries]
        
        # Process each entry
        for entry_name in entry_names:
            try:
                info = zip_file.getinfo(entry_name)
                
                # Skip directories
                if entry_name.endswith('/'):
                    entries.append(
                        EntryResult(
                            name=entry_name,
                            media_type="",
                            confidence=0,
                            is_directory=True
                        )
                    )
                    continue
                
                # Check budget
                if bytes_scanned >= ceilings.max_total_sniff_bytes:
                    entries.append(
                        EntryResult(
                            name="[TRUNCATED: byte budget exceeded]",
                            media_type="",
                            confidence=0,
                            error="Budget exceeded"
                        )
                    )
                    break
                
                # Check if encrypted
                if info.flag_bits & 0x1:
                    entries.append(
                        EntryResult(
                            name=entry_name,
                            media_type="application/octet-stream",
                            confidence=0,
                            error="Encrypted entry"
                        )
                    )
                    continue
                
                # Read entry header
                read_bytes = min(bytes_hint, info.file_size, ceilings.max_bytes_per_file)
                
                with zip_file.open(info) as entry_file:
                    entry_data = entry_file.read(read_bytes)
                
                bytes_scanned += len(entry_data)
                
                # Detect entry type
                mime_guess = detect_buffer(entry_data, use_libmagic)
                
                entries.append(
                    EntryResult(
                        name=entry_name,
                        media_type=mime_guess.media_type,
                        confidence=mime_guess.confidence,
                        size_bytes=info.file_size
                    )
                )
                
            except Exception as e:
                entries.append(
                    EntryResult(
                        name=entry_name,
                        media_type="application/octet-stream",
                        confidence=0,
                        error=str(e)
                    )
                )
        
        # Try to infer OOXML type if not ODF
        if not container_type:
            container_type = _infer_ooxml_type(entry_names)
        
        zip_file.close()
        
    except zipfile.BadZipFile as e:
        raise ValueError(f"Invalid ZIP file: {e}")
    except Exception as e:
        raise RuntimeError(f"Error reading ZIP: {e}")
    
    return entries, container_type