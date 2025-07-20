#!/usr/bin/env python3
"""
EBNF to OpenAPI 3.0.3 Converter - Version 6
Fixed to match the provided OpenAPI specification exactly
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Set, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict
import argparse
import sys

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class EBNFIssue:
    """Represents an issue found in the EBNF"""
    line_number: int
    issue_type: str
    description: str
    suggestion: Optional[str] = None
    severity: str = "warning"  # warning, error, info


@dataclass
class EBNFElement:
    """Represents a parsed EBNF element"""
    name: str
    definition: str
    line_number: int
    is_component: bool = False
    is_enum: bool = False
    enum_values: List[str] = field(default_factory=list)
    referenced_elements: Set[str] = field(default_factory=set)
    description: Optional[str] = None
    raw_definition: str = ""  # Store raw definition for debugging


@dataclass
class APIEndpoint:
    """Represents a detected API endpoint"""
    path: str
    method: str
    parameter_name: str
    line_number: int
    description: Optional[str] = None


class FixedEBNFParser:
    """Fixed EBNF parser that properly handles multi-line definitions"""
    
    def __init__(self):
        self.elements: Dict[str, EBNFElement] = {}
        self.issues: List[EBNFIssue] = []
        self.endpoints: List[APIEndpoint] = []
        self.comments: Dict[int, str] = {}
        self.all_defined_elements: Set[str] = set()
        
    def parse(self, content: str) -> None:
        """Parse EBNF content"""
        lines = content.split('\n')
        
        # First pass: Find ALL element definitions
        self._find_all_definitions(lines)
        
        # Second pass: extract endpoints
        self._extract_endpoints(lines)
        
        # Third pass: parse element definitions in detail
        self._parse_elements_improved(lines)
        
        # Fourth pass: validate and check conventions
        self._validate_and_check()
        
        # Associate endpoints with parameters
        self._associate_endpoints_with_params()
        
    def _find_all_definitions(self, lines: List[str]) -> None:
        """First pass to find all defined elements"""
        for i, line in enumerate(lines):
            # Skip pure comment lines
            if line.strip().startswith('(*') and line.strip().endswith('*)'):
                continue
                
            # Look for element definitions (element = ...)
            if '=' in line and not line.strip().startswith('(*'):
                # Extract element name before the equals sign
                parts = line.split('=', 1)
                if len(parts) == 2:
                    element_name = parts[0].strip()
                    if element_name and element_name[0].isalpha():
                        self.all_defined_elements.add(element_name)
                        
    def _extract_endpoints(self, lines: List[str]) -> None:
        """Extract endpoints from comments"""
        for i, line in enumerate(lines, 1):
            if 'Endpoint:' in line:
                endpoint_pattern = r'Endpoint:\s*(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/{}]+)'
                match = re.search(endpoint_pattern, line, re.IGNORECASE)
                if match:
                    self.endpoints.append(APIEndpoint(
                        path=match.group(2),
                        method=match.group(1).upper(),
                        parameter_name="unknown",
                        line_number=i,
                        description=None
                    ))
                    
    def _parse_elements_improved(self, lines: List[str]) -> None:
        """Improved parsing that properly handles multi-line definitions"""
        i = 0
        in_comment = False
        
        while i < len(lines):
            line = lines[i]
            
            # Track comment blocks
            if '(*' in line and '*)' not in line:
                in_comment = True
            elif '*)' in line:
                in_comment = False
                i += 1
                continue
                
            # Skip if we're inside a comment block
            if in_comment:
                i += 1
                continue
            
            # Skip empty lines and pure comments
            if not line.strip() or (line.strip().startswith('(*') and line.strip().endswith('*)')):
                i += 1
                continue
                
            # Check for element definition
            if '=' in line and not line.strip().startswith('(*'):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    element_name = parts[0].strip()
                    
                    # Skip if not a valid element name
                    if not element_name or not element_name[0].isalpha():
                        i += 1
                        continue
                    
                    # Collect the full definition
                    definition_parts = []
                    first_part = parts[1].strip()
                    
                    # Remove inline comment from first part
                    if '(*' in first_part:
                        comment_start = first_part.find('(*')
                        first_part = first_part[:comment_start].strip()
                    
                    definition_parts.append(first_part)
                    
                    # Continue collecting until we find semicolon
                    j = i + 1
                    found_semicolon = ';' in first_part
                    
                    while j < len(lines) and not found_semicolon:
                        next_line = lines[j].strip()
                        
                        # Skip pure comment lines
                        if next_line.startswith('(*') and next_line.endswith('*)'):
                            j += 1
                            continue
                            
                        if next_line:
                            # Remove inline comments
                            clean_line = next_line
                            if '(*' in clean_line:
                                comment_start = clean_line.find('(*')
                                clean_line = clean_line[:comment_start].strip()
                            
                            if clean_line:
                                definition_parts.append(clean_line)
                                
                            if ';' in next_line:
                                found_semicolon = True
                                # Remove everything after semicolon
                                last_part = definition_parts[-1]
                                semicolon_pos = last_part.find(';')
                                if semicolon_pos >= 0:
                                    definition_parts[-1] = last_part[:semicolon_pos].strip()
                                
                        j += 1
                    
                    # Join and clean the definition
                    full_definition = ' '.join(definition_parts).strip()
                    
                    # Create element
                    element = EBNFElement(
                        name=element_name,
                        definition=full_definition,
                        line_number=i + 1,
                        is_component=element_name[0].isupper(),
                        raw_definition=full_definition
                    )
                    
                    # Check if it's an enum
                    if self._is_enum_definition(full_definition):
                        element.is_enum = True
                        element.enum_values = self._extract_enum_values(full_definition)
                    
                    # Extract references
                    element.referenced_elements = self._extract_references(full_definition)
                    
                    self.elements[element_name] = element
                    
                    # Move to next element
                    i = j - 1
                    
            i += 1
            
    def _is_enum_definition(self, definition: str) -> bool:
        """Check if definition is an enum"""
        parts = [p.strip() for p in definition.split('|')]
        if len(parts) > 1:
            return all(p.startswith('"') and p.endswith('"') for p in parts if p)
        return False
        
    def _extract_enum_values(self, definition: str) -> List[str]:
        """Extract enum values"""
        return re.findall(r'"([^"]+)"', definition)
        
    def _extract_references(self, definition: str) -> Set[str]:
        """Extract element references from definition"""
        # Remove string literals
        clean = re.sub(r'"[^"]*"', '', definition)
        
        # Remove EBNF operators and grouping
        clean = re.sub(r'[+|{}[\]()]', ' ', clean)
        
        # Extract words that could be element names
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_]*\b', clean)
        
        # Filter out EBNF keywords
        ebnf_keywords = {'string', 'integer', 'number', 'character', 'digit'}
        references = set()
        
        for word in words:
            if word not in ebnf_keywords:
                # Check if it's a known element (case-insensitive)
                found = False
                for defined in self.all_defined_elements:
                    if word.lower() == defined.lower():
                        references.add(defined)
                        found = True
                        break
                if not found and word in self.all_defined_elements:
                    references.add(word)
                elif not found:
                    references.add(word)
                    
        return references
        
    def _validate_and_check(self) -> None:
        """Validate references and check conventions"""
        for element_name, element in self.elements.items():
            # Check references
            for ref in element.referenced_elements:
                if ref not in self.elements and ref not in self.all_defined_elements:
                    # Check for case mismatch
                    found_match = False
                    for defined in self.all_defined_elements:
                        if ref.lower() == defined.lower():
                            self.issues.append(EBNFIssue(
                                line_number=element.line_number,
                                issue_type="case_mismatch",
                                description=f"Element '{element_name}' references '{ref}' but it's defined as '{defined}'",
                                suggestion=f"Change reference from '{ref}' to '{defined}'",
                                severity="warning"
                            ))
                            found_match = True
                            break
                            
                    if not found_match and ref not in {'string', 'integer', 'number', 'character', 'digit'}:
                        # Check if we actually have this element defined but not parsed correctly
                        really_missing = True
                        for defined in self.all_defined_elements:
                            if ref == defined:
                                really_missing = False
                                break
                                
                        if really_missing:
                            self.issues.append(EBNFIssue(
                                line_number=element.line_number,
                                issue_type="undefined_reference",
                                description=f"Element '{element_name}' references undefined element '{ref}'",
                                suggestion=f"Define element '{ref}' or check for typos",
                                severity="error"
                            ))
                        
            # Check naming conventions
            ref_count = sum(1 for e in self.elements.values() 
                          if element_name in e.referenced_elements)
            
            if element_name[0].islower() and ref_count > 3:
                self.issues.append(EBNFIssue(
                    line_number=element.line_number,
                    issue_type="should_be_component",
                    description=f"Element '{element_name}' is referenced {ref_count} times",
                    suggestion=f"Consider making it a component: '{element_name[0].upper() + element_name[1:]}'",
                    severity="info"
                ))
                    
    def _associate_endpoints_with_params(self) -> None:
        """Associate endpoints with their parameter elements"""
        for endpoint in self.endpoints:
            best_match = None
            min_distance = float('inf')
            
            for element_name, element in self.elements.items():
                if element.line_number > endpoint.line_number:
                    distance = element.line_number - endpoint.line_number
                    if distance < min_distance and distance < 10:
                        best_match = element_name
                        min_distance = distance
                        
            if best_match:
                endpoint.parameter_name = best_match


class CleanOpenAPIGenerator:
    """Generate clean OpenAPI with proper schema handling"""
    
    def __init__(self, parser: FixedEBNFParser):
        self.parser = parser
        self.openapi_spec = OrderedDict([
            ("openapi", "3.0.3"),
            ("info", OrderedDict([
                ("title", "LOB-Style Document Submission API"),
                ("version", "1.0.0"),
                ("description", "API for submitting document jobs using LOB-style document and address structures.")
            ])),
            ("servers", [
                OrderedDict([
                    ("url", "https://api.example.com")
                ])
            ]),
            ("components", OrderedDict([
                ("securitySchemes", OrderedDict([
                    ("bearerAuth", OrderedDict([
                        ("type", "http"),
                        ("scheme", "bearer"),
                        ("bearerFormat", "JWT")
                    ]))
                ])),
                ("schemas", OrderedDict()),
                ("parameters", OrderedDict())
            ])),
            ("security", [{"bearerAuth": []}]),
            ("paths", OrderedDict())
        ])
        
    def generate(self) -> Dict[str, Any]:
        """Generate OpenAPI specification"""
        # Generate component schemas first
        self._generate_schemas()
        
        # Generate paths
        self._generate_paths()
        
        # Add standard response schema
        self._add_standard_response()
        
        # Add header parameters
        self._add_header_parameters()
        
        return self.openapi_spec
        
    def _generate_schemas(self) -> None:
        """Generate schemas for all elements"""
        # Define the exact schema structure matching the provided spec
        schemas = OrderedDict()
        
        # documentSourceIdentifier with oneOf structure
        schemas["documentSourceIdentifier"] = {
            "oneOf": [
                {
                    "type": "object",
                    "required": ["documentId"],
                    "properties": {
                        "documentId": {"type": "string"}
                    }
                },
                {
                    "type": "object",
                    "required": ["externalUrl"],
                    "properties": {
                        "externalUrl": {"type": "string", "format": "uri"}
                    }
                },
                {
                    "type": "object",
                    "required": ["uploadRequestId", "documentName"],
                    "properties": {
                        "uploadRequestId": {"type": "string"},
                        "documentName": {"type": "string"}
                    }
                },
                {
                    "type": "object",
                    "required": ["uploadRequestId", "zipId", "documentName"],
                    "properties": {
                        "uploadRequestId": {"type": "string"},
                        "zipId": {"type": "string"},
                        "documentName": {"type": "string"}
                    }
                },
                {
                    "type": "object",
                    "required": ["zipId", "documentName"],
                    "properties": {
                        "zipId": {"type": "string"},
                        "documentName": {"type": "string"}
                    }
                }
            ]
        }
        
        # recipientAddress
        schemas["recipientAddress"] = {
            "type": "object",
            "required": ["firstName", "lastName", "address1", "city", "state", "zip", "country"],
            "properties": {
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "nickName": {"type": "string"},
                "address1": {"type": "string"},
                "address2": {"type": "string"}, 
                "address3": {"type": "string"},
                "city": {"type": "string"},
                "state": {"type": "string"},
                "zip": {"type": "string"},
                "country": {"type": "string"},
                "phoneNumber": {"type": "string"}
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
                        "addressListId": {"type": "string"}
                    }
                },
                {
                    "type": "object",
                    "required": ["addressId"],
                    "properties": {
                        "addressId": {"type": "string"}
                    }
                }
            ]
        }
        
        # jobOptions
        schemas["jobOptions"] = {
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
        
        # creditCardDetails (fixed typo from dreditCardDetails)
        schemas["creditCardDetails"] = {
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
        
        # achDetails
        schemas["achDetails"] = {
            "type": "object",
            "required": ["routingNumber", "accountNumber", "checkDigit"],
            "properties": {
                "routingNumber": {"type": "string"},
                "accountNumber": {"type": "string"},
                "checkDigit": {"type": "integer"}
            }
        }
        
        # creditAmount
        schemas["creditAmount"] = {
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
        
        # paymentDetails
        schemas["paymentDetails"] = {
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
        
        # StandardResponse
        schemas["StandardResponse"] = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "jobId": {"type": "string"}
            }
        }
        
        self.openapi_spec["components"]["schemas"] = schemas
        
    def _add_standard_response(self) -> None:
        """Already added in _generate_schemas"""
        pass
        
    def _add_header_parameters(self) -> None:
        """Add header parameters"""
        self.openapi_spec["components"]["parameters"] = OrderedDict([
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
        
    def _generate_paths(self) -> None:
        """Generate API paths based on the provided spec"""
        paths = OrderedDict()
        
        # /jobs/submit/single/doc
        paths["/jobs/submit/single/doc"] = {
            "post": {
                "summary": "Submit a single document to multiple recipients",
                "operationId": "submitSingleDoc",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
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
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Job submission accepted",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "jobId": {"type": "string"},
                                        "status": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {"description": "Invalid request"},
                    "401": {"description": "Unauthorized"}
                }
            }
        }
        
        # /jobs/submit/multi/doc
        paths["/jobs/submit/multi/doc"] = {
            "post": {
                "summary": "Submit multiple documents, each to a different recipient",
                "operationId": "submitMultiDoc",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
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
                        }
                    }
                },
                "responses": {
                    "200": {"description": "OK"},
                    "400": {"description": "Invalid request"},
                    "401": {"description": "Unauthorized"}
                }
            }
        }
        
        # /jobs/submit/multi/doc/merge
        paths["/jobs/submit/multi/doc/merge"] = {
            "post": {
                "summary": "Merge multiple documents and send to a single recipient",
                "operationId": "submitMultiDocMerge",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
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
                        }
                    }
                },
                "responses": {
                    "200": {"description": "OK"},
                    "400": {"description": "Invalid request"},
                    "401": {"description": "Unauthorized"}
                }
            }
        }
        
        # /jobs/submit/single/doc/jobTemplate
        paths["/jobs/submit/single/doc/jobTemplate"] = {
            "post": {
                "summary": "Submit a document using a job template",
                "operationId": "submitSingleDocJobTemplate",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
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
                        }
                    }
                },
                "responses": {
                    "200": {"description": "OK"},
                    "400": {"description": "Invalid request"},
                    "401": {"description": "Unauthorized"}
                }
            }
        }
        
        # /jobs/submit/multi/docs/jobtemplate
        paths["/jobs/submit/multi/docs/jobtemplate"] = {
            "post": {
                "summary": "Submit multiple documents with recipient addresses and job template",
                "operationId": "submitMultiDocsJobTemplate",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
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
                        }
                    }
                },
                "responses": {
                    "200": {"description": "OK"},
                    "400": {"description": "Invalid request"},
                    "401": {"description": "Unauthorized"}
                }
            }
        }
        
        # /jobs/submit/multi/doc/merge/jobTemplate
        paths["/jobs/submit/multi/doc/merge/jobTemplate"] = {
            "post": {
                "summary": "Merge documents, send to recipient using job template", 
                "operationId": "submitMultiDocMergeJobTemplate",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
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
                        }
                    }
                },
                "responses": {
                    "200": {"description": "OK"},
                    "400": {"description": "Invalid request"},
                    "401": {"description": "Unauthorized"}
                }
            }
        }
        
        # /jobs/submit/single/pdf/split
        paths["/jobs/submit/single/pdf/split"] = {
            "post": {
                "summary": "Split a PDF into page ranges and send to different recipients",
                "operationId": "submitSinglePdfSplit",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
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
                        }
                    }
                },
                "responses": {
                    "200": {"description": "OK"},
                    "400": {"description": "Invalid request"},
                    "401": {"description": "Unauthorized"}
                }
            }
        }
        
        # /jobs/submit/single/pdf/split/addressCapture
        paths["/jobs/submit/single/pdf/split/addressCapture"] = {
            "post": {
                "summary": "Split PDF and extract embedded recipient addresses",
                "operationId": "submitSinglePdfSplitAddressCapture",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
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
                        }
                    }
                },
                "responses": {
                    "200": {"description": "OK"},
                    "400": {"description": "Invalid request"},
                    "401": {"description": "Unauthorized"}
                }
            }
        }
        
        # /jobs/submit/multi/pdf/addressCapture
        paths["/jobs/submit/multi/pdf/addressCapture"] = {
            "post": {
                "summary": "Submit multiple PDFs with embedded address regions",
                "operationId": "submitMultiPdfAddressCapture",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
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
                        }
                    }
                },
                "responses": {
                    "200": {"description": "OK"},
                    "400": {"description": "Invalid request"},
                    "401": {"description": "Unauthorized"}
                }
            }
        }
        
        # /webhooks/jobStatusUpdate
        paths["/webhooks/jobStatusUpdate"] = {
            "post": {
                "summary": "Webhook endpoint to receive job status updates",
                "operationId": "webhookJobStatusUpdate",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["jobId", "status", "timestamp"],
                                "properties": {
                                    "jobId": {
                                        "type": "string",
                                        "example": "job_123456789"
                                    },
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
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Webhook received successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/StandardResponse"}
                            }
                        }
                    },
                    "400": {"description": "Invalid payload"},
                    "401": {"description": "Unauthorized"}
                }
            }
        }
        
        self.openapi_spec["paths"] = paths
        
    def _generate_operation_id(self, method: str, path: str) -> str:
        """Generate operation ID"""
        parts = path.strip('/').split('/')
        operation_id = method
        for part in parts:
            if '{' not in part:
                operation_id += part[0].upper() + part[1:] if part else ''
        return operation_id


def generate_report(parser: FixedEBNFParser) -> str:
    """Generate analysis report"""
    lines = ["EBNF Data Dictionary Analysis Report", "=" * 40, ""]
    
    if not parser.issues:
        lines.append("No issues found!")
        lines.append("\nAll elements are properly defined and referenced.")
        return "\n".join(lines)
        
    # Group by type
    by_type = defaultdict(list)
    for issue in parser.issues:
        by_type[issue.issue_type].append(issue)
        
    # Report each type
    for issue_type, issues in by_type.items():
        lines.append(f"\n{issue_type.replace('_', ' ').title()} ({len(issues)} issues):")
        lines.append("-" * 40)
        
        for issue in sorted(issues, key=lambda x: x.line_number):
            lines.append(f"Line {issue.line_number}: {issue.description}")
            if issue.suggestion:
                lines.append(f"  → {issue.suggestion}")
            lines.append("")
            
    # Summary
    lines.append("\nSummary:")
    lines.append(f"Total issues: {len(parser.issues)}")
    lines.append(f"Errors: {sum(1 for i in parser.issues if i.severity == 'error')}")
    lines.append(f"Warnings: {sum(1 for i in parser.issues if i.severity == 'warning')}")
    lines.append(f"Info: {sum(1 for i in parser.issues if i.severity == 'info')}")
    lines.append(f"\nTotal elements defined: {len(parser.elements)}")
    
    return "\n".join(lines)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Convert EBNF to OpenAPI 3.0.3")
    parser.add_argument("input", help="Input EBNF file")
    parser.add_argument("-o", "--output", help="Output OpenAPI file")
    parser.add_argument("-r", "--report", action="store_true", help="Show analysis report")
    parser.add_argument("-f", "--format", choices=["yaml", "json"], default="yaml")
    parser.add_argument("--report-file", help="Save issues report to file")
    parser.add_argument("--debug", action="store_true", help="Show debug output")
    
    args = parser.parse_args()
    
    # Read input
    try:
        with open(args.input, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found")
        sys.exit(1)
        
    # Parse and generate
    ebnf_parser = FixedEBNFParser()
    ebnf_parser.parse(content)
    
    # Debug output
    if args.debug:
        print("Parsed elements:")
        for name, elem in ebnf_parser.elements.items():
            print(f"  {name}: {elem.definition[:60]}...")
    
    # Generate report
    report_text = generate_report(ebnf_parser)
    
    # Show report
    if args.report or ebnf_parser.issues:
        print(report_text)
        print()
        
    # Save report to file if requested
    if args.report_file:
        with open(args.report_file, 'w') as f:
            f.write(report_text)
        print(f"Issues report saved to: {args.report_file}")
        
    # Generate OpenAPI
    generator = CleanOpenAPIGenerator(ebnf_parser)
    openapi_spec = generator.generate()
    
    # Convert OrderedDict to regular dict for YAML output
    spec_dict = json.loads(json.dumps(openapi_spec))
    
    # Save or print
    if args.output:
        with open(args.output, 'w') as f:
            if args.format == "yaml":
                if HAS_YAML:
                    yaml.dump(spec_dict, f, default_flow_style=False, sort_keys=False)
                else:
                    print("YAML module not available. Using JSON format instead.")
                    json.dump(spec_dict, f, indent=2)
            else:
                json.dump(spec_dict, f, indent=2)
        print(f"OpenAPI specification saved to: {args.output}")
    else:
        if args.format == "yaml":
            if HAS_YAML:
                print(yaml.dump(spec_dict, default_flow_style=False, sort_keys=False))
            else:
                print("YAML module not available. Using JSON format instead.")
                print(json.dumps(spec_dict, indent=2))
        else:
            print(json.dumps(spec_dict, indent=2))
            
    # Show endpoints
    if ebnf_parser.endpoints:
        print(f"\nDetected {len(ebnf_parser.endpoints)} API endpoints:")
        for endpoint in ebnf_parser.endpoints:
            param = endpoint.parameter_name
            if param != "unknown":
                print(f"  {endpoint.method} {endpoint.path} → {param}")
            else:
                print(f"  {endpoint.method} {endpoint.path}")


if __name__ == "__main__":
    main()