#!/usr/bin/env python3
"""
Getting Started Collection with Real Examples Generator
========================================================
Generates a Postman collection with realistic test data instead of placeholders.

This script:
1. Reads pattern definitions from YAML configuration file
2. Generates realistic test data based on pattern filters
3. Creates a collection with actual example values for onboarding

Usage:
    python3 generate_getting_started_with_examples.py [--config CONFIG_FILE]

Arguments:
    --config: Path to YAML configuration file (default: config/getting-started-patterns.yaml)
    --output: Output file path (default: postman/generated/c2mapiv2-getting-started-with-examples-collection.json)

Output:
    Postman collection with realistic test data for each pattern
"""

import json
import yaml
import argparse
import random
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================

# Realistic test data for common fields
TEST_DATA = {
    "documentSourceIdentifier": {
        "requestId": lambda: random.randint(10000, 99999),
        "documentId": lambda: random.randint(1000, 9999),
        "url": lambda: f"https://api.example.com/documents/{random.randint(1000, 9999)}.pdf",
        "documentsToMerge": lambda: [
            {"requestId": random.randint(10000, 99999)},
            {"documentId": random.randint(1000, 9999)},
            {"documentId": random.randint(1000, 9999)}
        ]
    },

    "recipientAddressSource": {
        "singleAddress": lambda: {
            "firstName": random.choice(["John", "Sarah", "Michael", "Emily", "David"]),
            "lastName": random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones"]),
            "address1": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Cedar', 'Park'])} {random.choice(['St', 'Ave', 'Blvd', 'Ln', 'Dr'])}",
            "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
            "state": random.choice(["NY", "CA", "IL", "TX", "AZ"]),
            "zip": f"{random.randint(10000, 99999)}"
        },
        "addressList": lambda: [
            {
                "firstName": "Alice",
                "lastName": "Anderson",
                "address1": "123 Business Ave",
                "city": "Boston",
                "state": "MA",
                "zip": "02101",
                "foo1": "Marketing Campaign Q1",
                "foo2": "Priority Customer"
            },
            {
                "firstName": "Bob",
                "lastName": "Baker",
                "address1": "456 Commerce Blvd",
                "city": "Seattle",
                "state": "WA",
                "zip": "98101",
                "foo1": "Marketing Campaign Q1",
                "foo2": "Standard Customer"
            }
        ],
        "addressListId": lambda: random.randint(1000, 9999),
        "addressListName": lambda: {
            "addressListName": f"campaign_{random.choice(['q1', 'q2', 'monthly', 'annual'])}_{random.randint(2024, 2025)}",
            "mappingId": random.randint(100, 999),
            "addressList": [
                {
                    "firstName": "Carol",
                    "lastName": "Clark",
                    "address1": "789 Market St",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                    "foo1": "Newsletter Subscriber",
                    "foo2": "Active"
                }
            ]
        }
    },

    "paymentDetails": {
        "creditCard": lambda: {
            "creditCard": {
                "cardNumber": "4111111111111111",
                "cardType": "visa",
                "cvv": "123",
                "expirationMonth": str(random.randint(1, 12)),
                "expirationYear": str(random.randint(2025, 2028))
            }
        },
        "ach": lambda: {
            "ach": {
                "accountNumber": "123456789",
                "routingNumber": "021000021",
                "accountType": "checking"
            }
        },
        "invoice": lambda: {
            "invoice": {
                "invoiceNumber": f"INV-{random.randint(2024, 2025)}-{random.randint(1000, 9999)}",
                "poNumber": f"PO-{random.randint(10000, 99999)}"
            }
        }
    },

    "jobTemplate": {
        "template": lambda: random.choice([
            "legal_certified_mail",
            "real_estate_postcard",
            "medical_correspondence",
            "monthly_newsletter",
            "invoice_first_class"
        ])
    }
}


# =============================================================================
# YAML CONFIGURATION LOADING
# =============================================================================

def load_patterns_from_yaml(config_path: str) -> List[Dict[str, Any]]:
    """
    Load pattern definitions from YAML configuration file.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        List of pattern dictionaries

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file has invalid YAML
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    print(f"Loading patterns from {config_path}...")

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    patterns = config.get('patterns', [])

    if not patterns:
        raise ValueError(f"No patterns found in {config_path}")

    print(f"   Loaded {len(patterns)} patterns")

    return patterns


def group_patterns_by_category(patterns: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group patterns by their category field.

    Args:
        patterns: List of pattern dictionaries

    Returns:
        Dictionary mapping category name to list of patterns
    """
    grouped = defaultdict(list)

    for pattern in patterns:
        category = pattern.get('category', 'Uncategorized')
        grouped[category].append(pattern)

    return dict(grouped)


