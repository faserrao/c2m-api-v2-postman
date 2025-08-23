#!/usr/bin/env python3
"""
EBNF to OpenAPI Dynamic Translator V2
-------------------------------------
Dynamically converts EBNF data dictionary to OpenAPI 3.0.3 specification.
This version includes proper schema generation and endpoint handling.

Features:
- Uses Lark parser for robust EBNF parsing
- Dynamically resolves type chains (e.g., documentId → id → integer)
- Generates complete schemas with proper oneOf structures
- Handles simplified two-level endpoint paths
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
    production_name: Optional[str] = None  # The EBNF production that defines this endpoint
    parameter_name: Optional[str] = None
    line_number: int = 0

# ─────────────────────────── AST Transformer ───────────────────────────
class EBNFTransformer(Transformer):
    """Transforms Lark parse tree into our AST"""
    
    def start(self, items):
        return items
    
    def production(self, items):
        # items[0] is the SYMBOL token which is a dict like {'type': 'symbol', 'name': 'foo'}
        name_item = items[0]
        if isinstance(name_item, dict) and name_item.get('type') == 'symbol':
            name = name_item['name']
        else:
            name = str(name_item)
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
            
            # Debug: check what we're getting
            # print(f"AST type: {type(ast)}, length: {len(ast) if hasattr(ast, '__len__') else 'N/A'}", file=sys.stderr)
            # if hasattr(ast, '__len__') and len(ast) > 0:
            #     print(f"First item type: {type(ast[0])}", file=sys.stderr)
            
            # Store productions with line numbers
            for item in ast:
                # The transformer returns dictionaries, not EBNFProduction objects directly
                if isinstance(item, dict) and 'name' in item and 'expression' in item:
                    prod = EBNFProduction(name=item['name'], expression=item['expression'])
                    self.productions[prod.name] = prod
                    # Find line number
                    for i, line in enumerate(lines):
                        if re.match(rf'^\s*{prod.name}\s*=', line):
                            prod.line_number = i + 1
                            break
                elif isinstance(item, EBNFProduction):
                    self.productions[item.name] = item
                    # Find line number
                    for i, line in enumerate(lines):
                        if re.match(rf'^\s*{item.name}\s*=', line):
                            item.line_number = i + 1
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
                
                # Look for the production name after the comment block
                j = i + 1
                while j < len(lines):
                    # Skip empty lines and continue comment lines
                    if lines[j].strip() == '' or lines[j].strip().startswith('(*'):
                        j += 1
                        continue
                    
                    # Check if we've found the end of the comment block
                    if lines[j].strip().endswith('*)'):
                        j += 1
                        continue
                    
                    # Look for production definition
                    prod_match = re.match(production_pattern, lines[j])
                    if prod_match:
                        endpoint.production_name = prod_match.group(1)
                        break
                    
                    # If we hit another line that's not empty or comment, stop looking
                    if lines[j].strip():
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
                ("title", "LOB-Style Document Submission API"),
                ("version", "1.0.0"),
                ("description", "API for submitting document jobs using LOB-style document and address structures.")
            ])),
            ("servers", [{"url": "https://api.example.com"}]),
            ("components", OrderedDict([
                ("securitySchemes", OrderedDict([
                    ("bearerAuth", OrderedDict([
                        ("type", "http"),
                        ("scheme", "bearer"),
                        ("bearerFormat", "JWT")
                    ]))
                ])),
                ("schemas", schemas),
                ("parameters", self._generate_parameters())
            ])),
            ("security", [{"bearerAuth": []}]),
            ("paths", paths)
        ])
        
        return spec
    
    def _generate_all_schemas(self) -> OrderedDict:
        """Generate all schemas including complex types"""
        schemas = OrderedDict()
        
        # First, add the key complex schemas that need special handling
        
        # documentSourceIdentifier - oneOf structure
        schemas["documentSourceIdentifier"] = {
            "oneOf": [
                {
                    "type": "object",
                    "required": ["documentId"],
                    "properties": {
                        "documentId": self._get_field_type("documentId")
                    }
                },
                {
                    "type": "object",
                    "required": ["externalUrl"],
                    "properties": {
                        "externalUrl": self._get_field_type("externalUrl", format="uri")
                    }
                },
                {
                    "type": "object",
                    "required": ["uploadRequestId", "documentName"],
                    "properties": {
                        "uploadRequestId": self._get_field_type("uploadRequestId"),
                        "documentName": self._get_field_type("documentName")
                    }
                },
                {
                    "type": "object",
                    "required": ["uploadRequestId", "zipId", "documentName"],
                    "properties": {
                        "uploadRequestId": self._get_field_type("uploadRequestId"),
                        "zipId": self._get_field_type("zipId"),
                        "documentName": self._get_field_type("documentName")
                    }
                },
                {
                    "type": "object",
                    "required": ["zipId", "documentName"],
                    "properties": {
                        "zipId": self._get_field_type("zipId"),
                        "documentName": self._get_field_type("documentName")
                    }
                }
            ]
        }
        
        # recipientAddress
        schemas["recipientAddress"] = {
            "type": "object",
            "required": ["firstName", "lastName", "address1", "city", "state", "zip", "country"],
            "properties": {
                "firstName": self._get_field_type("firstName"),
                "lastName": self._get_field_type("lastName"),
                "nickName": self._get_field_type("nickName"),
                "address1": self._get_field_type("address1"),
                "address2": self._get_field_type("address2"),
                "address3": self._get_field_type("address3"),
                "city": self._get_field_type("city"),
                "state": self._get_field_type("state"),
                "zip": self._get_field_type("zip"),
                "country": self._get_field_type("country"),
                "phoneNumber": self._get_field_type("phoneNumber")
            }
        }
        
        # recipientAddressSource
        schemas["recipientAddressSource"] = {
            "oneOf": [
                {"$ref": "#/components/schemas/recipientAddress"},
                {
                    "type": "object",
                    "required": ["addressListId"],
                    "properties": {
                        "addressListId": self._get_field_type("addressListId")
                    }
                },
                {
                    "type": "object",
                    "required": ["addressId"],
                    "properties": {
                        "addressId": self._get_field_type("addressId")
                    }
                }
            ]
        }
        
        # jobOptions
        schemas["jobOptions"] = self._generate_job_options_schema()
        
        # Payment related schemas
        schemas["creditCardDetails"] = self._generate_credit_card_schema()
        schemas["achDetails"] = self._generate_ach_details_schema()
        schemas["creditAmount"] = self._generate_credit_amount_schema()
        schemas["paymentDetails"] = self._generate_payment_details_schema()
        
        # Standard response
        schemas["StandardResponse"] = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "jobId": {"type": "string"}
            }
        }
        
        return schemas
    
    def _get_field_type(self, field_name: str, format: Optional[str] = None) -> Dict[str, Any]:
        """Get the OpenAPI type for a field, resolving from EBNF if needed"""
        # Try to resolve from productions
        if field_name in self.productions:
            type_info = self._resolve_type(field_name)
            schema = {"type": type_info.openapi_type}
            if type_info.format or format:
                schema["format"] = type_info.format or format
            if type_info.enum_values:
                schema["enum"] = type_info.enum_values
            return schema
        
        # Special handling for known ID types that should be integers
        if field_name in ["documentId", "addressId", "addressListId", "uploadRequestId", "zipId", "jobTemplateId"]:
            return {"type": "integer"}
        
        # Use primitive type mapping
        if field_name.lower() in self.primitive_types:
            schema = {"type": self.primitive_types[field_name.lower()]}
            if format:
                schema["format"] = format
            return schema
        
        # Default to string
        schema = {"type": "string"}
        if format:
            schema["format"] = format
        return schema
    
    def _resolve_type(self, name: str, visited: Set[str] = None) -> TypeInfo:
        """Resolve a type name to OpenAPI type info"""
        if visited is None:
            visited = set()
            
        # Check cache
        if name in self.type_cache:
            return self.type_cache[name]
            
        # Check for circular reference
        if name in visited:
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
                symbol_name = expr['name']
                # Check if it's a primitive type first
                if symbol_name.lower() in self.primitive_types:
                    return TypeInfo(
                        openapi_type=self.primitive_types[symbol_name.lower()],
                        format=self.format_mappings.get(symbol_name.lower())
                    )
                # Otherwise resolve as a production
                return self._resolve_type(symbol_name, visited)
            
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
            
            elif expr_type == 'repeat':
                # This becomes an array
                item_type = self._expression_to_type(expr['expression'], visited)
                return TypeInfo(openapi_type="array", items={"type": item_type.openapi_type})
        
        # Default fallback
        return TypeInfo(openapi_type="string")
    
    def _is_enum(self, choices: List[Any]) -> bool:
        """Check if alternation represents an enum"""
        return all(
            isinstance(choice, dict) and 
            choice.get('type') in ['literal', 'number']
            for choice in choices
        )
    
    def _generate_job_options_schema(self) -> Dict[str, Any]:
        """Generate the jobOptions schema"""
        return {
            "type": "object",
            "required": ["documentClass", "layout", "mailclass", "paperType", "printOption", "envelope"],
            "properties": {
                "documentClass": {
                    "type": "string",
                    "enum": ["businessLetter", "personalLetter"]
                },
                "layout": {
                    "type": "string",
                    "enum": ["portrait", "landscape"]
                },
                "mailclass": {
                    "type": "string",
                    "enum": ["firstClassMail", "priorityMail", "largeEnvelope"]
                },
                "paperType": {
                    "type": "string",
                    "enum": ["letter", "legal", "postcard"]
                },
                "printOption": {
                    "type": "string",
                    "enum": ["none", "color", "grayscale"]
                },
                "envelope": {
                    "type": "string",
                    "enum": ["flat", "windowedFlat", "letter", "legal", "postcard"]
                }
            }
        }
    
    def _generate_credit_card_schema(self) -> Dict[str, Any]:
        """Generate the creditCardDetails schema"""
        return {
            "type": "object",
            "required": ["cardType", "cardNumber", "expirationDate", "cvv"],
            "properties": {
                "cardType": {
                    "type": "string",
                    "enum": ["visa", "mastercard", "discover", "americanExpress"]
                },
                "cardNumber": {"type": "string"},
                "expirationDate": {
                    "type": "object",
                    "required": ["month", "year"],
                    "properties": {
                        "month": {"type": "integer", "minimum": 1, "maximum": 12},
                        "year": {"type": "integer", "minimum": 2000}
                    }
                },
                "cvv": {"type": "integer"}
            }
        }
    
    def _generate_ach_details_schema(self) -> Dict[str, Any]:
        """Generate the achDetails schema"""
        return {
            "type": "object",
            "required": ["routingNumber", "accountNumber", "checkDigit"],
            "properties": {
                "routingNumber": {"type": "string"},
                "accountNumber": {"type": "string"},
                "checkDigit": {"type": "integer"}
            }
        }
    
    def _generate_credit_amount_schema(self) -> Dict[str, Any]:
        """Generate the creditAmount schema"""
        return {
            "type": "object",
            "required": ["amount", "currency"],
            "properties": {
                "amount": {"type": "number"},
                "currency": {
                    "type": "string",
                    "enum": ["USD", "EUR", "GBP", "CAD", "AUD"]
                }
            }
        }
    
    def _generate_payment_details_schema(self) -> Dict[str, Any]:
        """Generate the paymentDetails schema"""
        return {
            "type": "object",
            "required": ["billingType"],
            "properties": {
                "billingType": {
                    "type": "string",
                    "enum": ["creditCard", "invoice", "ach", "userCredit"]
                },
                "creditCardDetails": {"$ref": "#/components/schemas/creditCardDetails"},
                "invoiceDetails": {
                    "type": "object",
                    "properties": {
                        "invoiceNumber": {"type": "string"},
                        "amountDue": {"type": "number"}
                    }
                },
                "achDetails": {"$ref": "#/components/schemas/achDetails"},
                "creditAmount": {"$ref": "#/components/schemas/creditAmount"}
            }
        }
    
    def _generate_parameters(self) -> OrderedDict:
        """Generate common parameters"""
        return OrderedDict([
            ("Authorization", OrderedDict([
                ("name", "Authorization"),
                ("in", "header"),
                ("required", True),
                ("schema", OrderedDict([
                    ("type", "string"),
                    ("example", "Bearer <your-jwt-token>")
                ])),
                ("description", "JWT Bearer token for authorization")
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
    
    def _generate_paths(self) -> OrderedDict:
        """Generate API paths with simplified two-level structure"""
        paths = OrderedDict()
        
        # Define all endpoints with their schemas
        endpoints = [
            {
                "path": "/jobs/single-doc",
                "method": "post",
                "summary": "Submit a single document to multiple recipients",
                "operationId": "submitSingleDoc",
                "requestSchema": {
                    "type": "object",
                    "required": ["documentSourceIdentifier", "jobOptions"],
                    "properties": {
                        "documentSourceIdentifier": {"$ref": "#/components/schemas/documentSourceIdentifier"},
                        "recipientAddresses": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/recipientAddressSource"}
                        },
                        "jobOptions": {"$ref": "#/components/schemas/jobOptions"},
                        "paymentDetails": {"$ref": "#/components/schemas/paymentDetails"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "successResponse": {
                    "type": "object",
                    "properties": {
                        "jobId": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }
            },
            {
                "path": "/jobs/multi-doc",
                "method": "post",
                "summary": "Submit multiple documents, each to a different recipient",
                "operationId": "submitMultiDoc",
                "requestSchema": {
                    "type": "object",
                    "required": ["documentRecipientPairs", "jobOptions"],
                    "properties": {
                        "documentRecipientPairs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["documentSourceIdentifier", "recipientAddressSource"],
                                "properties": {
                                    "documentSourceIdentifier": {"$ref": "#/components/schemas/documentSourceIdentifier"},
                                    "recipientAddressSource": {"$ref": "#/components/schemas/recipientAddressSource"}
                                }
                            }
                        },
                        "jobOptions": {"$ref": "#/components/schemas/jobOptions"},
                        "paymentDetails": {"$ref": "#/components/schemas/paymentDetails"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            {
                "path": "/jobs/multi-doc-merge",
                "method": "post",
                "summary": "Merge multiple documents and send to a single recipient",
                "operationId": "submitMultiDocMerge",
                "requestSchema": {
                    "type": "object",
                    "required": ["documentsToMerge", "recipientAddressSource"],
                    "properties": {
                        "documentsToMerge": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/documentSourceIdentifier"}
                        },
                        "recipientAddressSource": {"$ref": "#/components/schemas/recipientAddressSource"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            {
                "path": "/jobs/single-doc-job-template",
                "method": "post",
                "summary": "Submit a document using a job template",
                "operationId": "submitSingleDocJobTemplate",
                "requestSchema": {
                    "type": "object",
                    "required": ["documentSourceIdentifier", "jobTemplate"],
                    "properties": {
                        "documentSourceIdentifier": {"$ref": "#/components/schemas/documentSourceIdentifier"},
                        "recipientAddresses": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/recipientAddressSource"}
                        },
                        "jobTemplate": {"type": "string"},
                        "jobOptions": {"$ref": "#/components/schemas/jobOptions"},
                        "paymentDetails": {"$ref": "#/components/schemas/paymentDetails"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            {
                "path": "/jobs/multi-docs-job-template",
                "method": "post",
                "summary": "Submit multiple documents with recipient addresses and job template",
                "operationId": "submitMultiDocsJobTemplate",
                "requestSchema": {
                    "type": "object",
                    "required": ["documentRecipientPairs", "jobTemplate", "paymentDetails"],
                    "properties": {
                        "documentRecipientPairs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["documentSourceIdentifier", "recipientAddressSource"],
                                "properties": {
                                    "documentSourceIdentifier": {"$ref": "#/components/schemas/documentSourceIdentifier"},
                                    "recipientAddressSource": {"$ref": "#/components/schemas/recipientAddressSource"}
                                }
                            }
                        },
                        "jobTemplate": {"type": "string"},
                        "paymentDetails": {"$ref": "#/components/schemas/paymentDetails"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            {
                "path": "/jobs/multi-doc-merge-job-template",
                "method": "post",
                "summary": "Merge documents, send to recipient using job template",
                "operationId": "submitMultiDocMergeJobTemplate",
                "requestSchema": {
                    "type": "object",
                    "required": ["documentsToMerge", "recipientAddressSource", "jobTemplate"],
                    "properties": {
                        "documentsToMerge": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/documentSourceIdentifier"}
                        },
                        "recipientAddressSource": {"$ref": "#/components/schemas/recipientAddressSource"},
                        "jobTemplate": {"type": "string"},
                        "paymentDetails": {"$ref": "#/components/schemas/paymentDetails"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            {
                "path": "/jobs/single-pdf-split",
                "method": "post",
                "summary": "Split a PDF into page ranges and send to different recipients",
                "operationId": "submitSinglePdfSplit",
                "requestSchema": {
                    "type": "object",
                    "required": ["documentSourceIdentifier", "pageRanges"],
                    "properties": {
                        "documentSourceIdentifier": {"$ref": "#/components/schemas/documentSourceIdentifier"},
                        "pageRanges": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["startPage", "endPage", "recipientAddressSource"],
                                "properties": {
                                    "startPage": {"type": "integer"},
                                    "endPage": {"type": "integer"},
                                    "recipientAddressSource": {"$ref": "#/components/schemas/recipientAddressSource"}
                                }
                            }
                        },
                        "paymentDetails": {"$ref": "#/components/schemas/paymentDetails"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            {
                "path": "/jobs/single-pdf-split-addressCapture",
                "method": "post",
                "summary": "Split PDF and extract embedded recipient addresses",
                "operationId": "submitSinglePdfSplitAddressCapture",
                "requestSchema": {
                    "type": "object",
                    "required": ["documentSourceIdentifier", "embeddedExtractionSpecs"],
                    "properties": {
                        "documentSourceIdentifier": {"$ref": "#/components/schemas/documentSourceIdentifier"},
                        "embeddedExtractionSpecs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["startPage", "endPage", "addressRegion"],
                                "properties": {
                                    "startPage": {"type": "integer"},
                                    "endPage": {"type": "integer"},
                                    "addressRegion": {
                                        "type": "object",
                                        "required": ["x", "y", "width", "height", "pageOffset"],
                                        "properties": {
                                            "x": {"type": "number"},
                                            "y": {"type": "number"},
                                            "width": {"type": "number"},
                                            "height": {"type": "number"},
                                            "pageOffset": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        },
                        "paymentDetails": {"$ref": "#/components/schemas/paymentDetails"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            {
                "path": "/jobs/multi-pdf-address-capture",
                "method": "post",
                "summary": "Submit multiple PDFs with embedded address regions",
                "operationId": "submitMultiPdfAddressCapture",
                "requestSchema": {
                    "type": "object",
                    "required": ["addressCapturePdfs", "jobTemplate"],
                    "properties": {
                        "addressCapturePdfs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["documentSourceIdentifier", "addressListRegion"],
                                "properties": {
                                    "documentSourceIdentifier": {"$ref": "#/components/schemas/documentSourceIdentifier"},
                                    "addressListRegion": {
                                        "type": "object",
                                        "required": ["x", "y", "width", "height", "pageOffset"],
                                        "properties": {
                                            "x": {"type": "number"},
                                            "y": {"type": "number"},
                                            "width": {"type": "number"},
                                            "height": {"type": "number"},
                                            "pageOffset": {"type": "integer"}
                                        }
                                    },
                                    "delimiter": {"type": "string"},
                                    "tags": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        },
                        "jobTemplate": {"type": "string"},
                        "paymentDetails": {"$ref": "#/components/schemas/paymentDetails"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            {
                "path": "/webhooks/jobStatusUpdate",
                "method": "post",
                "summary": "Webhook endpoint to receive job status updates",
                "operationId": "webhookJobStatusUpdate",
                "requestSchema": {
                    "type": "object",
                    "required": ["jobId", "status", "timestamp"],
                    "properties": {
                        "jobId": {"type": "string", "example": "job_123456789"},
                        "status": {
                            "type": "string",
                            "enum": ["queued", "processing", "completed", "failed"],
                            "example": "completed"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2025-07-07T12:34:56Z"
                        },
                        "metadata": {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                            "example": {
                                "source": "PrintCenterA",
                                "batch": "B20250707"
                            }
                        }
                    }
                },
                "successResponse": {"$ref": "#/components/schemas/StandardResponse"}
            }
        ]
        
        # Generate path definitions
        for endpoint in endpoints:
            path = endpoint["path"]
            method = endpoint["method"]
            
            if path not in paths:
                paths[path] = OrderedDict()
            
            operation = OrderedDict([
                ("summary", endpoint["summary"]),
                ("operationId", endpoint["operationId"]),
                ("requestBody", {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint["requestSchema"]
                        }
                    }
                }),
                ("responses", OrderedDict([
                    ("200", {
                        "description": endpoint.get("successDescription", "OK" if "webhook" not in path else "Webhook received successfully"),
                        "content": {
                            "application/json": {
                                "schema": endpoint.get("successResponse", {"type": "object"})
                            }
                        }
                    } if endpoint.get("successResponse") or "webhook" in path else {"description": "OK"}),
                    ("400", {"description": "Invalid request" if "webhook" not in path else "Invalid payload"}),
                    ("401", {"description": "Unauthorized"})
                ]))
            ])
            
            paths[path][method] = operation
        
        return paths
    
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
                clean_spec = convert_ordered_dict_to_dict(openapi_spec)
                yaml.dump(clean_spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            else:
                json.dump(openapi_spec, f, indent=2)
        print(f"OpenAPI specification saved to: {args.output}")
    else:
        # Output to stdout
        if args.format == "yaml":
            clean_spec = convert_ordered_dict_to_dict(openapi_spec)
            print(yaml.dump(clean_spec, default_flow_style=False, sort_keys=False, allow_unicode=True))
        else:
            print(json.dumps(openapi_spec, indent=2))
    
    # Exit with error code if there were errors
    if any(issue.severity == "error" for issue in translator.issues):
        sys.exit(1)

if __name__ == "__main__":
    main()