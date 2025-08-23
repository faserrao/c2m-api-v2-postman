#!/usr/bin/env python3
"""
EBNF to OpenAPI Dynamic Translator
----------------------------------
Dynamically converts EBNF data dictionary to OpenAPI 3.0.3 specification.
Actually reads and uses the EBNF type definitions instead of hardcoding.

Features:
- Uses Lark parser for robust EBNF parsing
- Dynamically resolves type chains (e.g., documentId → id → integer)
- Generates schemas based on actual EBNF content
- Comprehensive error reporting
- Handles complex types (oneOf, arrays, objects)
"""

import re
import sys
import json
import yaml
import textwrap
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict
from lark import Lark, Transformer, Tree, Token
import argparse

# ─────────────────────────── EBNF Grammar ───────────────────────────
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

# ─────────────────────────── Data Classes ───────────────────────────
@dataclass
class EBNFProduction:
    """Represents a parsed EBNF production rule"""
    name: str
    expression: Any  # AST node
    line_number: int = 0
    raw_text: str = ""
    
@dataclass
class TypeInfo:
    """Information about a resolved type"""
    openapi_type: str
    format: Optional[str] = None
    enum_values: Optional[List[Any]] = None
    ref: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    required: Optional[List[str]] = None
    items: Optional[Any] = None  # For arrays
    one_of: Optional[List[Any]] = None

@dataclass
class Issue:
    """Represents an issue found during parsing/generation"""
    severity: str  # "error", "warning", "info"
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None

@dataclass
class Endpoint:
    """Represents an API endpoint found in comments"""
    method: str
    path: str
    parameter_name: Optional[str] = None
    line_number: int = 0

# ─────────────────────────── AST Transformer ───────────────────────────
class EBNFTransformer(Transformer):
    """Transforms Lark parse tree into our AST"""
    
    def start(self, items):
        return items
    
    def production(self, items):
        name = str(items[0])
        expr = items[1]
        return EBNFProduction(name=name, expression=expr)
    
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
        # Remove quotes
        value = str(token)[1:-1]
        return {"type": "literal", "value": value}
    
    def NUMBER(self, token):
        return {"type": "number", "value": int(token)}