# =============================================================================
# TEST DATA GENERATION
# =============================================================================

def generate_realistic_value(field_name: str, field_type: str, pattern_filters: Dict[str, Any]) -> Any:
    """
    Generate realistic test data for a specific field based on pattern filters.

    Args:
        field_name: Name of the field
        field_type: Type of data needed (from pattern filters)
        pattern_filters: Filter criteria from pattern configuration

    Returns:
        Realistic test data value
    """
    # Handle documentSource field
    if field_name == "documentSource":
        doc_type = pattern_filters.get("documentSourceIdentifier", "requestId")
        if doc_type in TEST_DATA["documentSourceIdentifier"]:
            generator = TEST_DATA["documentSourceIdentifier"][doc_type]
            if doc_type == "documentsToMerge":
                return {"documentsToMerge": generator()}
            else:
                return {doc_type: generator()}
        return {"requestId": TEST_DATA["documentSourceIdentifier"]["requestId"]()}

    # Handle recipientAddressSource field
    elif field_name == "recipientAddressSource":
        addr_type = pattern_filters.get("recipientAddressSource", "singleAddress")
        if addr_type in TEST_DATA["recipientAddressSource"]:
            generator = TEST_DATA["recipientAddressSource"][addr_type]
            if addr_type == "addressListId":
                return {"addressListId": generator()}
            elif addr_type == "addressListName":
                return generator()
            elif addr_type == "addressList":
                return {"addressList": generator()}
            else:  # singleAddress
                return {"singleAddress": generator()}
        return {"singleAddress": TEST_DATA["recipientAddressSource"]["singleAddress"]()}

    # Handle paymentDetails field
    elif field_name == "paymentDetails":
        payment_type = pattern_filters.get("paymentDetails", "any")
        if payment_type == "any":
            # Skip payment details if filter is "any"
            return None
        elif payment_type in TEST_DATA["paymentDetails"]:
            return TEST_DATA["paymentDetails"][payment_type]()
        return None

    # Handle jobTemplate
    elif field_name == "jobTemplate":
        has_template = pattern_filters.get("has_jobTemplate", True)
        if has_template:
            return TEST_DATA["jobTemplate"]["template"]()
        return None

    # Handle tags
    elif field_name == "tags":
        return [
            "customer_segment_enterprise",
            f"campaign_{random.choice(['q1_2024', 'q2_2024', 'annual_2024'])}",
            random.choice(["priority_high", "priority_medium", "priority_low"])
        ]

    # Handle job-specific fields for bulk operations
    elif field_name == "jobs":
        # For split PDF operations
        return [
            {
                "pages": {
                    "startPage": 1,
                    "endPage": 5
                }
            },
            {
                "pages": {
                    "startPage": 6,
                    "endPage": 10
                }
            }
        ]

    # Default: return None if no specific generator
    return None


