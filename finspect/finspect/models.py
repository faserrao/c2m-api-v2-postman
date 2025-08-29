"""Data models for finspect."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class MimeGuess:
    """Result of MIME type detection."""
    media_type: str
    description: str
    confidence: int
    source: Optional[str] = None
    magic_bytes: Optional[str] = None


@dataclass
class EntryResult:
    """Result for a single entry in a container."""
    name: str
    media_type: str
    confidence: int
    size_bytes: Optional[int] = None
    is_directory: bool = False
    error: Optional[str] = None


@dataclass
class DetectionResult:
    """Complete detection result for a file."""
    tool: str = "finspect"
    version: str = "1.0.0"
    path: str = ""
    size_bytes: int = 0
    is_container: bool = False
    media_type: str = "application/octet-stream"
    description: str = "Unknown"
    confidence: int = 0
    container_inference: Optional[str] = None
    sources: Dict[str, str] = field(default_factory=dict)
    entries: List[EntryResult] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "tool": self.tool,
            "version": self.version,
            "path": self.path,
            "size_bytes": self.size_bytes,
            "is_container": self.is_container,
            "media_type": self.media_type,
            "description": self.description,
            "confidence": self.confidence,
            "sources": self.sources,
            "warnings": self.warnings,
            "errors": self.errors
        }
        
        if self.container_inference:
            result["container_inference"] = self.container_inference
            
        if self.entries:
            result["entries"] = [
                {
                    "name": e.name,
                    "media_type": e.media_type,
                    "confidence": e.confidence
                } for e in self.entries if not e.is_directory
            ]
            
        return result