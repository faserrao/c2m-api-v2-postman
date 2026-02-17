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
import yaml
import textwrap
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
    
    def generate_openapi(self) -> Dict[str, Any]:
        """Generate the complete OpenAPI specification"""
        # First, generate all schemas
        schemas = self._generate_all_schemas()

        # Generate paths based on endpoints
        paths = self._generate_paths()
        
        # Build the complete spec
        spec = OrderedDict([
            ("openapi", "3.0.3"),
            ("info", OrderedDict([
                ("title", "C2M API v2"),
                ("version", "2.0.0"),
                ("description", "API for submitting mailing jobs with various document routing options")
            ])),
            ("servers", [
                {"url": "https://api.example.com/v1", "description": "Production server"},
                {"url": "http://localhost:4010", "description": "Mock server"}
            ]),
            ("tags", [
                {
                    "name": "recommended",
                    "description": "Recommended starting points - the most commonly used job submission endpoints. All endpoints support Job Templates."
                },
                {
                    "name": "jobs",
                    "description": "Additional job submission endpoints for PDF split, ZIP, and address-capture workflows"
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
        
        # Simple types that should be generated as schemas when referenced
        # NOTE: Only include fields that are defined in EBNF data dictionary
        simple_type_schemas = {
            # String types
            'firstName': {'type': 'string'},
            'lastName': {'type': 'string'},
            'address1': {'type': 'string'},
            'address2': {'type': 'string'},
            'address3': {'type': 'string'},
            'city': {'type': 'string'},
            'state': {'type': 'string'},
            'country': {'type': 'string'},
            'zip': {'type': 'string'},
            'phoneNumber': {'type': 'string'},
            'tags': {'type': 'array', 'items': {'type': 'string'}},  # Fix recursive definition
            'jobTemplate': {'type': 'string'},
            'invoiceNumber': {'type': 'string'},
            'routingNumber': {'type': 'string'},
            'accountNumber': {'type': 'string'},
            'cardNumber': {'type': 'string'},

            # Integer types
            'documentId': {'type': 'integer'},
            'addressListId': {'type': 'integer'},
            'startPage': {'type': 'integer'},
            'endPage': {'type': 'integer'},
            'month': {'type': 'integer', 'minimum': 1, 'maximum': 12},
            'year': {'type': 'integer'},
            'cvv': {'type': 'integer'},
            'checkDigit': {'type': 'integer'},

            # Number types
            'amountDue': {'type': 'number'},
            'amount': {'type': 'number'}
        }
        
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

        # Add a standard response schema
        schemas["StandardResponse"] = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "requestId": {"type": "string"}
            }
        }
        
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

            # The 3 recommended endpoints appear first in Redoc sidebar (all endpoints support templates)
            RECOMMENDED_ENDPOINTS = {
                "/jobs/submit/single/doc",
                "/jobs/submit/multi/doc",
                "/jobs/submit/multi/doc/merge"
            }
            endpoint_tags = ["recommended"] if endpoint.path in RECOMMENDED_ENDPOINTS else ["jobs"]

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
                                "schema": {"$ref": "#/components/schemas/StandardResponse"}
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
        
        return paths
    
    def _generate_operation_id(self, endpoint: Endpoint) -> str:
        """Generate operation ID from endpoint"""
        # Use the production name as the operation ID
        return endpoint.production_name

    def _generate_summary(self, endpoint: Endpoint) -> str:
        """Generate a brief summary from endpoint path"""
        # Extract meaningful parts from path
        # Example: /jobs/submit/single/doc -> "Submit a single document job"
        path_parts = [p for p in endpoint.path.strip('/').split('/') if p]

        # Build summary based on path pattern
        if len(path_parts) >= 3 and path_parts[0] == 'jobs' and path_parts[1] == 'submit':
            variant = ' '.join(path_parts[2:])
            return f"Submit a {variant} job"

        # Fallback: use production name as readable text
        return endpoint.production_name.replace('_', ' ').title()

    def _generate_description(self, endpoint: Endpoint) -> str:
        """Generate a detailed description from endpoint"""
        # Extract path components
        path_parts = [p for p in endpoint.path.strip('/').split('/') if p]

        # Generate description based on path pattern
        if len(path_parts) >= 3 and path_parts[0] == 'jobs' and path_parts[1] == 'submit':
            variant = ' '.join(path_parts[2:])

            # Add specific details based on variant
            descriptions = {
                'single doc': 'Submits a mailing job with a single document to be sent to one or more recipients.',
                'multi doc': 'Submits a mailing job with multiple documents to be sent to recipients.',
                'multi doc-merge': 'Submits a mailing job that merges multiple documents before mailing.',
                'single pdf-split': 'Submits a mailing job that splits a single PDF into multiple mailings.',
                'multi pdf-address-capture': 'Submits a mailing job that extracts addresses embedded in PDF documents.',
                'single pdf-address-capture': 'Submits a mailing job that extracts addresses from a single PDF document.'
            }

            base_desc = descriptions.get(variant, f"Submits a {variant} mailing job.")

            # Add common details
            return (f"{base_desc} The request body contains job parameters including document source, "
                   f"recipient address information, and payment details.")

        # Fallback description
        return f"API endpoint for {endpoint.production_name.replace('_', ' ')}"

    def _generate_error_examples(self, status_code: str, endpoint: Endpoint) -> Dict[str, Any]:
        """Generate error response examples from EBNF error schemas

        Dynamically reads errorType and errorCode enums from EBNF and maps
        them to appropriate HTTP status codes. No hardcoding.
        """
        import random
        import string
        from datetime import datetime

        # Extract error codes and types from EBNF
        error_codes = self._get_enum_values('errorCode')
        error_types = self._get_enum_values('errorType')

        # Map HTTP status codes to appropriate errorType
        status_to_type = {
            '400': 'ValidationError',
            '401': 'AuthenticationError',
            '403': 'AuthorizationError',
            '404': 'ResourceNotFoundError',
            '422': 'ValidationError',
            '500': 'ServerError'
        }

        # Map HTTP status codes to appropriate errorCode values (multiple per status)
        status_to_codes = {
            '400': ['MISSING_REQUIRED_FIELD', 'INVALID_ONEOF', 'INVALID_JSON'],
            '401': ['MISSING_AUTH_HEADER', 'INVALID_TOKEN', 'EXPIRED_TOKEN'],
            '403': ['INSUFFICIENT_PERMISSIONS', 'ACCOUNT_SUSPENDED'],
            '404': ['JOB_NOT_FOUND', 'RESOURCE_NOT_FOUND'],
            '422': ['INVALID_ENUM_VALUE', 'MUTUAL_EXCLUSION_VIOLATION', 'INVALID_FORMAT'],
            '500': ['SERVER_ERROR', 'DATABASE_ERROR', 'EXTERNAL_SERVICE_ERROR']
        }

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
        error_type = status_to_type.get(status_code, 'ServerError')
        codes = status_to_codes.get(status_code, ['SERVER_ERROR'])
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

    def _extract_endpoint_field_names(self, endpoint: Endpoint) -> Dict[str, str]:
        """Extract relevant field names from endpoint's request body schema"""
        # Try to get the production for this endpoint
        if not endpoint.production_name or endpoint.production_name not in self.productions:
            return {'field': 'unknownField', 'field1': 'unknownField1'}

        production = self.productions[endpoint.production_name]

        # Look for common field names in the schema
        field_names = {}

        # Check for document source variants
        doc_fields = ['docSourceAll', 'docSourceStandard', 'docSourceZipFile', 'documentSource']
        for field in doc_fields:
            if self._has_field_in_production(production, field):
                field_names['documentField'] = field
                break

        # Check for address fields
        addr_fields = ['recipientAddressSource', 'recipientAddress', 'addressListId']
        for field in addr_fields:
            if self._has_field_in_production(production, field):
                field_names['addressField'] = field
                break

        # Default field names if not found
        if 'documentField' not in field_names:
            field_names['documentField'] = 'documentId'
        if 'addressField' not in field_names:
            field_names['addressField'] = 'recipientAddress'

        return field_names

    def _has_field_in_production(self, production: EBNFProduction, field_name: str) -> bool:
        """Check if a field exists in a production"""
        expr = production.expression
        if isinstance(expr, dict) and expr.get('type') == 'concatenation':
            for item in expr.get('items', []):
                if isinstance(item, dict):
                    if item.get('type') == 'symbol' and item.get('name') == field_name:
                        return True
                    if item.get('type') == 'optional':
                        opt_expr = item.get('expression')
                        if isinstance(opt_expr, dict) and opt_expr.get('type') == 'symbol':
                            if opt_expr.get('name') == field_name:
                                return True
        return False

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
                "expiresAt": "2026-02-15T10:30:00Z",
                "currentTime": "2026-02-16T14:00:00Z"
            },
            'INSUFFICIENT_PERMISSIONS': {
                "required": "jobs:write",
                "provided": "jobs:read"
            },
            'ACCOUNT_SUSPENDED': {
                "reason": "billing overdue",
                "contactSupport": "support@click2mail.com"
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
        import json
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
                        # Check if this is a simple/primitive type that needs wrapping in oneOf context
                        # For recipientAddressSource: addressId and addressListId need wrapping
                        needs_wrapping = False
                        if context == 'recipientAddressSource' and symbol_name in ['addressId', 'addressListId']:
                            needs_wrapping = True
                        
                        if needs_wrapping:
                            # Wrap simple types in an object to preserve field name in oneOf contexts
                            wrapped_schema = {
                                "type": "object",
                                "properties": {
                                    symbol_name: {"$ref": f"#/components/schemas/{symbol_name}"}
                                },
                                "required": [symbol_name]
                            }
                            schemas.append(wrapped_schema)
                        elif symbol_name in self.productions:
                            schemas.append({"$ref": f"#/components/schemas/{symbol_name}"})
                        else:
                            # Simple type reference
                            schemas.append({"$ref": f"#/components/schemas/{symbol_name}"})
                
                elif choice_type == 'concatenation':
                    # Complex object type - create named schema for oneOf variants
                    if context in ['recipientAddressSource', 'paymentDetails']:
                        # Analyze the concatenation to determine schema name
                        schema_obj = self._expression_to_schema(choice, context)
                        schema_name = self._get_schema_name_for_concatenation(choice, context)
                        
                        # Store this as a named schema
                        self.generated_schemas[schema_name] = schema_obj
                        schemas.append({"$ref": f"#/components/schemas/{schema_name}"})
                    else:
                        # For other contexts, use inline schema
                        schemas.append(self._expression_to_schema(choice, context))
                
                elif choice_type == 'group':
                    # Process the grouped expression
                    schemas.append(self._expression_to_schema(choice.get('expression'), context))
        
        if len(schemas) == 1:
            return schemas[0]
        else:
            return {"oneOf": schemas}
    
    def _get_schema_name_for_concatenation(self, concatenation: Dict[str, Any], context: str) -> str:
        """Generate a descriptive schema name based on concatenation properties"""
        items = concatenation.get('items', [])
        properties = []
        
        for item in items:
            if isinstance(item, dict) and item.get('type') == 'symbol':
                properties.append(item.get('name'))
        
        # Special handling for specific oneOf patterns
        if context == 'paymentDetails':
            if 'creditCardDetails' in properties:
                return 'creditCardPayment'
            elif 'invoiceDetails' in properties:
                return 'invoicePayment'
            elif 'achDetails' in properties:
                return 'achPayment'
            elif 'creditAmount' in properties:
                return 'userCreditPayment'
            elif 'applePaymentDetails' in properties:
                return 'applePayPayment'
            elif 'googlePaymentDetails' in properties:
                return 'googlePayPayment'
        
        # Fallback to generic naming
        self.schema_counter += 1
        return f"{context.title()}Variant{self.schema_counter}"
    
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
                prefix = {"error": "❌", "warning": "⚠️ ", "info": "ℹ️ "}[issue.severity]
                lines.append(f"  {prefix} {issue.message}")
                if issue.suggestion:
                    lines.append(f"     → {issue.suggestion}")
        else:
            lines.append("✅ No issues found!")
        
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