#!/usr/bin/env python3
"""
Endpoint Element Analyzer for EBNF Data Dictionary
==================================================

This utility analyzes the EBNF data dictionary and breaks down each endpoint
into its constituent elements in a hierarchical format. It shows how data
elements are reused across different endpoints.

Usage:
    python analyze_endpoint_elements.py data_dictionary/c2mapiv2-dd.ebnf [-o output.txt]

Output:
    A hierarchical breakdown of each endpoint showing all constituent elements
    with their types and descriptions.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict
import json
import yaml

try:
    from lark import Lark, Transformer, Tree, Token
except ImportError:
    print("Error: lark-parser is required. Install with: pip install lark")
    sys.exit(1)


# EBNF Grammar for parsing
EBNF_GRAMMAR = r"""
    start      : (production ";")+
    
    production : SYMBOL "=" expression
    
    expression : alternation
    
    alternation : concatenation ("|" concatenation)*
    
    concatenation : term ("+" term)*
    
    term       : SYMBOL
               | STRING
               | NUMBER
               | "[" expression "]"        -> optional
               | "(" expression ")"        -> group
               | "{" expression "}"        -> repeat
               
    SYMBOL     : /[A-Za-z_][A-Za-z0-9_]*/
    STRING     : /"[^"]*"/ | /'[^']*'/
    NUMBER     : /\d+/
    
    %import common.WS
    %ignore WS
    %ignore /\(\*.*?\*\)/s
