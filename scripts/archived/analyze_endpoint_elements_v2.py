#!/usr/bin/env python3
"""
Endpoint Element Analyzer v2 - Using Existing EBNF Translator
=============================================================

This utility leverages the existing ebnf_to_openapi_dynamic_v2.py translator
to analyze the EBNF data dictionary and break down each endpoint into its 
constituent elements in a hierarchical format.

Usage:
    python analyze_endpoint_elements_v2.py data_dictionary/c2mapiv2-dd.ebnf [-o output.txt]

Output:
    A hierarchical breakdown of each endpoint showing all constituent elements
    with their types and descriptions.
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import json

# Import the existing EBNF translator
sys.path.append(str(Path(__file__).parent))
from ebnf_to_openapi_dynamic_v2 import (
    EBNFToOpenAPITranslator, 
    EBNFProduction,
    TypeInfo,
    Endpoint
)


@dataclass
class ElementBreakdown:
    """Represents the hierarchical breakdown of an element"""
    name: str
    element_type: str  # 'object', 'array', 'string', 'integer', 'enum', etc.
    required: bool = True
    description: Optional[str] = None
    enum_values: Optional[List[str]] = None
    children: List['ElementBreakdown'] = field(default_factory=list)
    reference_path: List[str] = field(default_factory=list)  # Path to this element


class EndpointElementAnalyzer:
    """Analyzes EBNF endpoints using the existing translator"""
    
    def __init__(self):
        self.translator = EBNFToOpenAPITranslator()
        self.breakdown_cache: Dict[str, ElementBreakdown] = {}
    
    def analyze_file(self, filepath: str) -> Dict[str, ElementBreakdown]:
        """Analyze EBNF file and return endpoint breakdowns"""
        # Use the existing translator to parse
        with open(filepath, 'r') as f:
            content = f.read()
        
        self.translator.parse_ebnf(content)
        
        # Map endpoints to their parameter productions
        endpoint_to_params = self._map_endpoints_to_params(content)
        
        # Build breakdowns for each endpoint
        endpoint_breakdowns = {}
        
        for endpoint_path, param_name in endpoint_to_params.items():
            if param_name in self.translator.productions:
                breakdown = self._build_breakdown_from_production(
                    param_name, 
                    [endpoint_path]
                )
                endpoint_breakdowns[endpoint_path] = breakdown
        
        return endpoint_breakdowns
    
    def _map_endpoints_to_params(self, content: str) -> Dict[str, str]:
        """Map endpoint paths to their parameter production names"""
        lines = content.split('\n')
        endpoint_to_params = {}
        
        # Pattern to find endpoint comments
        endpoint_pattern = r'Endpoint:\s*(?:GET|POST|PUT|DELETE|PATCH)\s+(/[\w/\-{}]+)'
        
        for i, line in enumerate(lines):
            match = re.search(endpoint_pattern, line, re.IGNORECASE)
            if match:
                endpoint_path = match.group(1)
                
                # Look for the production immediately following the endpoint comment
                # Skip empty lines and closing comment lines
                for j in range(i + 1, min(i + 10, len(lines))):
                    if lines[j].strip() and not lines[j].strip().startswith('*)'):
                        # Check if this line has a production definition
                        prod_match = re.match(r'^(\w+)\s*=', lines[j])
                        if prod_match:
                            param_name = prod_match.group(1)
                            endpoint_to_params[endpoint_path] = param_name
                            break
        
        return endpoint_to_params
    
    def _build_breakdown_from_production(self, production_name: str, 
                                       path: List[str], 
                                       visited: Optional[Set[str]] = None) -> ElementBreakdown:
        """Build breakdown from a production"""
        if visited is None:
            visited = set()
        
        # Check cache
        cache_key = f"{production_name}:{':'.join(path)}"
        if cache_key in self.breakdown_cache:
            return self.breakdown_cache[cache_key]
        
        # Prevent circular references
        if production_name in visited:
            return ElementBreakdown(
                name=production_name,
                element_type="circular_reference",
                description=f"Circular reference to {production_name}",
                reference_path=path
            )
        
        visited.add(production_name)
        
        # Get production from translator
        if production_name not in self.translator.productions:
            # Try to resolve as a type
            type_info = self.translator._resolve_type(production_name)
            breakdown = self._type_info_to_breakdown(production_name, type_info, path)
        else:
            production = self.translator.productions[production_name]
            breakdown = self._analyze_production(production, path, visited)
        
        self.breakdown_cache[cache_key] = breakdown
        visited.remove(production_name)
        return breakdown
    
    def _analyze_production(self, production: EBNFProduction, 
                           path: List[str], 
                           visited: Set[str]) -> ElementBreakdown:
        """Analyze a production and return its breakdown"""
        breakdown = ElementBreakdown(
            name=production.name,
            element_type="object",
            reference_path=path
        )
        
        # Analyze the expression
        self._analyze_expression(
            production.expression, 
            breakdown, 
            path + [production.name],
            visited
        )
        
        return breakdown
    
    def _analyze_expression(self, expr: Any, parent: ElementBreakdown, 
                           path: List[str], visited: Set[str]):
        """Analyze an expression and add children to parent"""
        if isinstance(expr, dict):
            expr_type = expr.get('type')
            
            if expr_type == 'symbol':
                # It's a reference to another element
                child = self._build_breakdown_from_production(
                    expr['name'], 
                    path,
                    visited
                )
                parent.children.append(child)
            
            elif expr_type == 'alternation':
                # Check if it's an enum
                if self._is_enum(expr['choices']):
                    parent.element_type = "enum"
                    parent.enum_values = [
                        choice['value'] for choice in expr['choices']
                        if choice.get('type') in ['literal', 'number']
                    ]
                else:
                    # It's a oneOf
                    parent.element_type = "oneOf"
                    for i, choice in enumerate(expr['choices']):
                        child = ElementBreakdown(
                            name=f"option_{i+1}",
                            element_type="object",
                            reference_path=path + [f"option_{i+1}"]
                        )
                        self._analyze_expression(choice, child, path + [f"option_{i+1}"], visited)
                        parent.children.append(child)
            
            elif expr_type == 'concatenation':
                # Multiple fields
                for i, item in enumerate(expr['items']):
                    self._analyze_expression(item, parent, path, visited)
            
            elif expr_type == 'optional':
                # Create a child and mark as optional
                temp_parent = ElementBreakdown(
                    name="temp",
                    element_type="object",
                    reference_path=path
                )
                self._analyze_expression(expr['expression'], temp_parent, path, visited)
                for child in temp_parent.children:
                    child.required = False
                    parent.children.append(child)
            
            elif expr_type == 'repeat':
                # It's an array
                item_name = f"{parent.name}_items"
                item_breakdown = ElementBreakdown(
                    name=item_name,
                    element_type="array_item",
                    reference_path=path + ["[]"]
                )
                self._analyze_expression(expr['expression'], item_breakdown, path + ["[]"], visited)
                
                array_breakdown = ElementBreakdown(
                    name=f"{parent.name}_array",
                    element_type="array",
                    reference_path=path,
                    children=[item_breakdown]
                )
                parent.children.append(array_breakdown)
            
            elif expr_type == 'literal':
                parent.children.append(ElementBreakdown(
                    name=expr['value'],
                    element_type="constant",
                    description=f"Literal: '{expr['value']}'",
                    reference_path=path
                ))
    
    def _type_info_to_breakdown(self, name: str, type_info: TypeInfo, 
                               path: List[str]) -> ElementBreakdown:
        """Convert TypeInfo to ElementBreakdown"""
        breakdown = ElementBreakdown(
            name=name,
            element_type=type_info.openapi_type,
            reference_path=path
        )
        
        if type_info.enum_values:
            breakdown.element_type = "enum"
            breakdown.enum_values = type_info.enum_values
        
        if type_info.format:
            breakdown.description = f"Format: {type_info.format}"
        
        return breakdown
    
    def _is_enum(self, choices: List[Any]) -> bool:
        """Check if alternation represents an enum"""
        return all(
            isinstance(choice, dict) and 
            choice.get('type') in ['literal', 'number']
            for choice in choices
        )
    
    def format_breakdown(self, breakdown: ElementBreakdown, indent: int = 0) -> str:
        """Format breakdown as indented text"""
        lines = []
        prefix = "  " * indent
        
        # Format the element
        type_str = f"[{breakdown.element_type}]"
        req_str = "" if breakdown.required else " (optional)"
        desc_str = f" - {breakdown.description}" if breakdown.description else ""
        
        lines.append(f"{prefix}{breakdown.name} {type_str}{req_str}{desc_str}")
        
        # Add enum values if present
        if breakdown.enum_values:
            lines.append(f"{prefix}  Values: {', '.join(repr(v) for v in breakdown.enum_values)}")
        
        # Add children
        for child in breakdown.children:
            lines.append(self.format_breakdown(child, indent + 1))
        
        return "\n".join(lines)
    
    def format_as_markdown(self, breakdowns: Dict[str, ElementBreakdown]) -> str:
        """Format all breakdowns as markdown"""
        lines = ["# Endpoint Element Breakdown", ""]
        lines.append("This document shows the hierarchical breakdown of each API endpoint's data elements.")
        lines.append("Generated using the dynamic EBNF to OpenAPI translator.")
        lines.append("")
        
        for endpoint_path in sorted(breakdowns.keys()):
            breakdown = breakdowns[endpoint_path]
            
            # Find the method from the endpoint data
            method = "POST"  # Default
            for ep in self.translator.endpoints:
                if ep.path == endpoint_path:
                    method = ep.method
                    break
            
            lines.append(f"## {method} {endpoint_path}")
            lines.append("")
            
            # Add description if available
            endpoint_info = next((ep for ep in self.translator.endpoints if ep.path == endpoint_path), None)
            if endpoint_info and endpoint_info.parameter_name in self.translator.productions:
                prod = self.translator.productions[endpoint_info.parameter_name]
                if hasattr(prod, 'comment') and prod.comment:
                    lines.append(f"*{prod.comment}*")
                    lines.append("")
            
            lines.append("### Structure")
            lines.append("```")
            lines.append(self.format_breakdown(breakdown))
            lines.append("```")
            lines.append("")
        
        # Add summary of shared elements
        lines.append("## Shared Elements Summary")
        lines.append("")
        shared = self._find_shared_elements(breakdowns)
        
        # Group by usage count
        usage_groups = defaultdict(list)
        for element_name, endpoints in shared.items():
            if len(endpoints) > 1:
                usage_groups[len(endpoints)].append((element_name, endpoints))
        
        for count in sorted(usage_groups.keys(), reverse=True):
            lines.append(f"### Used in {count} endpoints")
            lines.append("")
            for element_name, endpoints in sorted(usage_groups[count]):
                lines.append(f"**{element_name}**")
                for ep in sorted(endpoints):
                    lines.append(f"- {ep}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _find_shared_elements(self, breakdowns: Dict[str, ElementBreakdown]) -> Dict[str, Set[str]]:
        """Find elements that are shared across multiple endpoints"""
        element_usage = defaultdict(set)
        
        def collect_elements(breakdown: ElementBreakdown, endpoint: str, depth: int = 0):
            # Skip primitives, constants, and top-level
            if depth > 0 and breakdown.element_type not in ['string', 'integer', 'number', 'boolean', 'constant', 'unknown', 'circular_reference']:
                element_usage[breakdown.name].add(endpoint)
            
            for child in breakdown.children:
                collect_elements(child, endpoint, depth + 1)
        
        for endpoint, breakdown in breakdowns.items():
            collect_elements(breakdown, endpoint)
        
        return dict(element_usage)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze EBNF endpoints using the existing dynamic translator"
    )
    parser.add_argument("input", help="Input EBNF file")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("-f", "--format", choices=["text", "markdown", "json"], 
                       default="markdown", help="Output format")
    
    args = parser.parse_args()
    
    # Check input file
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Analyze
    analyzer = EndpointElementAnalyzer()
    try:
        breakdowns = analyzer.analyze_file(args.input)
    except Exception as e:
        print(f"Error analyzing file: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Format output
    if args.format == "json":
        def breakdown_to_dict(bd: ElementBreakdown) -> dict:
            result = {
                'name': bd.name,
                'type': bd.element_type,
                'required': bd.required,
                'path': bd.reference_path
            }
            if bd.description:
                result['description'] = bd.description
            if bd.enum_values:
                result['enum_values'] = bd.enum_values
            if bd.children:
                result['children'] = [breakdown_to_dict(child) for child in bd.children]
            return result
        
        output_dict = {}
        for endpoint, breakdown in breakdowns.items():
            output_dict[endpoint] = breakdown_to_dict(breakdown)
        output = json.dumps(output_dict, indent=2)
    
    elif args.format == "markdown":
        output = analyzer.format_as_markdown(breakdowns)
    
    else:  # text
        lines = []
        for endpoint in sorted(breakdowns.keys()):
            lines.append(f"\n{'='*60}")
            lines.append(f"Endpoint: {endpoint}")
            lines.append('='*60)
            lines.append(analyzer.format_breakdown(breakdowns[endpoint]))
        output = "\n".join(lines)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Analysis written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()