# ─────────────────────────── Main Translator Class ───────────────────────────
class EBNFToOpenAPITranslator:
    """Main translator class that converts EBNF to OpenAPI"""
    
    def __init__(self):
        self.parser = Lark(EBNF_GRAMMAR, parser='lalr', transformer=EBNFTransformer())
        self.productions: Dict[str, EBNFProduction] = {}
        self.endpoints: List[Endpoint] = []
        self.issues: List[Issue] = []
        self.type_cache: Dict[str, TypeInfo] = {}
        
        # OpenAPI type mappings for primitives
        self.primitive_types = {
            'string': 'string',
            'integer': 'integer',
            'number': 'number',
            'boolean': 'boolean',
            'id': 'integer',  # Special case for your data dictionary
            'url': 'string',
            'uri': 'string',
            'date': 'string',
            'datetime': 'string',
            'email': 'string',
            'phone': 'string',
            'phoneNumber': 'string'
        }
        
        # Format mappings
        self.format_mappings = {
            'url': 'uri',
            'uri': 'uri',
            'date': 'date',
            'datetime': 'date-time',
            'email': 'email'
        }
    
    def parse_ebnf(self, content: str) -> None:
        """Parse EBNF content and extract productions and endpoints"""
        lines = content.splitlines()
        
        # First extract endpoints from comments
        self._extract_endpoints(lines)
        
        # Parse the EBNF
        try:
            ast = self.parser.parse(content)
            
            # Store productions with line numbers
            for prod in ast:
                if isinstance(prod, EBNFProduction):
                    self.productions[prod.name] = prod
                    # Find line number
                    for i, line in enumerate(lines):
                        if re.match(rf'^\s*{prod.name}\s*=', line):
                            prod.line_number = i + 1
                            break
        except Exception as e:
            self.issues.append(Issue(
                severity="error",
                message=f"Failed to parse EBNF: {str(e)}"
            ))
    
    def _extract_endpoints(self, lines: List[str]) -> None:
        """Extract endpoint definitions from comments"""
        endpoint_pattern = r'Endpoint:\s*(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/\-{}]+)'
        
        for i, line in enumerate(lines):
            match = re.search(endpoint_pattern, line, re.IGNORECASE)
            if match:
                self.endpoints.append(Endpoint(
                    method=match.group(1).upper(),
                    path=match.group(2),
                    line_number=i + 1
                ))
    
    def resolve_type(self, name: str, visited: Set[str] = None) -> TypeInfo:
        """Resolve a type name to OpenAPI type info"""
        if visited is None:
            visited = set()
            
        # Check cache
        if name in self.type_cache:
            return self.type_cache[name]
            
        # Check for circular reference
        if name in visited:
            self.issues.append(Issue(
                severity="error",
                message=f"Circular reference detected: {name}"
            ))
            return TypeInfo(openapi_type="string")
            
        visited.add(name)
        
        # Check primitives
        if name.lower() in self.primitive_types:
            type_info = TypeInfo(
                openapi_type=self.primitive_types[name.lower()],
                format=self.format_mappings.get(name.lower())
            )
            self.type_cache[name] = type_info
            return type_info
        
        # Check if it's a defined production
        if name not in self.productions:
            self.issues.append(Issue(
                severity="warning",
                message=f"Undefined type referenced: {name}"
            ))
            return TypeInfo(openapi_type="string")
        
        # Resolve the production
        prod = self.productions[name]
        type_info = self._expression_to_type(prod.expression, visited)
        
        # Cache the result
        self.type_cache[name] = type_info
        return type_info
    
    def _expression_to_type(self, expr: Any, visited: Set[str]) -> TypeInfo:
        """Convert an EBNF expression to OpenAPI type info"""
        if isinstance(expr, dict):
            expr_type = expr.get('type')
            
            if expr_type == 'symbol':
                return self.resolve_type(expr['name'], visited)
            
            elif expr_type == 'literal':
                return TypeInfo(
                    openapi_type="string",
                    enum_values=[expr['value']]
                )
            
            elif expr_type == 'number':
                return TypeInfo(
                    openapi_type="integer",
                    enum_values=[expr['value']]
                )
            
            elif expr_type == 'alternation':
                # Check if it's an enum (all literals)
                choices = expr['choices']
                if self._is_enum(choices):
                    values = []
                    base_type = "string"
                    for choice in choices:
                        if choice['type'] == 'literal':
                            values.append(choice['value'])
                        elif choice['type'] == 'number':
                            values.append(choice['value'])
                            base_type = "integer"
                    return TypeInfo(openapi_type=base_type, enum_values=values)
                else:
                    # It's a oneOf
                    one_of = []
                    for choice in choices:
                        choice_type = self._expression_to_type(choice, visited)
                        if choice_type.ref:
                            one_of.append({"$ref": choice_type.ref})
                        else:
                            schema = {"type": choice_type.openapi_type}
                            if choice_type.properties:
                                schema["properties"] = choice_type.properties
                                if choice_type.required:
                                    schema["required"] = choice_type.required
                            one_of.append(schema)
                    return TypeInfo(openapi_type="oneOf", one_of=one_of)
            
            elif expr_type == 'concatenation':
                # This becomes an object with properties
                properties = OrderedDict()
                required = []
                
                for i, item in enumerate(expr['items']):
                    # Check if it's optional
                    is_optional = False
                    if isinstance(item, dict) and item.get('type') == 'optional':
                        is_optional = True
                        item = item['expression']
                    
                    # Get property name
                    if isinstance(item, dict) and item.get('type') == 'symbol':
                        prop_name = item['name']
                    else:
                        prop_name = f"field_{i}"
                    
                    # Get property type
                    prop_type = self._expression_to_type(item, visited)
                    
                    if prop_type.ref:
                        properties[prop_name] = {"$ref": prop_type.ref}
                    else:
                        schema = {"type": prop_type.openapi_type}
                        if prop_type.format:
                            schema["format"] = prop_type.format
                        if prop_type.enum_values:
                            schema["enum"] = prop_type.enum_values
                        properties[prop_name] = schema
                    
                    if not is_optional:
                        required.append(prop_name)
                
                return TypeInfo(
                    openapi_type="object",
                    properties=properties,
                    required=required if required else None
                )
            
            elif expr_type == 'optional':
                # Just return the inner type - optionality is handled by parent
                return self._expression_to_type(expr['expression'], visited)
            
            elif expr_type == 'repeat':
                # This becomes an array
                item_type = self._expression_to_type(expr['expression'], visited)
                if item_type.ref:
                    items = {"$ref": item_type.ref}
                else:
                    items = {"type": item_type.openapi_type}
                    if item_type.format:
                        items["format"] = item_type.format
                return TypeInfo(openapi_type="array", items=items)
        
        # Default fallback
        return TypeInfo(openapi_type="string")
    
    def _is_enum(self, choices: List[Any]) -> bool:
        """Check if alternation represents an enum"""
        return all(
            isinstance(choice, dict) and 
            choice.get('type') in ['literal', 'number']
            for choice in choices
        )
    
    def generate_openapi(self) -> Dict[str, Any]:
        """Generate the complete OpenAPI specification"""
        # Build schemas
        schemas = OrderedDict()
        
        for name, prod in self.productions.items():
            # Ensure name is a string, not an AST node
            if not isinstance(name, str):
                continue
                
            # Skip lowercase names unless they're used as components
            if name[0].islower() and not self._is_referenced_type(name):
                continue
            
            type_info = self.resolve_type(name)
            
            if type_info.one_of:
                schemas[name] = {"oneOf": type_info.one_of}
            elif type_info.ref:
                schemas[name] = {"$ref": type_info.ref}
            else:
                schema = {"type": type_info.openapi_type}
                if type_info.format:
                    schema["format"] = type_info.format
                if type_info.enum_values:
                    schema["enum"] = type_info.enum_values
                if type_info.properties:
                    schema["properties"] = type_info.properties
                    if type_info.required:
                        schema["required"] = type_info.required
                if type_info.items:
                    schema["items"] = type_info.items
                schemas[name] = schema
        
        # Build paths based on endpoints
        paths = self._generate_paths(schemas)
        
        # Build the complete spec
        spec = OrderedDict([
            ("openapi", "3.0.3"),
            ("info", OrderedDict([
                ("title", "API Generated from EBNF"),
                ("version", "1.0.0"),
                ("description", "API specification dynamically generated from EBNF data dictionary")
            ])),
            ("servers", [{"url": "https://api.example.com"}]),
            ("paths", paths),
            ("components", OrderedDict([
                ("schemas", schemas),
                ("securitySchemes", OrderedDict([
                    ("bearerAuth", OrderedDict([
                        ("type", "http"),
                        ("scheme", "bearer"),
                        ("bearerFormat", "JWT")
                    ]))
                ]))
            ])),
            ("security", [{"bearerAuth": []}])
        ])
        
        return spec
    
    def _is_referenced_type(self, name: str) -> bool:
        """Check if a type is referenced by other types"""
        for prod in self.productions.values():
            if self._references_type(prod.expression, name):
                return True
        return False
    
    def _references_type(self, expr: Any, type_name: str) -> bool:
        """Check if an expression references a type"""
        if isinstance(expr, dict):
            if expr.get('type') == 'symbol' and expr.get('name') == type_name:
                return True
            # Recursively check sub-expressions
            for key, value in expr.items():
                if isinstance(value, list):
                    for item in value:
                        if self._references_type(item, type_name):
                            return True
                elif isinstance(value, dict):
                    if self._references_type(value, type_name):
                        return True
        return False
    
    def _generate_paths(self, schemas: Dict[str, Any]) -> OrderedDict:
        """Generate API paths from endpoints"""
        paths = OrderedDict()
        
        # Map endpoints to their parameter types
        endpoint_params = {}
        for i, endpoint in enumerate(self.endpoints):
            # Try to find the parameter type after this endpoint
            param_name = self._find_parameter_for_endpoint(endpoint)
            if param_name:
                endpoint_params[i] = param_name
        
        # Generate path specifications
        for i, endpoint in enumerate(self.endpoints):
            path = endpoint.path
            method = endpoint.method.lower()
            
            if path not in paths:
                paths[path] = OrderedDict()
            
            operation = OrderedDict([
                ("summary", f"{endpoint.method} {path}"),
                ("operationId", self._generate_operation_id(endpoint.method, path))
            ])
            
            # Add request body if we found a parameter type
            if i in endpoint_params:
                param_type = endpoint_params[i]
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{param_type}"}
                        }
                    }
                }
            
            # Add responses
            operation["responses"] = OrderedDict([
                ("200", {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/StandardResponse"}
                        }
                    }
                }),
                ("400", {"description": "Bad request"}),
                ("401", {"description": "Unauthorized"})
            ])
            
            paths[path][method] = operation
        
        # Add standard response schema if not already defined
        if "StandardResponse" not in schemas:
            schemas["StandardResponse"] = {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        
        return paths
    
    def _find_parameter_for_endpoint(self, endpoint: Endpoint) -> Optional[str]:
        """Find the parameter type defined after an endpoint comment"""
        # Look for the next production after the endpoint line
        for name, prod in self.productions.items():
            if prod.line_number > endpoint.line_number:
                # Check if it looks like a parameter type (ends with Params or similar)
                if 'param' in name.lower() or name.endswith('Request'):
                    return name
        return None
    
    def _generate_operation_id(self, method: str, path: str) -> str:
        """Generate an operation ID from method and path"""
        # Convert path to camelCase operation ID
        parts = path.strip('/').split('/')
        operation_id = method.lower()
        for part in parts:
            # Remove path parameters
            if '{' in part:
                part = part.replace('{', '').replace('}', '')
            # Convert to camelCase
            words = part.split('-')
            if words:
                operation_id += words[0].capitalize()
                for word in words[1:]:
                    operation_id += word.capitalize()
        return operation_id
    
    def generate_report(self) -> str:
        """Generate a report of the translation process"""
        lines = ["EBNF to OpenAPI Translation Report", "=" * 40, ""]
        
        # Summary
        lines.append(f"Productions parsed: {len(self.productions)}")
        lines.append(f"Endpoints found: {len(self.endpoints)}")
        lines.append(f"Issues found: {len(self.issues)}")
        lines.append("")
        
        # Type classifications
        objects = []
        enums = []
        primitives = []
        
        for name in self.productions:
            if isinstance(name, str):
                type_info = self.resolve_type(name)
                if type_info.properties:
                    objects.append(name)
                elif type_info.enum_values:
                    enums.append(name)
                else:
                    primitives.append(name)
        
        lines.append("Type Classifications:")
        lines.append(f"  Objects: {', '.join(objects) if objects else 'none'}")
        lines.append(f"  Enums: {', '.join(enums) if enums else 'none'}")
        lines.append(f"  Primitives: {', '.join(primitives) if primitives else 'none'}")
        lines.append("")
        
        # Issues
        if self.issues:
            lines.append("Issues:")
            for issue in self.issues:
                prefix = {"error": "❌", "warning": "⚠️ ", "info": "ℹ️ "}[issue.severity]
                lines.append(f"  {prefix} {issue.message}")
                if issue.suggestion:
                    lines.append(f"     → {issue.suggestion}")
        else:
            lines.append("✅ No issues found!")
        
        lines.append("")
        
        # Type resolution details
        lines.append("Type Resolutions:")
        for name in sorted(self.productions.keys()):
            type_info = self.resolve_type(name)
            if type_info.openapi_type == "oneOf":
                lines.append(f"  {name} → oneOf[{len(type_info.one_of)} options]")
            elif type_info.enum_values:
                lines.append(f"  {name} → {type_info.openapi_type} enum[{len(type_info.enum_values)} values]")
            elif type_info.properties:
                lines.append(f"  {name} → object[{len(type_info.properties)} properties]")
            else:
                lines.append(f"  {name} → {type_info.openapi_type}")
        
        return "\n".join(lines)

# ─────────────────────────── CLI Interface ───────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Convert EBNF data dictionary to OpenAPI 3.0.3 specification"
    )
    parser.add_argument("input", help="Input EBNF file")
    parser.add_argument("-o", "--output", help="Output OpenAPI file (YAML or JSON)")
    parser.add_argument("-f", "--format", choices=["yaml", "json"], default="yaml",
                        help="Output format (default: yaml)")
    parser.add_argument("-r", "--report", action="store_true",
                        help="Show detailed report")
    parser.add_argument("--report-file", help="Save report to file")
    
    args = parser.parse_args()
    
    # Read input file
    try:
        with open(args.input, 'r') as f:
            ebnf_content = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create translator and parse
    translator = EBNFToOpenAPITranslator()
    translator.parse_ebnf(ebnf_content)
    
    # Generate OpenAPI spec
    openapi_spec = translator.generate_openapi()
    
    # Generate report
    report = translator.generate_report()
    
    # Show or save report
    if args.report:
        print(report)
        print()
    
    if args.report_file:
        with open(args.report_file, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.report_file}")
    
    # Output OpenAPI spec
    if args.output:
        with open(args.output, 'w') as f:
            if args.format == "yaml":
                yaml.dump(dict(openapi_spec), f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            else:
                json.dump(openapi_spec, f, indent=2)
        print(f"OpenAPI specification saved to: {args.output}")
    else:
        # Output to stdout
        if args.format == "yaml":
            print(yaml.dump(dict(openapi_spec), default_flow_style=False, sort_keys=False, allow_unicode=True))
        else:
            print(json.dumps(openapi_spec, indent=2))
    
    # Exit with error code if there were errors
    if any(issue.severity == "error" for issue in translator.issues):
        sys.exit(1)

if __name__ == "__main__":
    main()