"""


@dataclass
class Element:
    """Represents a parsed element with its definition and metadata"""
    name: str
    definition: Any  # AST node
    line_number: int = 0
    comment: Optional[str] = None
    is_endpoint: bool = False
    endpoint_path: Optional[str] = None
    is_primitive: bool = False
    is_enum: bool = False
    enum_values: List[str] = field(default_factory=list)


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


class EBNFTransformer(Transformer):
    """Transforms Lark parse tree into our AST"""
    
    def start(self, items):
        return items
    
    def production(self, items):
        name = str(items[0])
        expr = items[1]
        return {'name': name, 'expression': expr}
    
    def expression(self, items):
        return items[0]
    
    def alternation(self, items):
        if len(items) == 1:
            return items[0]
        return {"type": "alternation", "choices": items}
    
    def concatenation(self, items):
        if len(items) == 1:
            return items[0]
        return {"type": "concatenation", "items": items}
    
    def term(self, items):
        return items[0]
    
    def optional(self, items):
        return {"type": "optional", "expression": items[0]}
    
    def group(self, items):
        return items[0]
    
    def repeat(self, items):
        return {"type": "repeat", "expression": items[0]}
    
    def SYMBOL(self, token):
        return {"type": "symbol", "name": str(token)}
    
    def STRING(self, token):
        value = str(token)[1:-1]  # Remove quotes
        return {"type": "literal", "value": value}
    
    def NUMBER(self, token):
        return {"type": "number", "value": int(token)}


class EndpointElementAnalyzer:
    """Analyzes EBNF data dictionary to extract endpoint element hierarchies"""
    
    def __init__(self):
        self.parser = Lark(EBNF_GRAMMAR, parser='lalr', transformer=EBNFTransformer())
        self.elements: Dict[str, Element] = {}
        self.endpoints: Dict[str, Element] = {}
        self.comments: Dict[str, str] = {}
        self.breakdown_cache: Dict[str, ElementBreakdown] = {}
        
        # Primitive type mappings
        self.primitive_types = {
            'string', 'integer', 'number', 'boolean', 'id',
            'url', 'uri', 'date', 'datetime', 'email'
        }
        
        # Known endpoints from comments
        self.endpoint_mappings = {
            'singleDocJobParams': '/jobs/single-doc',
            'submitMultiDocParams': '/jobs/multi-doc',
            'mergeMultiDocParams': '/jobs/multi-doc-merge',
            'submitSingleDocWithTemplateParams': '/jobs/single-doc-job-template',
            'submitMultiDocWithTemplateParams': '/jobs/multi-docs-job-template',
            'mergeMultiDocWithTemplateParams': '/jobs/multi-doc-merge-job-template',
            'splitPdfParams': '/jobs/single-pdf-split',
            'splitPdfWithCaptureParams': '/jobs/single-pdf-split-addressCapture',
            'multiPdfWithCaptureParams': '/jobs/multi-pdf-address-capture'
        }
    
    def analyze_file(self, filepath: str) -> Dict[str, ElementBreakdown]:
        """Analyze EBNF file and return endpoint breakdowns"""
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Parse EBNF
        self._parse_ebnf(content)
        
        # Extract endpoints
        self._identify_endpoints()
        
        # Debug output (optional)
        print(f"Found {len(self.elements)} elements total", file=sys.stderr)
        print(f"Found {len(self.endpoints)} endpoints", file=sys.stderr)
        for name, ep in self.endpoints.items():
            print(f"  - {name}: {ep.endpoint_path}", file=sys.stderr)
        
        # Build hierarchical breakdowns for each endpoint
        endpoint_breakdowns = {}
        for endpoint_name, endpoint in self.endpoints.items():
            if endpoint.endpoint_path:
                breakdown = self._build_breakdown(endpoint_name, [endpoint.endpoint_path])
                endpoint_breakdowns[endpoint.endpoint_path] = breakdown
        
        return endpoint_breakdowns
    
    def _parse_ebnf(self, content: str):
        """Parse EBNF content and extract elements"""
        lines = content.split('\n')
        
        # Extract comments FIRST - this populates endpoint_mappings
        self._extract_comments(lines)
        print(f"After extracting comments, endpoint_mappings has {len(self.endpoint_mappings)} entries", file=sys.stderr)
        
        # Parse with Lark
        parsed = self.parser.parse(content)
        
        # Build element dictionary
        for production in parsed:
            if isinstance(production, dict) and 'name' in production:
                element = Element(
                    name=production['name'],
                    definition=production['expression']
                )
                
                # Check if it's an endpoint (after extracting comments)
                if production['name'] in self.endpoint_mappings:
                    element.is_endpoint = True
                    element.endpoint_path = self.endpoint_mappings[production['name']]
                    print(f"Found endpoint: {production['name']} -> {element.endpoint_path}", file=sys.stderr)
                else:
                    if production['name'] in ['singleDocJobParams', 'submitMultiDocParams']:
                        print(f"Not found in mappings: {production['name']}, mappings={list(self.endpoint_mappings.keys())}", file=sys.stderr)
                
                # Add associated comment if any
                if production['name'] in self.comments:
                    element.comment = self.comments[production['name']]
                
                self.elements[production['name']] = element
    
    def _extract_comments(self, lines: List[str]):
        """Extract comments associated with productions"""
        for i, line in enumerate(lines):
            # Look for endpoint comments
            if 'Endpoint:' in line:
                # Match patterns like "Endpoint: POST /jobs/single-doc"
                match = re.search(r'Endpoint:\s*(?:POST|GET|PUT|DELETE)?\s*(/[^\s]+)', line)
                if match:
                    endpoint_path = match.group(1)
                    # Look for the production following this comment
                    for j in range(i + 1, min(i + 10, len(lines))):
                        prod_match = re.match(r'^(\w+)\s*=', lines[j])
                        if prod_match:
                            prod_name = prod_match.group(1)
                            self.endpoint_mappings[prod_name] = endpoint_path
                            # print(f"Mapped {prod_name} to {endpoint_path}", file=sys.stderr)
                            break
            
            # Extract inline comments
            if '(*' in line and '*)' in line and '=' in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    comment_match = re.search(r'\(\*\s*(.+?)\s*\*\)', parts[1])
                    if comment_match and name:
                        self.comments[name] = comment_match.group(1)
    
    def _identify_endpoints(self):
        """Identify endpoint productions"""
        # First, update elements with endpoint information from mappings
        for name in self.endpoint_mappings:
            if name in self.elements:
                self.elements[name].is_endpoint = True
                self.elements[name].endpoint_path = self.endpoint_mappings[name]
        
        # Then collect all endpoints
        for name, element in self.elements.items():
            if element.is_endpoint:
                self.endpoints[name] = element
    
    def _build_breakdown(self, element_name: str, path: List[str], 
                        visited: Optional[Set[str]] = None) -> ElementBreakdown:
        """Build hierarchical breakdown of an element"""
        if visited is None:
            visited = set()
        
        # Check cache
        cache_key = f"{element_name}:{':'.join(path)}"
        if cache_key in self.breakdown_cache:
            return self.breakdown_cache[cache_key]
        
        # Prevent infinite recursion
        if element_name in visited:
            return ElementBreakdown(
                name=element_name,
                element_type="reference",
                description=f"Circular reference to {element_name}",
                reference_path=path
            )
        
        visited.add(element_name)
        
        # Check if primitive
        if element_name.lower() in self.primitive_types:
            breakdown = ElementBreakdown(
                name=element_name,
                element_type=self._get_primitive_type(element_name),
                reference_path=path
            )
            self.breakdown_cache[cache_key] = breakdown
            return breakdown
        
        # Get element definition
        if element_name not in self.elements:
            breakdown = ElementBreakdown(
                name=element_name,
                element_type="unknown",
                description=f"Element '{element_name}' not found in dictionary",
                reference_path=path
            )
            self.breakdown_cache[cache_key] = breakdown
            return breakdown
        
        element = self.elements[element_name]
        breakdown = self._analyze_expression(
            element.definition, 
            element_name,
            path + [element_name],
            visited,
            element.comment
        )
        breakdown.name = element_name
        breakdown.reference_path = path
        
        self.breakdown_cache[cache_key] = breakdown
        visited.remove(element_name)
        return breakdown
    
    def _analyze_expression(self, expr: Any, name: str, path: List[str], 
                           visited: Set[str], comment: Optional[str] = None) -> ElementBreakdown:
        """Analyze an expression and return its breakdown"""
        if isinstance(expr, dict):
            expr_type = expr.get('type')
            
            if expr_type == 'symbol':
                return self._build_breakdown(expr['name'], path, visited)
            
            elif expr_type == 'literal':
                return ElementBreakdown(
                    name=name,
                    element_type="constant",
                    description=f"Literal value: '{expr['value']}'",
                    reference_path=path
                )
            
            elif expr_type == 'number':
                return ElementBreakdown(
                    name=name,
                    element_type="constant",
                    description=f"Numeric value: {expr['value']}",
                    reference_path=path
                )
            
            elif expr_type == 'alternation':
                # Check if it's an enum
                if self._is_enum(expr['choices']):
                    values = [choice['value'] for choice in expr['choices'] 
                             if choice.get('type') in ['literal', 'number']]
                    return ElementBreakdown(
                        name=name,
                        element_type="enum",
                        enum_values=values,
                        description=comment,
                        reference_path=path
                    )
                else:
                    # It's a union type
                    breakdown = ElementBreakdown(
                        name=name,
                        element_type="oneOf",
                        description=comment or "One of the following options",
                        reference_path=path
                    )
                    for i, choice in enumerate(expr['choices']):
                        child = self._analyze_expression(
                            choice, 
                            f"{name}_option_{i+1}",
                            path + [f"option_{i+1}"],
                            visited
                        )
                        breakdown.children.append(child)
                    return breakdown
            
            elif expr_type == 'concatenation':
                # It's an object with multiple fields
                breakdown = ElementBreakdown(
                    name=name,
                    element_type="object",
                    description=comment,
                    reference_path=path
                )
                for i, item in enumerate(expr['items']):
                    child = self._analyze_expression(
                        item,
                        f"{name}_field_{i+1}",
                        path + [f"field_{i+1}"],
                        visited
                    )
                    breakdown.children.append(child)
                return breakdown
            
            elif expr_type == 'optional':
                child = self._analyze_expression(
                    expr['expression'],
                    name,
                    path,
                    visited,
                    comment
                )
                child.required = False
                return child
            
            elif expr_type == 'repeat':
                # It's an array
                item_breakdown = self._analyze_expression(
                    expr['expression'],
                    f"{name}_items",
                    path + ["items"],
                    visited
                )
                return ElementBreakdown(
                    name=name,
                    element_type="array",
                    description=comment or f"Array of {item_breakdown.name}",
                    children=[item_breakdown],
                    reference_path=path
                )
        
        # Default
        return ElementBreakdown(
            name=name,
            element_type="unknown",
            description=str(expr),
            reference_path=path
        )
    
    def _is_enum(self, choices: List[Any]) -> bool:
        """Check if alternation represents an enum"""
        return all(
            isinstance(choice, dict) and 
            choice.get('type') in ['literal', 'number']
            for choice in choices
        )
    
    def _get_primitive_type(self, name: str) -> str:
        """Get the OpenAPI type for a primitive"""
        type_map = {
            'string': 'string',
            'integer': 'integer',
            'number': 'number',
            'boolean': 'boolean',
            'id': 'integer',
            'url': 'string',
            'uri': 'string',
            'date': 'string',
            'datetime': 'string',
            'email': 'string'
        }
        return type_map.get(name.lower(), 'string')
    
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
        lines.append("")
        
        for endpoint_path in sorted(breakdowns.keys()):
            breakdown = breakdowns[endpoint_path]
            lines.append(f"## {endpoint_path}")
            lines.append("")
            lines.append("```")
            lines.append(self.format_breakdown(breakdown))
            lines.append("```")
            lines.append("")
        
        # Add summary of shared elements
        lines.append("## Shared Elements Summary")
        lines.append("")
        shared = self._find_shared_elements(breakdowns)
        
        for element_name, endpoints in sorted(shared.items()):
            if len(endpoints) > 1:
                lines.append(f"### {element_name}")
                lines.append(f"Used in {len(endpoints)} endpoints:")
                for ep in sorted(endpoints):
                    lines.append(f"- {ep}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _find_shared_elements(self, breakdowns: Dict[str, ElementBreakdown]) -> Dict[str, Set[str]]:
        """Find elements that are shared across multiple endpoints"""
        element_usage = defaultdict(set)
        
        def collect_elements(breakdown: ElementBreakdown, endpoint: str):
            # Skip primitives and constants
            if breakdown.element_type not in ['string', 'integer', 'number', 'boolean', 'constant', 'unknown']:
                element_usage[breakdown.name].add(endpoint)
            
            for child in breakdown.children:
                collect_elements(child, endpoint)
        
        for endpoint, breakdown in breakdowns.items():
            collect_elements(breakdown, endpoint)
        
        return dict(element_usage)
    
    def export_as_json(self, breakdowns: Dict[str, ElementBreakdown]) -> str:
        """Export breakdowns as JSON"""
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
        
        output = {}
        for endpoint, breakdown in breakdowns.items():
            output[endpoint] = breakdown_to_dict(breakdown)
        
        return json.dumps(output, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze EBNF data dictionary to extract endpoint element hierarchies"
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
        sys.exit(1)
    
    # Format output
    if args.format == "json":
        output = analyzer.export_as_json(breakdowns)
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