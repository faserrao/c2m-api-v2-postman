"""Command-line interface for finspect."""

import argparse
import sys
import warnings
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from . import __version__
from .detect import detect_file, HAS_LIBMAGIC
from .output import print_human, print_json
from .limits import Ceilings


# Exit codes
EXIT_SUCCESS = 0
EXIT_FILE_NOT_FOUND = 2
EXIT_UNKNOWN_TYPE = 3
EXIT_CONTAINER_ERROR = 4
EXIT_TIMEOUT = 5
EXIT_STRICT_VIOLATION = 6


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog='finspect',
        description='File Type Inspector - Detect true file types by inspecting content',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  finspect document.pdf
  finspect archive.zip --json
  finspect mystery.bin --no-libmagic --show-sources
  finspect nested.zip --max-depth 2
        """
    )
    
    parser.add_argument(
        'path',
        help='Path to file or directory to inspect'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    # Output options
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output machine-readable JSON'
    )
    
    parser.add_argument(
        '--show-sources',
        action='store_true',
        help='Include detection evidence in output'
    )
    
    # Detection options
    parser.add_argument(
        '--bytes',
        type=int,
        default=8192,
        metavar='N',
        help='Number of bytes to sniff (default: 8192)'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=1,
        metavar='D',
        help='Recursion depth for containers (default: 1, 0=no inspection)'
    )
    
    parser.add_argument(
        '--no-libmagic',
        action='store_true',
        help='Force fallback detector (skip libmagic)'
    )
    
    # Security options
    parser.add_argument(
        '--follow-symlinks',
        action='store_true',
        help='Follow symbolic links (default: do not follow)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        metavar='MS',
        help='Soft per-file read timeout in milliseconds'
    )
    
    # Behavior options
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Non-zero exit if any container entry is unknown'
    )
    
    # Directory options
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Process directories recursively'
    )
    
    parser.add_argument(
        '--include-hidden',
        action='store_true',
        help='Include hidden files (starting with .)'
    )
    
    parser.add_argument(
        '--report-format',
        choices=['json', 'html', 'both'],
        default='both',
        help='Report format for directory processing (default: both)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )
    
    return parser.parse_args()


def process_directory(
    dir_path: Path,
    args: argparse.Namespace,
    ceilings: Ceilings
) -> List[Dict[str, Any]]:
    """Process all files in a directory."""
    results = []
    
    # Determine which files to process
    if args.recursive:
        pattern = "**/*"
    else:
        pattern = "*"
    
    files = [f for f in dir_path.glob(pattern) if f.is_file()]
    
    # Sort files for consistent output
    files.sort()
    
    print(f"Processing {len(files)} files in {dir_path}...", file=sys.stderr)
    
    for file_path in files:
        # Skip hidden files unless requested
        if not args.include_hidden and file_path.name.startswith('.'):
            continue
            
        try:
            result = detect_file(
                file_path,
                max_bytes=args.bytes,
                max_depth=args.max_depth,
                use_libmagic=not args.no_libmagic,
                follow_symlinks=args.follow_symlinks,
                ceilings=ceilings
            )
            
            # Convert to dict for report
            result_dict = result.to_dict()
            result_dict['relative_path'] = str(file_path.relative_to(dir_path))
            results.append(result_dict)
            
            # Show progress if not JSON output
            if not args.json and not args.quiet:
                print(f"  ✓ {file_path.name}: {result.media_type}", file=sys.stderr)
                
        except Exception as e:
            error_result = {
                "path": str(file_path),
                "relative_path": str(file_path.relative_to(dir_path)),
                "error": str(e),
                "media_type": "error",
                "confidence": 0
            }
            results.append(error_result)
            
            if not args.json and not args.quiet:
                print(f"  ✗ {file_path.name}: Error - {e}", file=sys.stderr)
    
    return results


def generate_report(
    results: List[Dict[str, Any]],
    output_dir: Path,
    format: str = "both"
) -> List[Path]:
    """Generate report files in the specified directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report_paths = []
    
    # Generate JSON report
    if format in ["json", "both"]:
        json_path = output_dir / f"finspect_report_{timestamp}.json"
        report_data = {
            "tool": "finspect",
            "version": __version__,
            "timestamp": datetime.now().isoformat(),
            "directory": str(output_dir),
            "total_files": len(results),
            "results": results,
            "summary": generate_summary(results)
        }
        
        with open(json_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        report_paths.append(json_path)
    
    # Generate HTML report
    if format in ["html", "both"]:
        html_path = output_dir / f"finspect_report_{timestamp}.html"
        html_content = generate_html_report(results, output_dir)
        
        with open(html_path, 'w') as f:
            f.write(html_content)
        report_paths.append(html_path)
    
    return report_paths


def generate_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics from results."""
    summary = {
        "total_files": len(results),
        "by_type": {},
        "errors": 0,
        "containers": 0,
        "high_confidence": 0,
        "low_confidence": 0
    }
    
    for result in results:
        # Count by type
        media_type = result.get("media_type", "unknown")
        summary["by_type"][media_type] = summary["by_type"].get(media_type, 0) + 1
        
        # Count errors
        if result.get("error") or result.get("errors"):
            summary["errors"] += 1
        
        # Count containers
        if result.get("is_container"):
            summary["containers"] += 1
        
        # Confidence levels
        confidence = result.get("confidence", 0)
        if confidence >= 90:
            summary["high_confidence"] += 1
        elif confidence < 70:
            summary["low_confidence"] += 1
    
    return summary


def generate_html_report(results: List[Dict[str, Any]], output_dir: Path) -> str:
    """Generate HTML report content."""
    summary = generate_summary(results)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>File Type Inspection Report - {output_dir.name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        h2 {{ color: #667eea; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: #f7fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; }}
        .summary-card h3 {{ margin: 0 0 10px 0; color: #4a5568; font-size: 14px; }}
        .summary-card .number {{ font-size: 28px; font-weight: bold; color: #667eea; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #667eea; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; }}
        tr:hover {{ background: #f7fafc; }}
        .confidence-high {{ color: #48bb78; font-weight: bold; }}
        .confidence-med {{ color: #ed8936; }}
        .confidence-low {{ color: #f56565; }}
        .error {{ color: #f56565; font-weight: bold; }}
        .container-badge {{ background: #667eea; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
        .timestamp {{ color: #718096; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>File Type Inspection Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>Directory: <strong>{output_dir}</strong></p>
        
        <h2>Summary</h2>
        <div class="summary">
            <div class="summary-card">
                <h3>Total Files</h3>
                <div class="number">{summary['total_files']}</div>
            </div>
            <div class="summary-card">
                <h3>High Confidence</h3>
                <div class="number">{summary['high_confidence']}</div>
            </div>
            <div class="summary-card">
                <h3>Containers</h3>
                <div class="number">{summary['containers']}</div>
            </div>
            <div class="summary-card">
                <h3>Errors</h3>
                <div class="number">{summary['errors']}</div>
            </div>
        </div>
        
        <h2>File Type Distribution</h2>
        <table>
            <tr>
                <th>Media Type</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
"""
    
    # Sort by count
    type_counts = sorted(summary['by_type'].items(), key=lambda x: x[1], reverse=True)
    total = summary['total_files']
    
    for media_type, count in type_counts:
        percentage = (count / total * 100) if total > 0 else 0
        html += f"""            <tr>
                <td>{media_type}</td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
"""
    
    html += """        </table>
        
        <h2>Detailed Results</h2>
        <table>
            <tr>
                <th>File</th>
                <th>Type</th>
                <th>Confidence</th>
                <th>Size</th>
                <th>Notes</th>
            </tr>
"""
    
    # Sort results by path
    sorted_results = sorted(results, key=lambda x: x.get('relative_path', ''))
    
    for result in sorted_results:
        rel_path = result.get('relative_path', result.get('path', 'unknown'))
        media_type = result.get('media_type', 'unknown')
        confidence = result.get('confidence', 0)
        size_bytes = result.get('size_bytes', 0)
        
        # Format size
        if size_bytes > 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
        elif size_bytes > 1024:
            size_str = f"{size_bytes / 1024:.1f} KB"
        else:
            size_str = f"{size_bytes} B"
        
        # Confidence class
        if confidence >= 90:
            conf_class = "confidence-high"
        elif confidence >= 70:
            conf_class = "confidence-med"
        else:
            conf_class = "confidence-low"
        
        # Notes
        notes = []
        if result.get('is_container'):
            notes.append('<span class="container-badge">Container</span>')
        if result.get('error'):
            notes.append(f'<span class="error">Error: {result["error"]}</span>')
        elif result.get('errors'):
            notes.append(f'<span class="error">{len(result["errors"])} errors</span>')
        
        notes_str = ' '.join(notes) if notes else '-'
        
        html += f"""            <tr>
                <td>{rel_path}</td>
                <td>{media_type}</td>
                <td class="{conf_class}">{confidence}%</td>
                <td>{size_str}</td>
                <td>{notes_str}</td>
            </tr>
"""
    
    html += """        </table>
    </div>
</body>
</html>"""
    
    return html


def determine_exit_code(result, strict: bool) -> int:
    """Determine appropriate exit code based on results."""
    # Check for critical errors first
    if any('not found' in err.lower() for err in result.errors):
        return EXIT_FILE_NOT_FOUND
    
    if any('timeout' in err.lower() for err in result.errors):
        return EXIT_TIMEOUT
    
    if result.is_container and result.errors:
        if any('zip' in err.lower() or 'container' in err.lower() for err in result.errors):
            return EXIT_CONTAINER_ERROR
    
    # Check for unknown types
    if result.confidence == 0 or result.media_type == 'application/octet-stream':
        if not result.is_container:  # Top-level unknown
            return EXIT_UNKNOWN_TYPE
    
    # Strict mode checks
    if strict and result.entries:
        for entry in result.entries:
            if entry.confidence == 0 or entry.error:
                return EXIT_STRICT_VIOLATION
    
    return EXIT_SUCCESS


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    # Check libmagic availability
    if not args.no_libmagic and not HAS_LIBMAGIC:
        warnings.warn(
            "python-magic not available, using fallback detector. "
            "Install with: pip install python-magic"
        )
    
    # Configure ceilings
    ceilings = Ceilings(
        max_bytes_per_file=args.bytes,
        max_recursion_depth=args.max_depth,
        timeout_ms=args.timeout
    )
    
    path = Path(args.path)
    
    # Check if path exists
    if not path.exists():
        print(f"Error: Path '{path}' does not exist", file=sys.stderr)
        return EXIT_FILE_NOT_FOUND
    
    # Handle directory
    if path.is_dir():
        # Cannot use JSON output for directory mode (we generate reports instead)
        if args.json:
            print("Error: --json flag is not supported for directory processing. Use --report-format instead.", file=sys.stderr)
            return EXIT_CONTAINER_ERROR
        
        # Process directory
        results = process_directory(path, args, ceilings)
        
        if not results:
            print("No files found to process.", file=sys.stderr)
            return EXIT_SUCCESS
        
        # Generate reports
        report_paths = generate_report(results, path, args.report_format)
        
        # Summary output
        print(f"\nProcessed {len(results)} files", file=sys.stderr)
        print(f"Reports generated:", file=sys.stderr)
        for report_path in report_paths:
            print(f"  - {report_path}", file=sys.stderr)
        
        # Determine overall exit code
        has_errors = any(r.get('error') or r.get('errors') for r in results)
        if has_errors and args.strict:
            return EXIT_STRICT_VIOLATION
        
        return EXIT_SUCCESS
    
    # Handle single file (existing behavior)
    try:
        result = detect_file(
            args.path,
            max_bytes=args.bytes,
            max_depth=args.max_depth,
            use_libmagic=not args.no_libmagic,
            follow_symlinks=args.follow_symlinks,
            ceilings=ceilings
        )
    except Exception as e:
        # Handle unexpected errors
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_CONTAINER_ERROR
    
    # Output results
    if args.json:
        print_json(result)
    else:
        print_human(result, show_sources=args.show_sources)
    
    # Determine exit code
    return determine_exit_code(result, args.strict)


if __name__ == '__main__':
    sys.exit(main())