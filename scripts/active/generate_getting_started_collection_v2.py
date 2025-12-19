#!/usr/bin/env python3
"""
Getting Started Collection Generator (Configuration-Driven)
============================================================
Generates a Postman collection organized by usage patterns to onboard new API users.

This script creates an educational collection showing different ways to use the API,
organized by frequency of use and common patterns. Patterns are defined in a YAML
configuration file for easy maintenance and extensibility.

Usage:
    python3 generate_getting_started_collection_v2.py [--config CONFIG_FILE]

Arguments:
    --config: Path to YAML configuration file (default: config/getting-started-patterns.yaml)

Output:
    postman/generated/c2mapiv2-getting-started-collection.json
"""

import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


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

    print(f"📖 Loading patterns from {config_path}...")

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
# COLLECTION GENERATION
# =============================================================================

def create_request_item(pattern: Dict[str, Any], base_url: str = "{{baseUrl}}") -> Dict[str, Any]:
    """
    Create a Postman request item from a pattern definition.

    Args:
        pattern: Pattern definition containing name, description, endpoint, body_template
        base_url: Base URL for the API (default: {{baseUrl}} variable)

    Returns:
        Postman request item dictionary
    """
    return {
        "name": pattern["name"],
        "request": {
            "method": "POST",
            "header": [],
            "body": {
                "mode": "raw",
                "raw": json.dumps(pattern["body_template"], indent=2),
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


def generate_getting_started_collection(patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate the complete Getting Started collection from pattern definitions.

    Args:
        patterns: List of pattern dictionaries loaded from YAML

    Returns:
        Complete Postman collection dictionary
    """
    collection = {
        "info": {
            "name": "C2M API v2 - Getting Started",
            "description": "Educational collection showing common API usage patterns organized by frequency.\n\n"
                          "**Categories:**\n"
                          "- **Most Frequently Used**: Essential calls every user needs\n"
                          "- **Bulk Operations**: High-volume and batch processing\n"
                          "- **Advanced Patterns**: Less common features and variations\n\n"
                          "**How to use:**\n"
                          "1. Set your `{{baseUrl}}` environment variable\n"
                          "2. Replace `<string>` and `<integer>` placeholders with actual values\n"
                          "3. Review the description of each request to understand the pattern\n"
                          "4. Copy the pattern and adapt it to your needs",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    # Group patterns by category
    grouped_patterns = group_patterns_by_category(patterns)

    # Category descriptions
    category_descriptions = {
        "Most Frequently Used": "The essential API calls that most users need. Start here if you're new to the API.",
        "Bulk Operations": "High-volume processing patterns for handling multiple documents or recipients efficiently.",
        "Advanced Patterns": "Less frequently used features and variations. Explore these once you're comfortable with the basics."
    }

    # Define category order (categories not in this list will be appended in alphabetical order)
    category_order = ["Most Frequently Used", "Bulk Operations", "Advanced Patterns"]

    # Add categories in order
    for category_name in category_order:
        if category_name in grouped_patterns:
            folder = {
                "name": category_name,
                "description": category_descriptions.get(category_name, ""),
                "item": [create_request_item(pattern) for pattern in grouped_patterns[category_name]]
            }
            collection["item"].append(folder)

    # Add any remaining categories not in the order list
    for category_name in sorted(grouped_patterns.keys()):
        if category_name not in category_order:
            folder = {
                "name": category_name,
                "description": category_descriptions.get(category_name, ""),
                "item": [create_request_item(pattern) for pattern in grouped_patterns[category_name]]
            }
            collection["item"].append(folder)

    return collection


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate Getting Started collection from YAML configuration")
    parser.add_argument('--config', default='config/getting-started-patterns.yaml',
                        help='Path to YAML configuration file (default: config/getting-started-patterns.yaml)')
    parser.add_argument('--output', default='postman/generated/c2mapiv2-getting-started-collection.json',
                        help='Output file path (default: postman/generated/c2mapiv2-getting-started-collection.json)')

    args = parser.parse_args()

    print("📚 Generating Getting Started collection...")
    print()

    try:
        # Load patterns from YAML
        patterns = load_patterns_from_yaml(args.config)

        # Generate the collection
        collection = generate_getting_started_collection(patterns)

        # Count items for summary
        total_patterns = sum(len(folder["item"]) for folder in collection["item"])

        # Save to file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(collection, f, indent=2)

        print()
        print(f"✅ Successfully generated Getting Started collection!")
        print(f"   Config: {args.config}")
        print(f"   Output: {output_path}")
        print(f"   Categories: {len(collection['item'])}")
        print(f"   Total patterns: {total_patterns}")
        print()
        print("📊 Category breakdown:")
        for folder in collection["item"]:
            print(f"   - {folder['name']}: {len(folder['item'])} patterns")
        print()
        print("Next steps:")
        print("1. Upload to Postman workspace")
        print("2. Set {{baseUrl}} environment variable")
        print("3. Share with new API users for onboarding")

    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        return 1
    except yaml.YAMLError as e:
        print(f"❌ ERROR: Invalid YAML in configuration file: {e}")
        return 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
