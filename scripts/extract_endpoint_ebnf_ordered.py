#!/usr/bin/env python3
"""
Extract Ordered EBNF Data Dictionaries for Each Endpoint
========================================================

This utility extracts EBNF productions used by each endpoint in a 
logical top-down order, where each referenced element appears 
immediately after it's first used.

Usage:
    python extract_endpoint_ebnf_ordered.py data_dictionary/c2mapiv2-dd.ebnf [-o output.txt]

Output:
    An ordered EBNF data dictionary for each endpoint.
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import OrderedDict

# Import the existing EBNF translator to leverage its parsing
sys.path.append(str(Path(__file__).parent))
from ebnf_to_openapi_dynamic_v2 import (
    EBNFToOpenAPITranslator, 
    EBNFProduction
)


class OrderedEndpointEBNFExtractor:
    """Extracts ordered EBNF data dictionaries for each endpoint"""
    
    def __init__(self):
        self.translator = EBNFToOpenAPITranslator()
        self.ebnf_lines: Dict[str, List[str]] = {}  # production name -> original EBNF lines
        self.comments: Dict[str, str] = {}  # production name -> associated comment
        
    def analyze_file(self, filepath: str) -> Dict[str, str]:
        """Analyze EBNF file and return ordered dictionaries for each endpoint"""
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Parse to get productions
        self.translator.parse_ebnf(content)
        
        # Extract original EBNF definitions and comments
        self._extract_original_definitions(content)
        
        # Map endpoints to their parameter productions
        endpoint_to_params = self._map_endpoints_to_params(content)
        
        # Build ordered dictionaries for each endpoint
        endpoint_dictionaries = {}
        
        for endpoint_path, param_name in endpoint_to_params.items():
            if param_name in self.translator.productions:
                # Build the ordered dictionary
                ordered_dict = self._build_ordered_dictionary(
                    endpoint_path, 
                    param_name
                )
                endpoint_dictionaries[endpoint_path] = ordered_dict
        
        return endpoint_dictionaries
    
    def _extract_original_definitions(self, content: str):
        """Extract the original EBNF definitions from the file"""
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines and pure comments
            if not line.strip() or (line.strip().startswith('(*') and line.strip().endswith('*)')):
                i += 1
                continue
            
            # Look for production definitions
            match = re.match(r'^(\w+)\s*=', line)
            if match:
                prod_name = match.group(1)
                definition_lines = []
                
                # Check for preceding comment
                if i > 0 and '(*' in lines[i-1]:
                    comment_match = re.search(r'\(\*\s*(.+?)\s*\*\)', lines[i-1])
                    if comment_match:
                        self.comments[prod_name] = comment_match.group(1)
                
                # Collect all lines of this production (until we find ';')
                j = i
                while j < len(lines):
                    definition_lines.append(lines[j])
                    if ';' in lines[j]:
                        break
                    j += 1
                
                self.ebnf_lines[prod_name] = definition_lines
                i = j + 1
            else:
                i += 1
    
    def _map_endpoints_to_params(self, content: str) -> Dict[str, str]:
        """Map endpoint paths to their parameter production names"""
        lines = content.split('\n')
        endpoint_to_params = {}
        
        endpoint_pattern = r'Endpoint:\s*(?:GET|POST|PUT|DELETE|PATCH)\s+(/[\w/\-{}]+)'
        
        for i, line in enumerate(lines):
            match = re.search(endpoint_pattern, line, re.IGNORECASE)
            if match:
                endpoint_path = match.group(1)
                
                # Look for the production immediately following
                for j in range(i + 1, min(i + 10, len(lines))):
                    if lines[j].strip() and not lines[j].strip().startswith('*)'):
                        prod_match = re.match(r'^(\w+)\s*=', lines[j])
                        if prod_match:
                            param_name = prod_match.group(1)
                            endpoint_to_params[endpoint_path] = param_name
                            break
        
        return endpoint_to_params
    
    def _extract_direct_symbols(self, production_name: str) -> List[str]:
        """Extract symbols directly referenced in a production's definition"""
        if production_name not in self.translator.productions:
            return []
        
        production = self.translator.productions[production_name]
        symbols = []
        
        # Extract symbols in the order they appear
        def extract_ordered(expr):
            if isinstance(expr, dict):
                expr_type = expr.get('type')
                
                if expr_type == 'symbol':
                    name = expr.get('name')
                    if name and isinstance(name, str):
                        symbols.append(name)
                
                elif expr_type == 'concatenation':
                    # Process items in order
                    for item in expr.get('items', []):
                        extract_ordered(item)
                
                elif expr_type == 'alternation':
                    # Process choices
                    for choice in expr.get('choices', []):
                        extract_ordered(choice)
                
                elif expr_type in ['optional', 'repeat']:
                    # Process nested expression
                    extract_ordered(expr.get('expression'))
            
            elif isinstance(expr, list):
                for item in expr:
                    extract_ordered(item)
        
        extract_ordered(production.expression)
        
        # Return unique symbols in order of first appearance
        seen = set()
        ordered_symbols = []
        for symbol in symbols:
            if symbol not in seen and symbol in self.translator.productions:
                seen.add(symbol)
                ordered_symbols.append(symbol)
        
        return ordered_symbols
    
    def _build_ordered_dictionary(self, endpoint_path: str, 
                                 main_production: str) -> str:
        """Build an ordered EBNF dictionary for an endpoint"""
        lines = []
        included = set()
        
        # Header
        lines.append(f"(* ===== Ordered Data Dictionary for {endpoint_path} ===== *)")
        lines.append(f"(* Main production: {main_production} *)")
        lines.append("")
        
        # Recursive function to add productions in order
        def add_production(prod_name: str, indent: int = 0):
            if prod_name in included or prod_name not in self.ebnf_lines:
                return
            
            included.add(prod_name)
            
            # Add comment if exists
            if prod_name in self.comments and indent == 0:
                lines.append(f"(* {self.comments[prod_name]} *)")
            
            # Add the production definition
            for line in self.ebnf_lines[prod_name]:
                lines.append(line)
            
            lines.append("")  # Empty line after production
            
            # Get direct dependencies and add them
            dependencies = self._extract_direct_symbols(prod_name)
            for dep in dependencies:
                add_production(dep, indent + 1)
        
        # Start with the main production
        add_production(main_production)
        
        return '\n'.join(lines).strip()
    
    def format_all_endpoints(self, endpoint_dictionaries: Dict[str, str]) -> str:
        """Format all endpoint ordered dictionaries"""
        lines = ["# Endpoint Ordered EBNF Data Dictionaries", ""]
        lines.append("This document contains ordered EBNF data dictionaries for each API endpoint.")
        lines.append("Each referenced element appears immediately after its first use.")
        lines.append("")
        
        for endpoint_path in sorted(endpoint_dictionaries.keys()):
            lines.append(f"## {endpoint_path}")
            lines.append("")
            lines.append("```ebnf")
            lines.append(endpoint_dictionaries[endpoint_path])
            lines.append("```")
            lines.append("")
        
        # Add summary
        lines.append("## Summary")
        lines.append("")
        
        # Count unique productions per endpoint
        production_counts = {}
        for endpoint_path, ordered_dict in endpoint_dictionaries.items():
            # Count productions in the dictionary
            count = len(re.findall(r'^\w+\s*=', ordered_dict, re.MULTILINE))
            production_counts[endpoint_path] = count
        
        lines.append("### Production Count by Endpoint")
        lines.append("")
        for endpoint, count in sorted(production_counts.items()):
            lines.append(f"- {endpoint}: {count} productions")
        
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Extract ordered EBNF data dictionaries for each endpoint"
    )
    parser.add_argument("input", help="Input EBNF file")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("-f", "--format", choices=["ebnf", "markdown"], 
                       default="markdown", help="Output format")
    
    args = parser.parse_args()
    
    # Check input file
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Extract
    extractor = OrderedEndpointEBNFExtractor()
    try:
        endpoint_dictionaries = extractor.analyze_file(args.input)
    except Exception as e:
        print(f"Error analyzing file: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Format output
    if args.format == "markdown":
        output = extractor.format_all_endpoints(endpoint_dictionaries)
    else:  # ebnf
        # Just concatenate all ordered dictionaries
        output = "\n\n".join(
            f"(* ========== {endpoint} ========== *)\n{ordered_dict}"
            for endpoint, ordered_dict in sorted(endpoint_dictionaries.items())
        )
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Ordered dictionaries written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()