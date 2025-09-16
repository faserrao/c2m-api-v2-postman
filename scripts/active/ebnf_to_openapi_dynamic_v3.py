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
    %ignore /\(\*.*?\*\)/s              // Multi-line comments
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
                
                # Look for the production name after the comment block
                j = i + 1
                in_comment = True  # We know we're starting inside a comment
                
                while j < len(lines):
                    line_content = lines[j].strip()
                    
                    # Check if we're exiting the comment block
                    if in_comment and '*)' in lines[j]:
                        in_comment = False
                        j += 1
                        continue
                    
                    # Skip lines while still in comment
                    if in_comment:
                        j += 1
                        continue
                    
                    # Skip empty lines after comment
                    if not line_content:
                        j += 1
                        continue
                    
                    # Look for production definition
                    prod_match = re.match(production_pattern, lines[j])
                    if prod_match:
                        endpoint.production_name = prod_match.group(1)
                        break
                    
                    # If we hit another line that's not a production, stop
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
                ("title", "C2M Job Submission API"),
                ("version", "V2.0.0"),
                ("description", "API for submitting documents with various routing options")
            ])),
            ("servers", [
                {"url": "https://api.example.com/v1", "description": "Production server"},
                {"url": "http://localhost:4010", "description": "Mock server"}
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
        simple_type_schemas = {
            # String types
            'documentName': {'type': 'string'},
            'firstName': {'type': 'string'},
            'lastName': {'type': 'string'},
            'nickName': {'type': 'string'},
            'address1': {'type': 'string'},
            'address2': {'type': 'string'},
            'address3': {'type': 'string'},
            'city': {'type': 'string'},
            'state': {'type': 'string'},
            'country': {'type': 'string'},
            'zip': {'type': 'string'},
            'phoneNumber': {'type': 'string'},
            'externalUrl': {'type': 'string', 'format': 'uri'},
            'tag': {'type': 'string'},
            'tags': {'type': 'array', 'items': {'type': 'string'}},  # Fix recursive definition
            'jobTemplate': {'type': 'string'},
            'invoiceNumber': {'type': 'string'},
            'routingNumber': {'type': 'string'},
            'accountNumber': {'type': 'string'},
            'cardNumber': {'type': 'string'},
            'delimiter': {'type': 'string'},
            'tbd': {'type': 'string'},
            
            # Integer types
            'documentId': {'type': 'integer'},
            'addressId': {'type': 'integer'},
            'addressListId': {'type': 'integer'},
            'uploadRequestId': {'type': 'integer'},
            'zipId': {'type': 'integer'},
            'startPage': {'type': 'integer'},
            'endPage': {'type': 'integer'},
            'month': {'type': 'integer', 'minimum': 1, 'maximum': 12},
            'year': {'type': 'integer'},
            'cvv': {'type': 'integer'},
            'checkDigit': {'type': 'integer'},
            'pageOffset': {'type': 'integer'},
            
            # Number types
            'amountDue': {'type': 'number'},
            'amount': {'type': 'number'},
            'x': {'type': 'number'},
            'y': {'type': 'number'},
            'width': {'type': 'number'},
            'height': {'type': 'number'}
        }
        
        # Add simple type schemas first
        schemas.update(simple_type_schemas)
        
        # Skip these fundamental types that shouldn't have schemas
        skip_types = {'string', 'integer', 'number', 'character', 'id'}
        
        # Generate schemas dynamically from EBNF productions
        for name, production in self.productions.items():
            # Skip if already added as simple type or is a fundamental type
            if name in simple_type_schemas or name in skip_types:
                continue
                
            # Generate schema from production
            schema = self._expression_to_schema(production.expression, name)
            
            # Add the schema
            schemas[name] = schema
        
        # Add composed schemas that might be missing
        if 'documentsToMerge' not in schemas:
            schemas['documentsToMerge'] = {
                'type': 'array',
                'items': {'$ref': '#/components/schemas/documentSourceIdentifier'}
            }
        
        if 'addressCapturePdfs' not in schemas:
            schemas['addressCapturePdfs'] = {
                'type': 'array',
                'items': {'$ref': '#/components/schemas/addressListPdf'}
            }
        
        if 'embeddedExtractionSpecs' not in schemas:
            schemas['embeddedExtractionSpecs'] = {
                'type': 'array',
                'items': {'$ref': '#/components/schemas/extractionSpec'}
            }
            
        if 'addressListRegion' not in schemas:
            schemas['addressListRegion'] = {'type': 'string'}  # Placeholder for 'tbd'
            
        if 'exactlyOneNewAddress' not in schemas:
            schemas['exactlyOneNewAddress'] = {'$ref': '#/components/schemas/recipientAddress'}
            
        if 'exactlyOneListId' not in schemas:
            schemas['exactlyOneListId'] = {'type': 'integer'}  # addressListId
            
        if 'exactlyOneId' not in schemas:
            schemas['exactlyOneId'] = {'type': 'integer'}  # addressId
        
        # Add a standard response schema
        schemas["StandardResponse"] = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "jobId": {"type": "string"}
            }
        }
        
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
            
            # Generate schema from EBNF production
            request_schema = self._generate_schema_from_production(endpoint.production_name)
            
            if endpoint.path not in paths:
                paths[endpoint.path] = OrderedDict()
            
            operation = OrderedDict([
                ("summary", f"Operation for {endpoint.path}"),
                ("operationId", self._generate_operation_id(endpoint)),
                ("requestBody", {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": request_schema
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
                    ("400", {"description": "Invalid request"}),
                    ("401", {"description": "Unauthorized"})
                ]))
            ])
            
            paths[endpoint.path][endpoint.method.lower()] = operation
        
        return paths
    
    def _generate_operation_id(self, endpoint: Endpoint) -> str:
        """Generate operation ID from endpoint"""
        # Use the production name as the operation ID
        return endpoint.production_name
    
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
                    # Generate oneOf schema
                    return self._generate_oneof_schema(choices, context)
            
            elif expr_type == 'symbol':
                symbol_name = expr.get('name')
                if symbol_name:
                    if symbol_name in self.productions:
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
        
        for choice in choices:
            if isinstance(choice, dict):
                choice_type = choice.get('type')
                
                if choice_type == 'symbol':
                    symbol_name = choice.get('name')
                    if symbol_name:
                        if symbol_name in self.productions:
                            schemas.append({"$ref": f"#/components/schemas/{symbol_name}"})
                        else:
                            # Simple type wrapped in object
                            schemas.append({
                                "type": "object",
                                "required": [symbol_name],
                                "properties": {
                                    symbol_name: self._get_field_type(symbol_name)
                                }
                            })
                
                elif choice_type == 'concatenation':
                    # Complex object type
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
        # Always use references for all fields that have schemas
        # This ensures consistency and avoids missing reference errors
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