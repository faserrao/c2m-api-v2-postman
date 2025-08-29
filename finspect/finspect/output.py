"""Output formatters for finspect."""

import json
import sys
from typing import TextIO

from .models import DetectionResult


def print_human(result: DetectionResult, show_sources: bool = False, file: TextIO = sys.stdout) -> None:
    """Print human-readable output."""
    # Basic file info
    if result.path:
        print(f"File: {result.path}", file=file)
    
    print(f"Type: {result.media_type} ({result.description})", file=file)
    print(f"Confidence: {result.confidence}", file=file)
    
    # Show sources if requested
    if show_sources and result.sources:
        for source, value in result.sources.items():
            print(f"Source: {source} = {value}", file=file)
    
    # Show size
    if result.size_bytes > 0:
        size_mb = result.size_bytes / (1024 * 1024)
        if size_mb > 1:
            print(f"Size: {size_mb:.1f} MB", file=file)
        else:
            print(f"Size: {result.size_bytes} bytes", file=file)
    
    # Container info
    if result.is_container:
        print(f"\nContainer: {result.media_type} ({result.description})", file=file)
        
        if result.container_inference:
            print(f"Inferred container format: {result.container_inference}", file=file)
        
        if result.entries:
            print("\nEntries:", file=file)
            for entry in result.entries:
                if entry.is_directory:
                    continue
                
                prefix = "  - "
                name = entry.name
                if len(name) > 40:
                    name = name[:37] + "..."
                
                line = f"{prefix}{name:<40} -> {entry.media_type} (confidence {entry.confidence})"
                
                if entry.error:
                    line += f" [ERROR: {entry.error}]"
                
                print(line, file=file)
    
    # Warnings and errors
    if result.warnings:
        print("\nWarnings:", file=file)
        for warning in result.warnings:
            print(f"  ! {warning}", file=file)
    
    if result.errors:
        print("\nErrors:", file=file)
        for error in result.errors:
            print(f"  ✗ {error}", file=file)


def print_json(result: DetectionResult, file: TextIO = sys.stdout) -> None:
    """Print JSON output."""
    output = result.to_dict()
    json.dump(output, file, indent=2)
    print(file=file)  # Add newline