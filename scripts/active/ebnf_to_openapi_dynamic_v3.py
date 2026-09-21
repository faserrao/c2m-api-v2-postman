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
_DEFAULT_API_DESCRIPTION = "API for submitting mailing jobs with various document routing options"

# ── Field-name heuristics ─────────────────────────────────────────────────
# Keyword priority lists for locating doc/address symbols via graph traversal.
_DOC_FIELD_KEYWORDS  = ['docSource', 'documentSource', 'document']
_ADDR_FIELD_KEYWORDS = ['addressSource', 'recipientAddress', 'addressList', 'address']

# ── JWT example token ─────────────────────────────────────────────────────
_JWT_EXAMPLE_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# ── H4: HTTP response description strings ────────────────────────────────
# Centralised here so they can be updated without hunting through _generate_paths().
_HTTP_STATUS_DESCRIPTIONS: Dict[str, str] = {
    '200': "Success",
    '400': "Bad Request - Invalid request parameters",
    '401': "Unauthorized - Missing or invalid authentication",
    '403': "Forbidden - Insufficient permissions",
    '404': "Not Found - Resource not found",
    '422': "Unprocessable Entity - Validation failed",
    '429': "Too Many Requests - Rate limit exceeded",
    '500': "Internal Server Error - Server encountered an error",
}

# ── M1: OpenAPI tag name / description ───────────────────────────────────
_OPENAPI_TAG_NAME        = "jobs"
_OPENAPI_TAG_DESCRIPTION = "Job submission endpoints"

# ── M2: Security scheme name ──────────────────────────────────────────────
_SECURITY_SCHEME_NAME = "bearerAuth"

# ── M5: Shared media-type constant ───────────────────────────────────────
_CONTENT_TYPE_JSON = "application/json"

# ── H1: Operational constants used in error-detail examples ──────────────
# These are intentional stable strings — not derivable from EBNF or OpenAPI spec.
_ERROR_DB_TABLE            = "jobs"
_ERROR_EXTERNAL_SERVICE    = "address-validation"  # BUG fix: aligned with error-response-examples.yaml
_ERROR_AUTH_SCOPE_REQUIRED = "jobs:write"
_ERROR_AUTH_SCOPE_PROVIDED = "jobs:read"
# A-new-1: Build-failure guard only — primary path uses _get_enum_values('documentClass')
# from the spec.  This list is unreachable in a normal build; a constant keeps it auditable.
_ERROR_DOCUMENT_CLASS_FALLBACK = ["letter", "postcard", "brochure", "flat"]
# H1: Fallback used when the @mutual_exclusion annotation is absent from the EBNF DD.
# The authoritative source is the @mutual_exclusion block in data_dictionary/c2mapiv2-dd.ebnf;
# the translator stores parsed values in self.mutual_exclusion_fields at parse time.
_MUTUAL_EXCLUSION_FIELDS = ["jobTemplate", "jobOptions"]

# ── D1: Response schema name constants ───────────────────────────────────
# These are EBNF DD rule names (standardResponse, errorResponse) used as
# OpenAPI component schema names.  Centralised here so a DD rule rename
# surfaces a single change point rather than silent $ref breakage.
_RESPONSE_SCHEMA_NAME = "standardResponse"
_ERROR_SCHEMA_NAME    = "errorResponse"

# ── F1: Address field name used in error-detail examples ─────────────────
_ERROR_POSTAL_FIELD = "postalCode"


def _load_error_code_messages() -> Dict[str, str]:
    """H2: Load errorCode → errorMessage from error-response-examples.yaml.

    Single source of truth shared with add_response_examples.py and
    add_error_responses_to_collection.js.  Eliminates the hardcoded
    status_to_messages dict that previously duplicated YAML content.
    """
    config = Path(__file__).parent.parent.parent / 'config' / 'error-response-examples.yaml'
    try:
        with open(config) as f:
            raw = yaml.safe_load(f)
        return {
            ex['errorCode']: ex['errorMessage']
            for status_examples in raw.values()
            for ex in status_examples.values()
            if isinstance(ex, dict) and 'errorCode' in ex
        }
    except (OSError, KeyError, TypeError):
        return {}


# Built once at import time — stable config file, no need to re-read per call.
_ERROR_CODE_MESSAGES: Dict[str, str] = _load_error_code_messages()


