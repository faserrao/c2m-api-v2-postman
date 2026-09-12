#!/usr/bin/env python3
"""
EBNF to OpenAPI Dynamic Translator V3
-------------------------------------
Fully dynamic converter from EBNF data dictionary to OpenAPI 3.0.3 specification.
No hardcoded endpoints or schemas - everything is generated from EBNF.

Features:
- Uses Lark parser for robust EBNF parsing
- Dynamically discovers endpoints from EBNF comments
- Dynamically generates schemas from EBNF productions
- Resolves type chains (e.g., documentId → id → integer)
- Comprehensive error reporting
"""

import re
import sys
import json
import random
import string
import yaml
import textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any, Union
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
    %ignore /\(\*(.|\n)*?\*\)/          // Multi-line comments
"""

# ─────────────────────────── Default constants ───────────────────────────
# Single source of truth for values that appear in __init__, generate_openapi(),
# and argparse defaults.  Override via Makefile / CLI args — not by editing here.
_DEFAULT_SERVER_URL   = "https://api.click2mail.com/v2"
_DEFAULT_SUPPORT_EMAIL = "support@click2mail.com"
_DEFAULT_API_TITLE    = "C2M API v2"
_DEFAULT_API_VERSION  = "2.0.0"

# ─────────────────────────── Data Classes ───────────────────────────
@dataclass
class EBNFProduction:
    """Represents an EBNF production rule"""
    name: str
    expression: Any  # AST node
    line_number: int = 0

@dataclass
class TypeInfo:
    """Type information for OpenAPI schema generation"""
    openapi_type: str
    format: Optional[str] = None
    enum_values: Optional[List[str]] = None
    properties: Optional[Dict[str, Any]] = None

@dataclass
class Issue:
    """Represents an issue found during translation"""
    severity: str  # 'error', 'warning', 'info'
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None

@dataclass
class Endpoint:
    """Represents an API endpoint found in comments"""
    method: str
    path: str
    production_name: Optional[str] = None
    line_number: int = 0

# ─────────────────────────── AST Transformer ───────────────────────────
class EBNFTransformer(Transformer):
    """Transforms Lark parse tree into our AST"""
    
    def start(self, items):
        return items
    
    def production(self, items):
        # items[0] is the SYMBOL which is a dict like {'type': 'symbol', 'name': 'foo'}
        name_item = items[0]
        if isinstance(name_item, dict) and name_item.get('type') == 'symbol':
            name = name_item['name']
        else:
            name = str(name_item)
        expr = items[1]
        return {'name': name, 'expression': expr}
    
    def expression(self, items):
        return items[0]
    
    def alternation(self, items):
        if len(items) == 1:
            return items[0]
        return {'type': 'alternation', 'choices': items}
    
    def concatenation(self, items):
        if len(items) == 1:
            return items[0]
        return {'type': 'concatenation', 'items': items}
    
    def term(self, items):
        return items[0]
    
    def SYMBOL(self, token):
        return {'type': 'symbol', 'name': str(token)}
    
    def STRING(self, token):
        value = str(token)[1:-1]  # Remove quotes
        return {'type': 'literal', 'value': value}
    
    def NUMBER(self, token):
        return {'type': 'number', 'value': int(token)}
    
    def optional(self, items):
        return {'type': 'optional', 'expression': items[0]}
    
    def group(self, items):
        return items[0]
    
    def repeat(self, items):
        return {'type': 'repeat', 'expression': items[0]}

# ─────────────────────────── Main Translator ───────────────────────────
class EBNFToOpenAPITranslator:
    """Main translator class that converts EBNF to OpenAPI"""
    
    def __init__(self):
        self.parser = Lark(EBNF_GRAMMAR, parser='lalr', transformer=EBNFTransformer())
        self.productions: Dict[str, EBNFProduction] = {}
        self.endpoints: List[Endpoint] = []
        self.issues: List[Issue] = []
        self.type_cache: Dict[str, TypeInfo] = {}
        self.generated_schemas: Dict[str, Dict[str, Any]] = {}  # Store generated named schemas
        self.schema_counter = 0  # Counter for unique schema names
        self.http_error_map: Dict[str, Any] = {}  # Parsed from @http_error_map block in EBNF
        self.numeric_constraints: Dict[str, Dict[str, Any]] = {}  # Parsed from @numeric_constraints block
        self.valid_combinations: List[Dict[str, Any]] = []  # Parsed from @valid_combinations block
        self.support_email: str = _DEFAULT_SUPPORT_EMAIL
        self.api_title: str = _DEFAULT_API_TITLE
        self.api_version: str = _DEFAULT_API_VERSION
        
        # OpenAPI type mappings for primitives
        self.primitive_types = {
            'string': 'string',
            'integer': 'integer',
            'number': 'number',
            'boolean': 'boolean',
            'id': 'integer',
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
            'date': 'date',
            'datetime': 'date-time',
            'email': 'email',
            'uri': 'uri',
            'url': 'uri'
        }
    
    def parse_ebnf(self, content: str) -> None:
        """Parse EBNF content and extract productions"""
        lines = content.split('\n')
        
        # Parse annotation blocks from EBNF
        self.http_error_map = self._parse_http_error_map(content)
        self.numeric_constraints = self._parse_numeric_constraints(content)
        self.valid_combinations = self._parse_valid_combinations(content)

        # First extract endpoints from comments
        self._extract_endpoints(lines)
        
        # Parse the EBNF
        try:
            ast = self.parser.parse(content)

            # Store productions
            for item in ast:
                if isinstance(item, dict) and 'name' in item and 'expression' in item:
                    prod = EBNFProduction(name=item['name'], expression=item['expression'])
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
    
    def _parse_http_error_map(self, content: str) -> Dict[str, Any]:
        """Parse @http_error_map annotation block from EBNF content.

        Returns dict keyed by HTTP status string: {'400': {'errorType': '...', 'errorCodes': [...]}}
        Returns empty dict if the block is absent (non-fatal; caller should guard).
        """
        match = re.search(r'@http_error_map\s*\n(.*?)@end_http_error_map', content, re.DOTALL)
        if not match:
            return {}
        result: Dict[str, Any] = {}
        for line in match.group(1).splitlines():
            m = re.match(r'\s*(\d+):\s*errorType=(\w+);\s*errorCodes=([\w,]+)', line)
            if m:
                status = m.group(1)
                error_type = m.group(2)
                codes = [c.strip() for c in m.group(3).split(',')]
                result[status] = {'errorType': error_type, 'errorCodes': codes}
        return result

    def _parse_numeric_constraints(self, content: str) -> Dict[str, Dict[str, Any]]:
        """Parse @numeric_constraints annotation block from EBNF content.

        Returns dict keyed by field name: {'month': {'minimum': 1, 'maximum': 12}}
        Returns empty dict if the block is absent.

        Line format:  fieldName: minimum=N, maximum=N
        (exclusiveMinimum and exclusiveMaximum are also recognised.)
        """
        match = re.search(r'@numeric_constraints\s*\n(.*?)@end_numeric_constraints', content, re.DOTALL)
        if not match:
            return {}
        result: Dict[str, Dict[str, Any]] = {}
        kw_map = {
            'minimum': 'minimum', 'maximum': 'maximum',
            'exclusiveMinimum': 'exclusiveMinimum', 'exclusiveMaximum': 'exclusiveMaximum',
        }
        for line in match.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            m = re.match(r'(\w+)\s*:\s*(.+)', line)
            if not m:
                continue
            field_name = m.group(1)
            constraints: Dict[str, Any] = {}
            for pair in re.findall(r'(minimum|maximum|exclusiveMinimum|exclusiveMaximum)\s*=\s*(-?\d+(?:\.\d+)?)', m.group(2)):
                kw, val_str = pair
                try:
                    val = int(val_str) if '.' not in val_str else float(val_str)
                except ValueError:
                    continue
                constraints[kw_map[kw]] = val
            if constraints:
                result[field_name] = constraints
        return result

    def _parse_valid_combinations(self, content: str) -> List[Dict[str, Any]]:
        """Parse @valid_combinations annotation block from EBNF content.

        Returns a list of combination rules, each a dict with keys:
          'when_field', 'when_value', 'then_field', 'then_values'

        Line format:  fieldA=value: fieldB must be one of (v1|v2|...)
        Returns empty list if the block is absent.
        """
        match = re.search(r'@valid_combinations\s*\n(.*?)@end_valid_combinations', content, re.DOTALL)
        if not match:
            return []
        result: List[Dict[str, Any]] = []
        for line in match.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            m = re.match(r'(\w+)=(\w+)\s*:\s*(\w+)\s+must\s+be\s+one\s+of\s+\(([^)]+)\)', line)
            if m:
                result.append({
                    'when_field': m.group(1),
                    'when_value': m.group(2),
                    'then_field': m.group(3),
                    'then_values': [v.strip() for v in m.group(4).split('|')],
                })
        return result

    def _extract_endpoints(self, lines: List[str]) -> None:
        """Extract endpoint definitions from comments and their associated productions"""
        endpoint_pattern = r'Endpoint:\s*(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/\-{}]+)'
        production_pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*='
        
        i = 0
        while i < len(lines):
            line = lines[i]
            match = re.search(endpoint_pattern, line, re.IGNORECASE)
            if match:
                endpoint = Endpoint(
                    method=match.group(1).upper(),
                    path=match.group(2),
                    line_number=i + 1
                )
                
                # Look for the production name after the comment block(s)
                j = i + 1
                in_comment = '(*' in lines[i] and not lines[i].strip().endswith('*)')

                while j < len(lines):
                    line_content = lines[j].strip()

                    # Check if entering a new comment block
                    if not in_comment and line_content.startswith('(*'):
                        in_comment = True

                    # Check if we're exiting the comment block
                    if in_comment and '*)' in lines[j]:
                        in_comment = False
                        j += 1
                        continue

                    # Skip lines while still in comment
                    if in_comment:
                        j += 1
                        continue

                    # Skip empty lines
                    if not line_content:
                        j += 1
                        continue

                    # Look for production definition
                    prod_match = re.match(production_pattern, lines[j])
                    if prod_match:
                        endpoint.production_name = prod_match.group(1)
                        break

                    # If we hit another line that's not a production or comment, stop
                    break

                j += 1
                
                self.endpoints.append(endpoint)
            
            i += 1
    
    def generate_openapi(self, server_url: str = _DEFAULT_SERVER_URL,
                         support_email: str = _DEFAULT_SUPPORT_EMAIL,
                         api_title: str = _DEFAULT_API_TITLE,
                         api_version: str = _DEFAULT_API_VERSION) -> Dict[str, Any]:
        """Generate the complete OpenAPI specification"""
        self.support_email = support_email
        self.api_title = api_title
        self.api_version = api_version

        # First, generate all schemas
        schemas = self._generate_all_schemas()

        # Generate paths based on endpoints
        paths = self._generate_paths()

        # Build the complete spec
        info = OrderedDict([
            ("title", self.api_title),
            ("version", self.api_version),
            ("description", "API for submitting mailing jobs with various document routing options"),
            ("x-http-error-map", self.http_error_map),
        ])
        if self.numeric_constraints:
            info["x-numeric-constraints"] = self.numeric_constraints
        if self.valid_combinations:
            info["x-valid-combinations"] = self.valid_combinations

        spec = OrderedDict([
            ("openapi", "3.0.3"),
            ("info", info),
            ("servers", [
                {
                    "url": server_url,
                    "description": "Production server"
                }
            ]),
            ("tags", [
                {
                    "name": "jobs",
                    "description": "Job submission endpoints"
                }
            ]),
            ("components", OrderedDict([
                ("schemas", schemas),
                ("parameters", self._generate_parameters()),
                ("securitySchemes", OrderedDict([
                    ("bearerAuth", OrderedDict([
                        ("type", "http"),
                        ("scheme", "bearer"),
                        ("bearerFormat", "JWT")
                    ]))
                ]))
            ])),
            ("security", [{"bearerAuth": []}]),
            ("paths", paths)
        ])
        
        return spec
    
    def _generate_all_schemas(self) -> OrderedDict:
        """Generate all schemas dynamically from EBNF productions"""
        schemas = OrderedDict()
        
        # Numeric constraint overrides — driven by the @numeric_constraints block in the EBNF.
        # Each entry becomes a schema override for integer fields that need min/max bounds.
        # The EBNF itself has no range syntax, so these live in the annotation block.
        simple_type_schemas: Dict[str, Any] = {}
        for field_name, constraints in self.numeric_constraints.items():
            prod = self.productions.get(field_name)
            if prod is None:
                continue
            type_info = self._resolve_type(field_name)
            base = {'type': type_info.openapi_type}
            if type_info.format:
                base['format'] = type_info.format
            base.update(constraints)
            simple_type_schemas[field_name] = base
        
        # Add simple type schemas first
        schemas.update(simple_type_schemas)
        
        # Skip these fundamental types that shouldn't have schemas
        skip_types = {'string', 'integer', 'number', 'character'}
        
        # Generate schemas dynamically from EBNF productions
        for name, production in self.productions.items():
            # Skip if already added as simple type or is a fundamental type
            if name in simple_type_schemas or name in skip_types:
                continue
                
            # Generate schema from production
            schema = self._expression_to_schema(production.expression, name)
            
            # Add the schema
            schemas[name] = schema

        # Add any generated named schemas from concatenation structures
        schemas.update(self.generated_schemas)
        
        return schemas
    
    def _generate_paths(self) -> OrderedDict:
        """Generate API paths dynamically from EBNF endpoints"""
        paths = OrderedDict()

        # Generate endpoints dynamically from EBNF
        for endpoint in self.endpoints:
            if not endpoint.production_name:
                self.issues.append(Issue(
                    severity="warning",
                    message=f"No production found for endpoint {endpoint.method} {endpoint.path}"
                ))
                continue
            
            if endpoint.production_name not in self.productions:
                self.issues.append(Issue(
                    severity="error",
                    message=f"Production '{endpoint.production_name}' not found for endpoint {endpoint.path}"
                ))
                continue
            
            # Use $ref to schema component instead of inlining
            # This preserves proper field names like 'documentsWithRecipients' instead of 'items'
            if endpoint.path not in paths:
                paths[endpoint.path] = OrderedDict()

            endpoint_tags = ["jobs"]

            operation = OrderedDict([
                ("tags", endpoint_tags),
                ("summary", self._generate_summary(endpoint)),
                ("description", self._generate_description(endpoint)),
                ("operationId", self._generate_operation_id(endpoint)),
                ("requestBody", {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{endpoint.production_name}"}
                        }
                    }
                }),
                ("responses", OrderedDict([
                    ("200", {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/standardResponse"}
                            }
                        }
                    }),
                    ("400", {
                        "description": "Bad Request - Invalid request parameters",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/errorResponse"},
                                "examples": self._generate_error_examples("400", endpoint)
                            }
                        }
                    }),
                    ("401", {
                        "description": "Unauthorized - Missing or invalid authentication",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/errorResponse"},
                                "examples": self._generate_error_examples("401", endpoint)
                            }
                        }
                    }),
                    ("403", {
                        "description": "Forbidden - Insufficient permissions",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/errorResponse"},
                                "examples": self._generate_error_examples("403", endpoint)
                            }
                        }
                    }),
                    ("404", {
                        "description": "Not Found - Resource not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/errorResponse"},
                                "examples": self._generate_error_examples("404", endpoint)
                            }
                        }
                    }),
                    ("422", {
                        "description": "Unprocessable Entity - Validation failed",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/errorResponse"},
                                "examples": self._generate_error_examples("422", endpoint)
                            }
                        }
                    }),
                    ("500", {
                        "description": "Internal Server Error - Server encountered an error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/errorResponse"},
                                "examples": self._generate_error_examples("500", endpoint)
                            }
                        }
                    })
                ]))
            ])
            
            paths[endpoint.path][endpoint.method.lower()] = operation

        # Bidirectional drift check: warn if any generated path has no _ENDPOINT_META
        # entry (spec falls back to terse auto-generated text) or if _ENDPOINT_META has
        # an entry for a path that no longer exists in the EBNF (stale entry).
        # Edit _ENDPOINT_META above to resolve either warning.
        for path in paths:
            if path not in self._ENDPOINT_META:
                self.issues.append(Issue(
                    severity="warning",
                    message=(
                        f"No _ENDPOINT_META entry for path '{path}' — spec will use "
                        f"auto-generated summary/description. Add an entry to "
                        f"_ENDPOINT_META in ebnf_to_openapi_dynamic_v3.py."
                    )
                ))
        for path in self._ENDPOINT_META:
            if path not in paths:
                self.issues.append(Issue(
                    severity="warning",
                    message=(
                        f"_ENDPOINT_META has a stale entry for '{path}' — this path "
                        f"no longer exists in the EBNF. Remove the entry from "
                        f"_ENDPOINT_META in ebnf_to_openapi_dynamic_v3.py."
                    )
                ))

        return paths
    
    def _generate_operation_id(self, endpoint: Endpoint) -> str:
        """Generate operation ID from endpoint"""
        # Use the production name as the operation ID
        return endpoint.production_name

    # Human-readable metadata keyed by endpoint path.
    # Update this table whenever endpoint paths change in the EBNF.
    _ENDPOINT_META = {
        '/static': (
            "Submit single document",
            "Submits a mailing job for a single document to one or more recipients. "
            "The request body must include a document source, recipient address information, "
            "and payment details."
        ),
        '/static/address-capture': (
            "Submit single document — address capture",
            "Submits a mailing job for a single PDF where recipient addresses are captured "
            "from the document via OCR. No inline recipient address is required."
        ),
        '/batch/split': (
            "Submit PDF split",
            "Splits a single PDF into page ranges and mails each range to a different "
            "recipient. Each job item specifies page range and recipient address."
        ),
        '/batch/split/address-capture': (
            "Submit PDF split — address capture",
            "Splits a single PDF into page ranges where recipient addresses are captured "
            "from the PDF. No inline recipient addresses are required."
        ),
        '/mail-merge': (
            "Submit mail merge",
            "Merges multiple documents into a single mailing sent to one recipient. "
            "Useful for creating document packets or multi-page letters."
        ),
        '/batch/zip': (
            "Submit ZIP batch",
            "Submits multiple mailing jobs sourced from files inside a single ZIP archive. "
            "Each job item specifies which file within the ZIP and the recipient address."
        ),
        '/batch/zip/address-capture': (
            "Submit ZIP batch — address capture",
            "Submits a ZIP-based mailing batch where recipient addresses are captured "
            "externally. No inline recipient addresses are required."
        ),
    }

    def _generate_summary(self, endpoint: Endpoint) -> str:
        """Generate a brief summary from endpoint path."""
        meta = self._ENDPOINT_META.get(endpoint.path)
        if meta:
            return meta[0]
        # Fallback: preserve camelCase production name (never call .title() on camelCase)
        return endpoint.production_name

    def _generate_description(self, endpoint: Endpoint) -> str:
        """Generate a detailed description from endpoint."""
        meta = self._ENDPOINT_META.get(endpoint.path)
        if meta:
            return meta[1]
        # Fallback description
        return f"API endpoint for {endpoint.production_name}"

    def _generate_error_examples(self, status_code: str, endpoint: Endpoint) -> Dict[str, Any]:
        """Generate error response examples for a given HTTP status code.

        errorType and errorCodes are read from the @http_error_map block in the EBNF
        (parsed into self.http_error_map). Edit that block in the data dictionary to
        change which error variants are produced — no Python changes needed.
        """
        if not self.http_error_map:
            raise RuntimeError(
                "@http_error_map block not found in EBNF data dictionary.\n"
                "Add it after the HTTP status aliases in data_dictionary/c2mapiv2-dd.ebnf."
            )

        # Map HTTP status codes to descriptive messages
        status_to_messages = {
            '400': [
                "Missing required field in request",
                "Invalid oneOf field value",
                "Malformed JSON in request body"
            ],
            '401': [
                "Authorization header is missing or invalid",
                "Authentication token is invalid",
                "Authentication token has expired"
            ],
            '403': [
                "Insufficient permissions to access this resource",
                "Account has been suspended"
            ],
            '404': [
                "Job not found",
                "Requested resource does not exist"
            ],
            '422': [
                "Invalid enum value provided",
                "Mutually exclusive fields both present",
                "Field format validation failed"
            ],
            '500': [
                "Internal server error occurred",
                "Database error occurred",
                "External service error"
            ]
        }

        # Extract endpoint-specific field names for contextual error details
        field_names = self._extract_endpoint_field_names(endpoint)

        # Generate examples for this status code
        examples = {}
        map_entry = self.http_error_map.get(status_code, {})
        error_type = map_entry.get('errorType', 'ServerError')
        codes = map_entry.get('errorCodes', ['SERVER_ERROR'])
        messages = status_to_messages.get(status_code, ['An error occurred'])

        # Create one example per error code for this status
        for idx, (code, message) in enumerate(zip(codes, messages)):
            # Generate unique tracking ID
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            tracking_id = f"TRK-{datetime.now().strftime('%Y%m%d')}-{suffix}"

            # Generate contextual error details
            details = self._generate_error_details(status_code, code, field_names)

            # Create example
            example_name = f"example-{idx+1}"
            examples[example_name] = {
                "value": {
                    "errorType": error_type,
                    "errorMessage": message,
                    "errorCode": code,
                    "errorDetails": details,
                    "errorTrackingId": tracking_id
                }
            }

        return examples

    def _get_enum_values(self, production_name: str) -> List[str]:
        """Extract enum values from an EBNF alternation production"""
        if production_name not in self.productions:
            return []

        production = self.productions[production_name]
        expr = production.expression

        if isinstance(expr, dict) and expr.get('type') == 'alternation':
            values = []
            for item in expr.get('items', []):
                if isinstance(item, dict) and item.get('type') == 'literal':
                    values.append(item.get('value', ''))
            return values

        return []

    def _collect_symbols_from_expression(self, expr: Any, result: List[str]) -> None:
        """Recursively collect all symbol names from an EBNF expression tree."""
        if not isinstance(expr, dict):
            return
        t = expr.get('type')
        if t == 'symbol':
            name = expr.get('name')
            if name:
                result.append(name)
        elif t == 'concatenation':
            for item in expr.get('items', []):
                self._collect_symbols_from_expression(item, result)
        elif t == 'alternation':
            for choice in expr.get('choices', []):
                self._collect_symbols_from_expression(choice, result)
        elif t in ('optional', 'repeat'):
            self._collect_symbols_from_expression(expr.get('expression'), result)

    def _extract_endpoint_field_names(self, endpoint: Endpoint) -> Dict[str, str]:
        """Extract relevant field names from endpoint's request body schema using EBNF graph traversal."""
        if not endpoint.production_name or endpoint.production_name not in self.productions:
            return {'field': 'unknownField', 'field1': 'unknownField1'}

        production = self.productions[endpoint.production_name]

        # Walk the full EBNF expression tree to collect all referenced symbol names.
        all_symbols: List[str] = []
        self._collect_symbols_from_expression(production.expression, all_symbols)

        field_names = {}

        # Find document field: match by keyword, most-specific first so the
        # best match wins (e.g. 'docSource*' beats 'document*').
        doc_keywords = ['docSource', 'documentSource', 'document']
        for kw in doc_keywords:
            match = next((s for s in all_symbols if kw.lower() in s.lower()), None)
            if match:
                field_names['documentField'] = match
                break

        # Find address field similarly.
        addr_keywords = ['addressSource', 'recipientAddress', 'addressList', 'address']
        for kw in addr_keywords:
            match = next((s for s in all_symbols if kw.lower() in s.lower()), None)
            if match:
                field_names['addressField'] = match
                break

        # Defaults if graph traversal found no matching symbols.
        if 'documentField' not in field_names:
            field_names['documentField'] = 'documentId'
        if 'addressField' not in field_names:
            field_names['addressField'] = 'recipientAddress'

        return field_names

    def _generate_error_details(self, status_code: str, error_code: str, field_names: Dict[str, str]) -> str:
        """Generate contextual error details based on error type"""
        details_map = {
            'MISSING_REQUIRED_FIELD': {
                "field": field_names.get('documentField', 'documentId'),
                "location": "requestBody"
            },
            'INVALID_ONEOF': {
                "field": field_names.get('documentField', 'docSourceAll'),
                "issue": "exactly one variant must be provided"
            },
            'INVALID_JSON': {
                "error": "unexpected token at position 42"
            },
            'MISSING_AUTH_HEADER': {
                "expected": "Bearer <token>",
                "received": "none"
            },
            'INVALID_TOKEN': {
                "issue": "token signature verification failed"
            },
            'EXPIRED_TOKEN': {
                "expiresAt": (datetime.now(timezone.utc) - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "currentTime": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            },
            'INSUFFICIENT_PERMISSIONS': {
                "required": "jobs:write",
                "provided": "jobs:read"
            },
            'ACCOUNT_SUSPENDED': {
                "reason": "billing overdue",
                "contactSupport": self.support_email
            },
            'JOB_NOT_FOUND': {
                "jobId": "JOB-12345"
            },
            'RESOURCE_NOT_FOUND': {
                "resourceType": "document",
                "resourceId": "DOC-67890"
            },
            'INVALID_ENUM_VALUE': {
                "field": field_names.get('documentField', 'documentType'),
                "value": "invalid_value",
                "allowedValues": ["pdf", "doc", "docx"]
            },
            'MUTUAL_EXCLUSION_VIOLATION': {
                "fields": ["jobTemplate", "jobOptions"],
                "issue": "only one may be provided"
            },
            'INVALID_FORMAT': {
                "errors": [
                    {
                        "field": field_names.get('documentField', 'documentId'),
                        "issue": "not found in document library"
                    },
                    {
                        "field": f"{field_names.get('addressField', 'recipientAddress')}.postalCode",
                        "issue": "invalid format - must be 5 or 9 digits"
                    }
                ]
            },
            'SERVER_ERROR': {
                "message": "An unexpected error occurred"
            },
            'DATABASE_ERROR': {
                "operation": "insert",
                "table": "jobs"
            },
            'EXTERNAL_SERVICE_ERROR': {
                "service": "payment-gateway",
                "status": "timeout"
            }
        }

        details = details_map.get(error_code, {"message": "An error occurred"})
        return json.dumps(details)

    def _generate_schema_from_production(self, production_name: str) -> Dict[str, Any]:
        """Generate schema from EBNF production"""
        if production_name not in self.productions:
            return {"type": "object"}
        
        production = self.productions[production_name]
        return self._expression_to_schema(production.expression, production_name)
    
    def _expression_to_schema(self, expr: Any, context: str = "") -> Dict[str, Any]:
        """Convert EBNF expression to OpenAPI schema"""
        if isinstance(expr, dict):
            expr_type = expr.get('type')
            
            if expr_type == 'concatenation':
                items = expr.get('items', [])
                
                # Check if first item is an alternation (pattern like (A | B | C) + D + E)
                if (items and isinstance(items[0], dict) and items[0].get('type') == 'alternation'):
                    return self._handle_alternation_plus_concatenation(items, context)
                
                # This is an object with required properties
                schema = {"type": "object", "properties": {}, "required": []}
                
                for item in items:
                    if isinstance(item, dict):
                        item_type = item.get('type')
                        
                        if item_type == 'symbol':
                            prop_name = item.get('name')
                            if prop_name:
                                # Always use direct type for properties, not refs
                                schema['properties'][prop_name] = self._get_field_type(prop_name)
                                schema['required'].append(prop_name)
                        
                        elif item_type == 'optional':
                            # Optional field
                            opt_expr = item.get('expression')
                            if opt_expr and isinstance(opt_expr, dict) and opt_expr.get('type') == 'symbol':
                                prop_name = opt_expr.get('name')
                                if prop_name:
                                    # Always use direct type for optional properties
                                    schema['properties'][prop_name] = self._get_field_type(prop_name)
                        
                        elif item_type == 'repeat':
                            # Array field
                            repeat_expr = item.get('expression')
                            if repeat_expr and isinstance(repeat_expr, dict):
                                if repeat_expr.get('type') == 'concatenation':
                                    schema['properties']['items'] = {
                                        "type": "array",
                                        "items": self._expression_to_schema(repeat_expr)
                                    }
                                    schema['required'].append('items')
                                elif repeat_expr.get('type') == 'symbol':
                                    prop_name = repeat_expr.get('name')
                                    if prop_name:
                                        schema['properties'][prop_name + 's'] = {
                                            "type": "array",
                                            "items": {"$ref": f"#/components/schemas/{prop_name}"} if prop_name in self.productions else self._get_field_type(prop_name)
                                        }
                                        schema['required'].append(prop_name + 's')
                        
                        elif item_type == 'alternation':
                            # Skip alternations for now - we'll handle them specially
                            pass
                
                # Remove empty required array
                if 'required' in schema and len(schema['required']) == 0:
                    del schema['required']
                    
                return schema
            
            elif expr_type == 'alternation':
                # This could be a oneOf or enum
                choices = expr.get('choices', [])
                if self._is_enum(choices):
                    return {
                        "type": "string",
                        "enum": [self._extract_literal_value(choice) for choice in choices]
                    }
                else:
                    # Generate oneOf schema with named schemas when appropriate
                    return self._generate_oneof_schema(choices, context)
            
            elif expr_type == 'symbol':
                symbol_name = expr.get('name')
                if symbol_name:
                    # Check if this symbol resolves to a primitive that will be skipped
                    skip_types = {'string', 'integer', 'number', 'character'}
                    if symbol_name in skip_types:
                        # Inline the primitive type instead of creating a $ref
                        return {"type": symbol_name}
                    elif symbol_name in self.productions:
                        return {"$ref": f"#/components/schemas/{symbol_name}"}
                    else:
                        return self._get_field_type(symbol_name)
            
            elif expr_type == 'optional':
                return self._expression_to_schema(expr.get('expression'), context)
            
            elif expr_type == 'repeat':
                inner_schema = self._expression_to_schema(expr.get('expression'), context)
                return {"type": "array", "items": inner_schema}
        
        return {"type": "object"}
    
    def _generate_oneof_schema(self, choices: List[Any], context: str) -> Dict[str, Any]:
        """Generate oneOf schema from alternation choices"""
        schemas = []
        
        for i, choice in enumerate(choices):
            if isinstance(choice, dict):
                choice_type = choice.get('type')
                
                if choice_type == 'symbol':
                    symbol_name = choice.get('name')
                    if symbol_name:
                        schemas.append({"$ref": f"#/components/schemas/{symbol_name}"})

                elif choice_type == 'concatenation':
                    schemas.append(self._expression_to_schema(choice, context))
                
                elif choice_type == 'group':
                    # Process the grouped expression
                    schemas.append(self._expression_to_schema(choice.get('expression'), context))
        
        if len(schemas) == 1:
            return schemas[0]
        else:
            return {"oneOf": schemas}
    
    def _is_enum(self, choices: List[Any]) -> bool:
        """Check if alternation represents an enum"""
        return all(
            isinstance(choice, dict) and 
            choice.get('type') in ['literal', 'number']
            for choice in choices
        )
    
    def _extract_literal_value(self, literal_expr: Dict[str, Any]) -> Any:
        """Extract the value from a literal expression"""
        if literal_expr.get('type') == 'literal':
            return literal_expr.get('value', '')
        elif literal_expr.get('type') == 'number':
            return literal_expr.get('value', 0)
        return ''
    
    def _get_field_type(self, field_name: str, format: Optional[str] = None) -> Dict[str, Any]:
        """Get the OpenAPI type for a field, resolving from EBNF if needed"""
        # Check if this field is a primitive alias (e.g., paymentData = string)
        type_info = self._resolve_type(field_name)

        # If it resolves to a primitive, inline it instead of creating a $ref
        # This prevents broken references like $ref: "#/components/schemas/string"
        if type_info.openapi_type in ('string', 'integer', 'number', 'boolean'):
            schema = {"type": type_info.openapi_type}
            if type_info.format:
                schema["format"] = type_info.format
            if type_info.enum_values:
                schema["enum"] = type_info.enum_values
            return schema

        # For complex types (array, oneOf, object), use a reference
        # This includes arrays like multiDocJobs, unions like paymentDetails, and objects
        return {"$ref": f"#/components/schemas/{field_name}"}
    
    def _resolve_type(self, name: str, visited: Set[str] = None) -> TypeInfo:
        """Resolve a type name to OpenAPI type info"""
        if visited is None:
            visited = set()
            
        # Check cache
        if name in self.type_cache:
            return self.type_cache[name]
            
        # Prevent infinite recursion
        if name in visited:
            return TypeInfo(openapi_type="string")
            
        visited.add(name)
        
        # Check primitive types first
        if name.lower() in self.primitive_types:
            type_info = TypeInfo(
                openapi_type=self.primitive_types[name.lower()],
                format=self.format_mappings.get(name.lower())
            )
            self.type_cache[name] = type_info
            return type_info
        
        # Check productions
        if name in self.productions:
            production = self.productions[name]
            expr = production.expression
            
            if isinstance(expr, dict):
                expr_type = expr.get('type')
                
                if expr_type == 'symbol':
                    # This is an alias, resolve the target
                    symbol_name = expr.get('name')
                    if symbol_name and symbol_name != name:
                        type_info = self._resolve_type(symbol_name, visited)
                        self.type_cache[name] = type_info
                        return type_info
                
                elif expr_type == 'alternation':
                    # Check if it's an enum
                    choices = expr.get('choices', [])
                    if self._is_enum(choices):
                        type_info = TypeInfo(
                            openapi_type="string",
                            enum_values=[self._extract_literal_value(choice) for choice in choices]
                        )
                        self.type_cache[name] = type_info
                        return type_info
                    else:
                        # This is a oneOf union - should use $ref
                        type_info = TypeInfo(openapi_type="oneOf")
                        self.type_cache[name] = type_info
                        return type_info

                elif expr_type == 'repeat':
                    # This is an array type - should use $ref
                    type_info = TypeInfo(openapi_type="array")
                    self.type_cache[name] = type_info
                    return type_info

                elif expr_type == 'concatenation':
                    # This is an object type
                    type_info = TypeInfo(openapi_type="object")
                    self.type_cache[name] = type_info
                    return type_info
        
        # Default
        type_info = TypeInfo(openapi_type="string")
        self.type_cache[name] = type_info
        return type_info
    
    def _handle_alternation_plus_concatenation(self, items: List[Any], context: str) -> Dict[str, Any]:
        """Handle pattern where concatenation starts with alternation: (A | B | C) + D + E"""
        alternation = items[0]
        rest_items = items[1:]
        
        # First, build the base schema from the rest of the concatenation
        base_schema = {"type": "object", "properties": {}, "required": []}
        
        for item in rest_items:
            if isinstance(item, dict):
                item_type = item.get('type')
                
                if item_type == 'symbol':
                    prop_name = item.get('name')
                    if prop_name:
                        base_schema['properties'][prop_name] = self._get_field_type(prop_name)
                        base_schema['required'].append(prop_name)
                
                elif item_type == 'optional':
                    opt_expr = item.get('expression')
                    if opt_expr and isinstance(opt_expr, dict) and opt_expr.get('type') == 'symbol':
                        prop_name = opt_expr.get('name')
                        if prop_name:
                            base_schema['properties'][prop_name] = self._get_field_type(prop_name)
                
                elif item_type == 'repeat':
                    repeat_expr = item.get('expression')
                    if repeat_expr and isinstance(repeat_expr, dict) and repeat_expr.get('type') == 'symbol':
                        prop_name = repeat_expr.get('name')
                        if prop_name:
                            base_schema['properties'][prop_name + 's'] = {
                                "type": "array",
                                "items": {"$ref": f"#/components/schemas/{prop_name}"}
                            }
                            base_schema['required'].append(prop_name + 's')
        
        # Now handle the alternation choices
        choices = alternation.get('choices', [])
        schemas = []
        
        for choice in choices:
            # Create a schema that combines this choice with the base properties
            choice_schema = {
                "type": "object",
                "properties": dict(base_schema['properties']),  # Copy base properties
                "required": list(base_schema['required'])  # Copy base required
            }
            
            if isinstance(choice, dict):
                choice_type = choice.get('type')
                
                if choice_type == 'symbol':
                    # Single field option
                    prop_name = choice.get('name')
                    if prop_name:
                        choice_schema['properties'][prop_name] = self._get_field_type(prop_name)
                        choice_schema['required'].append(prop_name)
                
                elif choice_type == 'repeat':
                    # Array field option (e.g., { recipientAddressSource })
                    repeat_expr = choice.get('expression')
                    if repeat_expr and isinstance(repeat_expr, dict) and repeat_expr.get('type') == 'symbol':
                        prop_name = repeat_expr.get('name')
                        if prop_name:
                            choice_schema['properties'][prop_name + 's'] = {
                                "type": "array",
                                "items": {"$ref": f"#/components/schemas/{prop_name}"}
                            }
                            choice_schema['required'].append(prop_name + 's')
                
                elif choice_type == 'concatenation':
                    # Combined fields option (e.g., documentSourceIdentifier + { recipientAddressSource })
                    for sub_item in choice.get('items', []):
                        if isinstance(sub_item, dict):
                            sub_type = sub_item.get('type')
                            
                            if sub_type == 'symbol':
                                prop_name = sub_item.get('name')
                                if prop_name:
                                    choice_schema['properties'][prop_name] = self._get_field_type(prop_name)
                                    choice_schema['required'].append(prop_name)
                            
                            elif sub_type == 'repeat':
                                repeat_expr = sub_item.get('expression')
                                if repeat_expr and isinstance(repeat_expr, dict) and repeat_expr.get('type') == 'symbol':
                                    prop_name = repeat_expr.get('name')
                                    if prop_name:
                                        choice_schema['properties'][prop_name + 's'] = {
                                            "type": "array",
                                            "items": {"$ref": f"#/components/schemas/{prop_name}"}
                                        }
                                        choice_schema['required'].append(prop_name + 's')
            
            # Clean up empty required arrays
            if not choice_schema.get('required'):
                del choice_schema['required']
            
            schemas.append(choice_schema)
        
        # Return the oneOf schema
        if len(schemas) == 1:
            return schemas[0]
        else:
            return {"oneOf": schemas}
    
    def _generate_parameters(self) -> OrderedDict:
        """Generate common parameters"""
        return OrderedDict([
            ("Authorization", OrderedDict([
                ("name", "Authorization"),
                ("in", "header"),
                ("required", True),
                ("schema", OrderedDict([
                    ("type", "string"),
                    ("example", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
                ]))
            ])),
            ("Content-Type", OrderedDict([
                ("name", "Content-Type"),
                ("in", "header"),
                ("required", True),
                ("schema", OrderedDict([
                    ("type", "string"),
                    ("example", "application/json")
                ]))
            ]))
        ])
    
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
                type_info = self._resolve_type(name)
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
                prefix = {"error": "ERROR", "warning": "WARNING", "info": "INFO"}[issue.severity]
                lines.append(f"  [{prefix}] {issue.message}")
                if issue.suggestion:
                    lines.append(f"     -> {issue.suggestion}")
        else:
            lines.append("No issues found.")
        
        lines.append("")
        
        # Type resolution details
        lines.append("Type Resolutions:")
        important_types = ["documentId", "addressId", "addressListId", "uploadRequestId", "zipId", "id"]
        for name in important_types:
            field_type = self._get_field_type(name)
            lines.append(f"  {name} → {field_type.get('type', 'unknown')}")
        
        lines.append("")
        
        # Endpoint mappings
        lines.append("Endpoint to Production Mappings:")
        for endpoint in self.endpoints:
            if endpoint.production_name:
                lines.append(f"  {endpoint.method} {endpoint.path} → {endpoint.production_name}")
            else:
                lines.append(f"  {endpoint.method} {endpoint.path} → [NO PRODUCTION FOUND]")
        
        return "\n".join(lines)

# ─────────────────────────── Helper Functions ───────────────────────────
def convert_ordered_dict_to_dict(obj):
    """Recursively convert OrderedDict to regular dict for clean YAML output"""
    if isinstance(obj, OrderedDict):
        return {k: convert_ordered_dict_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, dict):
        return {k: convert_ordered_dict_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_ordered_dict_to_dict(item) for item in obj]
    else:
        return obj

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
    parser.add_argument("--server-url", default=_DEFAULT_SERVER_URL,
                        help=f"Production server URL written into the OpenAPI servers: block "
                             f"(default: {_DEFAULT_SERVER_URL})")
    parser.add_argument("--support-email", default=_DEFAULT_SUPPORT_EMAIL,
                        help=f"Support contact email used in ACCOUNT_SUSPENDED error details "
                             f"(default: {_DEFAULT_SUPPORT_EMAIL})")
    parser.add_argument("--api-title", default=_DEFAULT_API_TITLE,
                        help=f"API title written into the OpenAPI info block "
                             f"(default: {_DEFAULT_API_TITLE})")
    parser.add_argument("--api-version", default=_DEFAULT_API_VERSION,
                        help=f"API version written into the OpenAPI info block "
                             f"(default: {_DEFAULT_API_VERSION})")

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
    openapi_spec = translator.generate_openapi(server_url=args.server_url,
                                               support_email=args.support_email,
                                               api_title=args.api_title,
                                               api_version=args.api_version)
    
    # Convert OrderedDict to regular dict for clean YAML output
    openapi_spec = convert_ordered_dict_to_dict(openapi_spec)
    
    # Output the specification
    if args.output:
        try:
            with open(args.output, 'w') as f:
                if args.format == "yaml" or args.output.endswith('.yaml') or args.output.endswith('.yml'):
                    yaml.dump(openapi_spec, f, default_flow_style=False, sort_keys=False, width=1000)
                else:
                    json.dump(openapi_spec, f, indent=2)
            print(f"OpenAPI specification saved to: {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Output to stdout
        if args.format == "yaml":
            yaml.dump(openapi_spec, sys.stdout, default_flow_style=False, sort_keys=False)
        else:
            json.dump(openapi_spec, sys.stdout, indent=2)
    
    # Generate report
    if args.report or args.report_file:
        report = translator.generate_report()
        if args.report:
            print("\n" + report, file=sys.stderr)
        if args.report_file:
            try:
                with open(args.report_file, 'w') as f:
                    f.write(report)
                print(f"Report saved to: {args.report_file}", file=sys.stderr)
            except Exception as e:
                print(f"Error writing report file: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()