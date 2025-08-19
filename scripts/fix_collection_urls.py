#!/usr/bin/env python3
"""
fix_collection_urls.py

Usage:
    python3 fix_collection_urls.py <input_collection_file> <output_collection_file>

This script:
- Ensures all Postman request URLs use {{baseUrl}}.
- Validates the structure of the collection.
"""

import json
import sys
from pathlib import Path

def ensure_baseurl_in_request(item):
    """Ensure requests use {{baseUrl}} for host."""
    if "request" in item and "url" in item["request"]:
        url = item["request"]["url"]
        if isinstance(url, dict):
            raw = url.get("raw", "")
            if not raw.startswith("{{baseUrl}}"):
                raw = raw.lstrip('/')
                url["raw"] = f"{{{{baseUrl}}}}/{raw}"
            url["host"] = ["{{baseUrl}}"]

    if "item" in item and isinstance(item["item"], list):
        for sub in item["item"]:
            ensure_baseurl_in_request(sub)

def validate_collection(collection):
    if "item" not in collection or not isinstance(collection["item"], list):
        raise ValueError("Invalid collection: top-level 'item' array is missing.")
    print("✅ Collection structure validated.")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 fix_collection_urls.py <input_collection_file> <output_collection_file>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        collection = json.load(f)

    print("🔧 Fixing Postman collection URLs with {{baseUrl}}...")
    for item in collection.get("item", []):
        ensure_baseurl_in_request(item)

    print("🔍 Validating collection...")
    validate_collection(collection)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2)

    print(f"🎉 Collection fixed and saved: {output_file}")

if __name__ == "__main__":
    main()