def _generate_tracking_id() -> str:
    """H3: Generate a unique error tracking ID.

    Format: TRK-{YYYYMMDD}-{6-char hex suffix}
    Same format as _generate_tracking_id() in add_response_examples.py.
    Update both if the format changes.
    """
    suffix = ''.join(random.choices('0123456789ABCDEF', k=6))
    return f"TRK-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{suffix}"

# Structural role classifications for EBNF rules are declared via (* @structural role *)
# annotations in the DD itself and loaded dynamically in parse_ebnf() below.
# See _extract_structural_annotations() for the extraction logic.
#
# Role semantics (used in _expression_to_schema / _generate_oneof_schema):
#   single_field_wrapper     — rule of form `a = b ;` that must become
#                              { type: object, properties: { b: T }, required: [b] }
#                              so it is structurally distinct from sibling oneOf variants.
#   named_wrapper_oneof      — union rule whose variants are wrapped in the variant's
#                              type name as a JSON key:
#                              { "variantName": { ...variantSchema } }
#   transparent_oneof_grouping — union rule that is inlined (expanded) when it appears
#                              as a choice inside another union (e.g. docSourceAll).

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
    summary: Optional[str] = None
    description: Optional[str] = None

def _extract_structural_annotations(ebnf_text: str) -> Dict[str, Set[str]]:
    """Extract @structural role annotations from EBNF rules.

    Format: (* @structural role1 role2 *) — space-separated roles.
    Works for both single-line and multi-line rules: the annotation must appear
    on the same line as (or after) the rule's closing ';'.

    Returns {rule_name: {role1, role2, ...}}
    """
    result: Dict[str, Set[str]] = {}
    current_rule: Optional[str] = None
    rule_start = re.compile(r'^([a-zA-Z][a-zA-Z0-9_]*)\s*=')
    annotation = re.compile(r'\(\*\s*@structural\s+([^*]+?)\s*\*\)')

    for line in ebnf_text.split('\n'):
        m = rule_start.match(line)
        if m:
            current_rule = m.group(1)
        if current_rule:
            sm = annotation.search(line)
            if sm:
                result[current_rule] = set(sm.group(1).split())
    return result


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
        self.mutual_exclusion_fields: List[str] = list(_MUTUAL_EXCLUSION_FIELDS)  # Parsed from @mutual_exclusion
        # Structural role sets — populated by parse_ebnf() from @structural annotations in the DD
        self._single_field_wrapper_rules: frozenset = frozenset()
        self._named_wrapper_oneof_rules: frozenset = frozenset()
        self._transparent_oneof_groupings: frozenset = frozenset()
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
        parsed_mutual = self._parse_mutual_exclusion(content)
        if parsed_mutual:
            self.mutual_exclusion_fields = parsed_mutual

        # Load structural role sets from @structural annotations in the DD
        structural = _extract_structural_annotations(content)
        self._single_field_wrapper_rules = frozenset(
            name for name, roles in structural.items() if 'single_field_wrapper' in roles
        )
        self._named_wrapper_oneof_rules = frozenset(
            name for name, roles in structural.items() if 'named_wrapper_oneof' in roles
        )
        self._transparent_oneof_groupings = frozenset(
            name for name, roles in structural.items() if 'transparent_oneof_grouping' in roles
        )
        # Guard: missing annotations mean silently wrong spec output — fail loudly
        for attr, min_expected in [
            ('_single_field_wrapper_rules', 5),
            ('_named_wrapper_oneof_rules', 6),
            ('_transparent_oneof_groupings', 2),
        ]:
            actual = len(getattr(self, attr))
            if actual < min_expected:
                self.issues.append(Issue(
                    severity='error',
                    message=(
                        f"@structural annotations: {attr} has {actual} member(s), "
                        f"expected at least {min_expected}. "
                        f"Add (* @structural ... *) to the relevant EBNF rules."
                    )
                ))

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

    def _parse_mutual_exclusion(self, content: str) -> List[str]:
        """Parse @mutual_exclusion annotation from EBNF content.

        Returns a list of field names that are mutually exclusive (only one per request).
        Format in EBNF:  @mutual_exclusion field1, field2, ...
        Returns empty list if the annotation is absent.
        """
        match = re.search(r'@mutual_exclusion\s+([^\n]+)', content)
        if not match:
            return []
        return [f.strip() for f in match.group(1).split(',') if f.strip()]

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
                
                # Look for the production name after the comment block(s).
                # Also capture @summary / @description annotations from comment lines.
                j = i + 1
                in_comment = '(*' in lines[i] and not lines[i].strip().endswith('*)')
                summary_pat = re.compile(r'\(\*\s*@summary\s+(.+?)\s*\*\)')
                desc_pat = re.compile(r'\(\*\s*@description\s+(.+?)\s*\*\)')

                while j < len(lines):
                    line_content = lines[j].strip()

                    # Capture @summary / @description before any skip logic
                    sm = summary_pat.search(lines[j])
                    if sm:
                        endpoint.summary = sm.group(1).strip()
                    dm = desc_pat.search(lines[j])
                    if dm:
                        endpoint.description = dm.group(1).strip()

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
            ("description", _DEFAULT_API_DESCRIPTION),
            ("x-http-error-map", self.http_error_map),
        ])
        if self.numeric_constraints:
            info["x-numeric-constraints"] = self.numeric_constraints
        if self.valid_combinations:
            info["x-valid-combinations"] = self.valid_combinations
        if self.mutual_exclusion_fields:
            info["x-mutual-exclusion"] = self.mutual_exclusion_fields

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
                    "name": _OPENAPI_TAG_NAME,
                    "description": _OPENAPI_TAG_DESCRIPTION,
                }
            ]),
            ("components", OrderedDict([
                ("schemas", schemas),
                ("parameters", self._generate_parameters()),
                ("securitySchemes", OrderedDict([
                    (_SECURITY_SCHEME_NAME, OrderedDict([
                        ("type", "http"),
                        ("scheme", "bearer"),
                        ("bearerFormat", "JWT")
                    ]))
                ]))
            ])),
            ("security", [{_SECURITY_SCHEME_NAME: []}]),
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

            endpoint_tags = [_OPENAPI_TAG_NAME]

            operation = OrderedDict([
                ("tags", endpoint_tags),
                ("summary", self._generate_summary(endpoint)),
                ("description", self._generate_description(endpoint)),
                ("operationId", self._generate_operation_id(endpoint)),
                ("requestBody", {
                    "required": True,
                    "content": {
                        _CONTENT_TYPE_JSON: {
                            "schema": {"$ref": f"#/components/schemas/{endpoint.production_name}"}
                        }
                    }
                }),
                ("responses", OrderedDict([
                    ("200", {
                        "description": _HTTP_STATUS_DESCRIPTIONS['200'],
                        "content": {
                            _CONTENT_TYPE_JSON: {
                                "schema": {"$ref": f"#/components/schemas/{_RESPONSE_SCHEMA_NAME}"}
                            }
                        }
                    }),
                    ("400", {
                        "description": _HTTP_STATUS_DESCRIPTIONS['400'],
                        "content": {
                            _CONTENT_TYPE_JSON: {
                                "schema": {"$ref": f"#/components/schemas/{_ERROR_SCHEMA_NAME}"},
                                "examples": self._generate_error_examples("400", endpoint)
                            }
                        }
                    }),
                    ("401", {
                        "description": _HTTP_STATUS_DESCRIPTIONS['401'],
                        "content": {
                            _CONTENT_TYPE_JSON: {
                                "schema": {"$ref": f"#/components/schemas/{_ERROR_SCHEMA_NAME}"},
                                "examples": self._generate_error_examples("401", endpoint)
                            }
                        }
                    }),
                    ("403", {
                        "description": _HTTP_STATUS_DESCRIPTIONS['403'],
                        "content": {
                            _CONTENT_TYPE_JSON: {
                                "schema": {"$ref": f"#/components/schemas/{_ERROR_SCHEMA_NAME}"},
                                "examples": self._generate_error_examples("403", endpoint)
                            }
                        }
                    }),
                    ("404", {
                        "description": _HTTP_STATUS_DESCRIPTIONS['404'],
                        "content": {
                            _CONTENT_TYPE_JSON: {
                                "schema": {"$ref": f"#/components/schemas/{_ERROR_SCHEMA_NAME}"},
                                "examples": self._generate_error_examples("404", endpoint)
                            }
                        }
                    }),
                    ("422", {
                        "description": _HTTP_STATUS_DESCRIPTIONS['422'],
                        "content": {
                            _CONTENT_TYPE_JSON: {
                                "schema": {"$ref": f"#/components/schemas/{_ERROR_SCHEMA_NAME}"},
                                "examples": self._generate_error_examples("422", endpoint)
                            }
                        }
                    }),
                    ("500", {
                        "description": _HTTP_STATUS_DESCRIPTIONS['500'],
                        "content": {
                            _CONTENT_TYPE_JSON: {
                                "schema": {"$ref": f"#/components/schemas/{_ERROR_SCHEMA_NAME}"},
                                "examples": self._generate_error_examples("500", endpoint)
                            }
                        }
                    })
                ]))
            ])
            
            paths[endpoint.path][endpoint.method.lower()] = operation

        # Drift check: warn if any endpoint is missing @summary or @description
        # annotations in the EBNF DD. Add (* @summary ... *) and (* @description ... *)
        # lines after the (* Endpoint: METHOD /path *) header to resolve.
        for path in paths:
            ep = next((e for e in self.endpoints if e.path == path), None)
            if ep and not ep.summary:
                self.issues.append(Issue(
                    severity="warning",
                    message=(
                        f"No @summary annotation for endpoint '{path}' — spec will use "
                        f"auto-generated text. Add (* @summary ... *) after the "
                        f"(* Endpoint: ... *) header in the EBNF DD."
                    )
                ))

        return paths
    
    def _generate_operation_id(self, endpoint: Endpoint) -> str:
        """Generate operation ID from endpoint"""
        # Use the production name as the operation ID
        return endpoint.production_name

    def _generate_summary(self, endpoint: Endpoint) -> str:
        """Generate a brief summary from endpoint path."""
        if endpoint.summary:
            return endpoint.summary
        # Fallback: preserve camelCase production name (never call .title() on camelCase)
        return endpoint.production_name

    def _generate_description(self, endpoint: Endpoint) -> str:
        """Generate a detailed description from endpoint."""
        if endpoint.description:
            return endpoint.description
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

        # Extract endpoint-specific field names for contextual error details
        field_names = self._extract_endpoint_field_names(endpoint)

        # Generate examples for this status code
        examples = {}
        map_entry = self.http_error_map.get(status_code, {})
        error_type = map_entry.get('errorType', 'ServerError')
        codes = map_entry.get('errorCodes', ['SERVER_ERROR'])

        # H2: messages sourced from error-response-examples.yaml via _ERROR_CODE_MESSAGES
        # (same YAML consumed by add_response_examples.py and the JS collection injector)
        def _msg(code: str) -> str:
            return _ERROR_CODE_MESSAGES.get(code, code.replace('_', ' ').capitalize())

        # Create one example per error code for this status
        for idx, code in enumerate(codes):
            tracking_id = _generate_tracking_id()  # H3: canonical format

            # Generate contextual error details
            details = self._generate_error_details(status_code, code, field_names)

            # Create example
            example_name = f"example-{idx+1}"
            examples[example_name] = {
                "value": {
                    "errorType": error_type,
                    "errorMessage": _msg(code),
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
            for item in expr.get('choices', []):
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
        for kw in _DOC_FIELD_KEYWORDS:
            match = next((s for s in all_symbols if kw.lower() in s.lower()), None)
            if match:
                field_names['documentField'] = match
                break

        # Find address field similarly.
        for kw in _ADDR_FIELD_KEYWORDS:
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
        """Generate contextual error details based on error type.

        NOTE: This dict is intentionally separate from config/error-response-examples.yaml.
        That YAML drives Postman collection and Newman test examples.
        This dict drives OpenAPI spec-level examples (rendered in Redoc/Swagger UI).
        Unlike the YAML, it uses field_names.get() for spec-derived field names — do not
        replace with YAML loading, as that would lose the dynamic field-name resolution.
        """
        # H1: operational constants (_ERROR_DB_TABLE etc.) are declared at module level —
        # not derivable from EBNF or spec, but now easy to find and update in one place.
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
                "required": _ERROR_AUTH_SCOPE_REQUIRED,
                "provided": _ERROR_AUTH_SCOPE_PROVIDED,
            },
            'ACCOUNT_SUSPENDED': {
                "reason": "billing overdue",
                "contactSupport": self.support_email
            },
            'JOB_NOT_FOUND': {
                # L5: date-stamped placeholder — same format as tracking IDs, no drift risk
                "jobId": f"JOB-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{''.join(random.choices('0123456789ABCDEF', k=4))}"
            },
            'RESOURCE_NOT_FOUND': {
                "resourceType": "document",
                # L5: date-stamped placeholder — same format as tracking IDs, no drift risk
                "resourceId": f"DOC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{''.join(random.choices('0123456789ABCDEF', k=4))}"
            },
            'INVALID_ENUM_VALUE': {
                "field": field_names.get('documentField', 'documentClass'),  # F2: DD rule is documentClass
                "value": "invalid_value",
                # Derived from EBNF documentClass enum; fallback matches actual DD values.
                "allowedValues": self._get_enum_values('documentClass') or _ERROR_DOCUMENT_CLASS_FALLBACK
            },
            'MUTUAL_EXCLUSION_VIOLATION': {
                "fields": self.mutual_exclusion_fields,  # H1: from @mutual_exclusion in EBNF DD
                "issue": "only one may be provided"
            },
            'INVALID_FORMAT': {
                "errors": [
                    {
                        "field": field_names.get('documentField', 'documentId'),
                        "issue": "not found in document library"
                    },
                    {
                        "field": f"{field_names.get('addressField', 'recipientAddress')}.{_ERROR_POSTAL_FIELD}",
                        "issue": "invalid format - must be 5 or 9 digits"
                    }
                ]
            },
            'SERVER_ERROR': {
                "message": "An unexpected error occurred"
            },
            'DATABASE_ERROR': {
                "operation": "insert",
                "table": _ERROR_DB_TABLE,
            },
            'EXTERNAL_SERVICE_ERROR': {
                "service": _ERROR_EXTERNAL_SERVICE,
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
                        # Single-field wrapper rules (e.g. documentIdSource = documentId)
                        # must be emitted as { type: object, properties: { b: T } } so
                        # they are structurally distinguishable from sibling oneOf variants.
                        if context in self._single_field_wrapper_rules:
                            return {
                                "type": "object",
                                "properties": {
                                    symbol_name: self._get_field_type(symbol_name)
                                },
                                "required": [symbol_name],
                            }
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
        """Generate oneOf schema from alternation choices.

        For rules in _NAMED_WRAPPER_ONEOF_RULES each named-schema variant is wrapped in
        its type name: { type: object, properties: { variantName: $ref }, required: [...] }.
        For transparent groupings appearing as choices, their own variants are inlined.
        All other rules use the legacy $ref behaviour.
        """
        schemas = []

        for choice in choices:
            if not isinstance(choice, dict):
                continue
            choice_type = choice.get('type')

            if choice_type == 'symbol':
                symbol_name = choice.get('name')
                if not symbol_name:
                    continue

                if symbol_name in self._transparent_oneof_groupings:
                    # Inline this grouping's own variants into the parent oneOf
                    schemas.extend(self._expand_transparent_grouping(symbol_name))
                elif context in self._named_wrapper_oneof_rules:
                    # Wrap the variant in its type name
                    schemas.append({
                        "type": "object",
                        "properties": {
                            symbol_name: {"$ref": f"#/components/schemas/{symbol_name}"}
                        },
                        "required": [symbol_name],
                    })
                else:
                    schemas.append({"$ref": f"#/components/schemas/{symbol_name}"})

            elif choice_type == 'concatenation':
                schemas.append(self._expression_to_schema(choice, context))

            elif choice_type == 'group':
                schemas.append(self._expression_to_schema(choice.get('expression'), context))

        if len(schemas) == 1:
            return schemas[0]
        return {"oneOf": schemas}

    def _expand_transparent_grouping(self, symbol_name: str) -> List[Dict[str, Any]]:
        """Return named-wrapper schemas for each choice inside a transparent grouping rule."""
        prod = self.productions.get(symbol_name)
        if not (prod and hasattr(prod, 'expression')):
            return [{"$ref": f"#/components/schemas/{symbol_name}"}]
        expr = prod.expression
        if not (isinstance(expr, dict) and expr.get('type') == 'alternation'):
            return [{"$ref": f"#/components/schemas/{symbol_name}"}]
        result = []
        for sub_choice in expr.get('choices', []):
            if isinstance(sub_choice, dict) and sub_choice.get('type') == 'symbol':
                sub_name = sub_choice.get('name')
                if sub_name:
                    result.append({
                        "type": "object",
                        "properties": {
                            sub_name: {"$ref": f"#/components/schemas/{sub_name}"}
                        },
                        "required": [sub_name],
                    })
        return result
    
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
                    ("example", _JWT_EXAMPLE_TOKEN)
                ]))
            ])),
            ("Content-Type", OrderedDict([
                ("name", "Content-Type"),
                ("in", "header"),
                ("required", True),
                ("schema", OrderedDict([
                    ("type", "string"),
                    ("example", _CONTENT_TYPE_JSON)
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

# ─────────────────────── Faker Hints Extraction ──────────────────────

def extract_faker_hints(ebnf_content: str) -> dict:
    """Extract @hint annotations from EBNF leaf rules.

    Supported annotation formats (inside (* *) comments on the same line):
      ruleName = string  ; (* @hint faker  first_name *)
      ruleName = integer ; (* @hint static 123 *)
      ruleName = id      ; (* @hint random_int 10000 99999 *)
      ruleName = string  ; (* @hint aba_routing_number *)

    Returns a dict in the same format as the faker_hints section of
    getting-started-template.yaml so the Getting Started generator can
    consume it directly.
    """
    hints = {}
    # Matches any single-line rule (terminals like "= string ;" and enums like "= "a" | "b" ;")
    # that has an inline (* @hint type args *) annotation. The [^;\n]* ensures we stay on one
    # line before the semicolon, and [^(\n]* prevents crossing a newline before the comment.
    pattern = re.compile(
        r'^([a-zA-Z][a-zA-Z0-9_]*)\s*=[^;\n]*;[^(\n]*\(\*\s*@hint\s+(\w+)\s+(.*?)\s*\*\)',
        re.MULTILINE,
    )
    for m in pattern.finditer(ebnf_content):
        rule_name = m.group(1)
        hint_type = m.group(2)   # faker | static | random_int
        hint_args = m.group(3).strip()

        if hint_type == 'faker':
            hints[rule_name] = {'type': 'faker', 'method': hint_args}
        elif hint_type == 'static':
            value: Any = hint_args
            # Quoted values ("...") are always kept as strings, preventing numeric coercion
            # for string-typed fields that happen to contain digit-only values (cardNumber etc.)
            if len(hint_args) >= 2 and hint_args[0] == '"' and hint_args[-1] == '"':
                value = hint_args[1:-1]
            else:
                # Try numeric coercion so YAML output looks correct (no quotes on numbers)
                try:
                    value = int(hint_args)
                except ValueError:
                    try:
                        value = float(hint_args)
                    except ValueError:
                        pass  # keep as string
            hints[rule_name] = {'type': 'static', 'value': value}
        elif hint_type == 'random_int':
            parts = hint_args.split()
            if len(parts) == 2:
                try:
                    hints[rule_name] = {'type': 'random_int', 'min': int(parts[0]), 'max': int(parts[1])}
                except ValueError:
                    pass  # malformed annotation — silently skip
        elif hint_type == 'aba_routing_number':
            hints[rule_name] = {'type': 'aba_routing_number'}
    return hints


# ──────────────────── Provider Mappings Generator ────────────────────

def extract_provider_mappings(openapi_spec: dict, aliases_path: str | None = None) -> dict:
    """Build provider mappings dict from DD-derived enums + optional static aliases file.

    Canonical values (key == value, e.g. first_class: "first_class") are derived at
    runtime from the generated OpenAPI spec components.schemas so they always match the
    EBNF DD.  Only the _aliases blocks — legacy / display strings that map to canonical
    values — are read from the manually maintained aliases file.

    H2: The field list is derived at runtime from jobOptions.properties — any field that
    has an enum in the spec is a provider-mapping field. No hardcoded list needed.

    Args:
        openapi_spec: The fully generated OpenAPI spec dict (post-generate_openapi()).
        aliases_path: Optional path to config/c2m_provider_aliases.yaml.  When provided,
                      each field's _aliases block is merged into the output.
    """
    schemas = (openapi_spec.get('components') or {}).get('schemas') or {}

    # H2: Derive field list from spec — jobOptions enum properties only
    joboptions_props = schemas.get('jobOptions', {}).get('properties', {})
    provider_mapping_fields = [f for f, s in joboptions_props.items() if s.get('enum')]

    aliases: dict = {}
    if aliases_path:
        try:
            with open(aliases_path) as f:
                raw = yaml.safe_load(f) or {}
            for field, block in raw.items():
                if isinstance(block, dict) and '_aliases' in block:
                    aliases[field] = block['_aliases']
        except Exception as e:
            print(f"Warning: could not read provider aliases from {aliases_path}: {e}", file=sys.stderr)

    mappings: dict = {}
    for field in provider_mapping_fields:
        schema = schemas.get(field, {})
        enum_values: list = schema.get('enum', [])
        if not enum_values:
            continue
        field_block: dict = {v: v for v in enum_values}   # canonical == provider value
        if field in aliases:
            field_block['_aliases'] = aliases[field]
        mappings[field] = field_block

    return mappings


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
    parser.add_argument("--faker-hints-output",
                        help="Write @hint annotations extracted from the EBNF DD to this YAML file "
                             "(e.g. config/faker_hints.yaml). Consumed by the Getting Started generator.")
    parser.add_argument("--provider-mappings-output",
                        help="Write the generated provider mappings (canonical enum values from DD + "
                             "static aliases) to this YAML file (e.g. config/c2m_provider_mappings.yaml). "
                             "DO NOT EDIT the output — edit config/c2m_provider_aliases.yaml instead.")
    parser.add_argument("--provider-aliases",
                        help="Path to the manually maintained aliases file merged into the generated "
                             "provider mappings (e.g. config/c2m_provider_aliases.yaml).")

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
    
    # Emit derived faker_hints.yaml if requested
    if args.faker_hints_output:
        hints = extract_faker_hints(ebnf_content)
        hints_doc = {'faker_hints': hints}
        try:
            with open(args.faker_hints_output, 'w') as f:
                f.write("# Generated by ebnf_to_openapi_dynamic_v3.py from @hint annotations in the DD.\n")
                f.write("# DO NOT EDIT — update the @hint annotation in the EBNF Data Dictionary instead.\n")
                yaml.dump(hints_doc, f, default_flow_style=False, sort_keys=True, width=120)
            print(f"Faker hints ({len(hints)} rules) written to: {args.faker_hints_output}")
        except Exception as e:
            print(f"Error writing faker hints file: {e}", file=sys.stderr)
            sys.exit(1)

    # Emit derived c2m_provider_mappings.yaml if requested.
    # Canonical values come from the generated spec (single source = EBNF DD).
    # _aliases blocks come from the manually maintained provider aliases file.
    if args.provider_mappings_output:
        mappings = extract_provider_mappings(openapi_spec, args.provider_aliases)
        try:
            with open(args.provider_mappings_output, 'w') as f:
                f.write("# Generated by ebnf_to_openapi_dynamic_v3.py — DO NOT EDIT.\n")
                f.write("# Canonical values are derived from the EBNF Data Dictionary (c2mapiv2-dd.ebnf).\n")
                f.write("# To add/change aliases, edit config/c2m_provider_aliases.yaml and re-run make openapi-build.\n")
                f.write("#\n")
                f.write("# Format:\n")
                f.write("#   field:\n")
                f.write("#     canonical_value: provider_literal  # canonical == provider for this API\n")
                f.write("#     _aliases:\n")
                f.write("#       legacy_string: canonical_value   # from c2m_provider_aliases.yaml\n")
                yaml.dump(mappings, f, default_flow_style=False, sort_keys=False, width=120)
            field_count = len(mappings)
            value_count = sum(
                len([k for k in v if not k.startswith('_')]) for v in mappings.values()
            )
            print(f"Provider mappings ({field_count} fields, {value_count} canonical values) "
                  f"written to: {args.provider_mappings_output}")
        except Exception as e:
            print(f"Error writing provider mappings file: {e}", file=sys.stderr)
            sys.exit(1)

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