def populate_body_with_realistic_data(body_template: Dict[str, Any], pattern_filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Replace placeholders in body template with realistic test data.

    Args:
        body_template: Request body template with placeholders
        pattern_filters: Filter criteria from pattern configuration

    Returns:
        Body populated with realistic test data
    """
    result = {}

    for key, value in body_template.items():
        # Generate realistic value based on field name and filters
        realistic_value = generate_realistic_value(key, str(type(value)), pattern_filters)

        if realistic_value is not None:
            result[key] = realistic_value
        elif isinstance(value, dict):
            # Recursively process nested objects
            result[key] = populate_body_with_realistic_data(value, pattern_filters)
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            # Handle arrays of objects
            if key == "jobs":
                result[key] = generate_realistic_value(key, "array", pattern_filters)
            else:
                result[key] = [populate_body_with_realistic_data(item, pattern_filters) for item in value]
        elif isinstance(value, str) and value.startswith("<"):
            # Replace placeholder strings with realistic values
            if value == "<string>":
                result[key] = f"example_{key}_{random.randint(100, 999)}"
            elif value == "<integer>":
                result[key] = random.randint(1000, 9999)
            else:
                result[key] = value
        else:
            result[key] = value

    return result


# =============================================================================
# COLLECTION GENERATION
# =============================================================================

def create_request_item_with_examples(pattern: Dict[str, Any], base_url: str = "{{baseUrl}}") -> Dict[str, Any]:
    """
    Create a Postman request item with realistic test data.

    Args:
        pattern: Pattern definition containing name, description, endpoint, body_template, filters
        base_url: Base URL for the API (default: {{baseUrl}} variable)

    Returns:
        Postman request item dictionary with realistic examples
    """
    # Get filters from pattern
    filters = pattern.get("filters", {})

    # Populate body template with realistic data
    realistic_body = populate_body_with_realistic_data(pattern["body_template"], filters)

    return {
        "name": pattern["name"],
        "request": {
            "method": "POST",
            "header": [],
            "body": {
                "mode": "raw",
                "raw": json.dumps(realistic_body, indent=2),
                "options": {
                    "raw": {
                        "language": "json"
                    }
                }
            },
            "url": {
                "raw": f"{base_url}{pattern['endpoint']}",
                "host": base_url.split("://")[-1].split("/")[0] if "://" in base_url else base_url,
                "path": pattern['endpoint'].strip('/').split('/')
            },
            "description": pattern["description"]
        },
        "response": []
    }


def generate_getting_started_with_examples(patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate the complete Getting Started collection with realistic examples.

    Args:
        patterns: List of pattern dictionaries loaded from YAML

    Returns:
        Complete Postman collection dictionary with realistic test data
    """
    collection = {
        "info": {
            "name": "C2M API v2 - Getting Started - With Examples",
            "description": "Educational collection showing common API usage patterns with realistic test data.\n\n"
                          "**Categories:**\n"
                          "- **Most Frequently Used**: Essential calls every user needs\n"
                          "- **Bulk Operations**: High-volume and batch processing\n"
                          "- **Advanced Patterns**: Less common features and variations\n\n"
                          "**How to use:**\n"
                          "1. Set your `{{baseUrl}}` environment variable\n"
                          "2. Review the realistic example data in each request\n"
                          "3. Test the request as-is or modify values to match your needs\n"
                          "4. Copy the pattern and adapt it to your use case\n\n"
                          "**Note**: This collection contains realistic example values instead of placeholders. "
                          "All data is fictitious and safe for testing.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    # Group patterns by category
    grouped_patterns = group_patterns_by_category(patterns)

    # Category descriptions
    category_descriptions = {
        "Most Frequently Used": "The essential API calls that most users need. Start here if you're new to the API. Each example shows realistic data you can test with.",
        "Bulk Operations": "High-volume processing patterns for handling multiple documents or recipients efficiently. Examples show how to batch process documents.",
        "Advanced Patterns": "Less frequently used features and variations. Explore these once you're comfortable with the basics. Examples demonstrate edge cases and special features."
    }

    # Define category order (categories not in this list will be appended in alphabetical order)
    category_order = ["Most Frequently Used", "Bulk Operations", "Advanced Patterns"]

    # Add categories in order
    for category_name in category_order:
        if category_name in grouped_patterns:
            folder = {
                "name": category_name,
                "description": category_descriptions.get(category_name, ""),
                "item": [create_request_item_with_examples(pattern) for pattern in grouped_patterns[category_name]]
            }
            collection["item"].append(folder)

    # Add any remaining categories not in the order list
    for category_name in sorted(grouped_patterns.keys()):
        if category_name not in category_order:
            folder = {
                "name": category_name,
                "description": category_descriptions.get(category_name, ""),
                "item": [create_request_item_with_examples(pattern) for pattern in grouped_patterns[category_name]]
            }
            collection["item"].append(folder)

    return collection


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate Getting Started collection with realistic examples")
    parser.add_argument('--config', default='config/getting-started-patterns.yaml',
                        help='Path to YAML configuration file (default: config/getting-started-patterns.yaml)')
    parser.add_argument('--output', default='postman/generated/c2mapiv2-getting-started-with-examples-collection.json',
                        help='Output file path (default: postman/generated/c2mapiv2-getting-started-with-examples-collection.json)')

    args = parser.parse_args()

    print("Generating Getting Started collection with realistic examples...")
    print()

    try:
        # Load patterns from YAML
        patterns = load_patterns_from_yaml(args.config)

        # Generate the collection with realistic examples
        collection = generate_getting_started_with_examples(patterns)

        # Count items for summary
        total_patterns = sum(len(folder["item"]) for folder in collection["item"])

        # Save to file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(collection, f, indent=2)

        print()
        print(f"Successfully generated Getting Started collection with examples!")
        print(f"   Config: {args.config}")
        print(f"   Output: {output_path}")
        print(f"   Categories: {len(collection['item'])}")
        print(f"   Total patterns: {total_patterns}")
        print()
        print("Category breakdown:")
        for folder in collection["item"]:
            print(f"   - {folder['name']}: {len(folder['item'])} patterns")
        print()
        print("Next steps:")
        print("1. Upload to Postman workspace")
        print("2. Set {{baseUrl}} environment variable")
        print("3. Test requests with realistic example data")
        print("4. Share with new API users for hands-on learning")

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in configuration file: {e}")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
