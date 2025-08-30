import json
import random
import re
from pathlib import Path
import sys

# Expect input and output file as arguments
if len(sys.argv) < 3:
    print("Usage: python generate_test_data.py <input_collection> <output_collection>")
    sys.exit(1)

INPUT_COLLECTION = Path(sys.argv[1])
OUTPUT_COLLECTION = Path(sys.argv[2])

def random_email():
    return f"user{random.randint(1000, 9999)}@example.com"

def random_name():
    names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
    return random.choice(names)

def random_id():
    return random.randint(1, 9999)

def random_phone():
    return f"+1-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"

def random_date():
    return "2025-01-01"

def generate_value(field_name):
    fname = field_name.lower()
    if "email" in fname:
        return random_email()
    elif "name" in fname:
        return random_name()
    elif "phone" in fname or "mobile" in fname:
        return random_phone()
    elif re.search(r"id$", fname):
        return random_id()
    elif "date" in fname:
        return random_date()
    return f"test_{random.randint(100,999)}"

def populate_examples(collection_data):
    for item in collection_data.get("item", []):
        if "item" in item:
            populate_examples(item)
        else:
            request = item.get("request", {})
            # Fill query parameters
            for param in request.get("url", {}).get("query", []):
                if not param.get("value") or "<string>" in str(param.get("value")):
                    param["value"] = generate_value(param["key"])
            # Fill raw JSON body
            body = request.get("body", {})
            if body.get("mode") == "raw":
                try:
                    json_body = json.loads(body.get("raw", "{}"))
                    for k, v in json_body.items():
                        if not v or isinstance(v, str) and "<string>" in v:
                            json_body[k] = generate_value(k)
                    body["raw"] = json.dumps(json_body, indent=2)
                except json.JSONDecodeError:
                    pass
    return collection_data

def main():
    if not INPUT_COLLECTION.exists():
        print(f"❌ Collection file not found: {INPUT_COLLECTION}")
        return

    with INPUT_COLLECTION.open("r", encoding="utf-8") as f:
        collection = json.load(f)

    updated_collection = populate_examples(collection)

    with OUTPUT_COLLECTION.open("w", encoding="utf-8") as f:
        json.dump(updated_collection, f, indent=2)

    print(f"✅ Example data added. Updated collection saved to {OUTPUT_COLLECTION}")

if __name__ == "__main__":
    main()
