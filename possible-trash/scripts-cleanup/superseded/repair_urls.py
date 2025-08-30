import json
import sys
from pathlib import Path

def repair_urls(item_list, parent_path=None):
    """
    Recursively repair request URLs using only folder hierarchy.
    """
    if parent_path is None:
        parent_path = []

    for item in item_list:
        current_path = parent_path + [item.get("name", "").strip().lower().replace(" ", "_")]

        if "request" in item:
            request = item["request"]
            # Use only parent_path (excluding the request name)
            path_parts = parent_path
            raw_url = "{{baseUrl}}/" + "/".join(path_parts)
            request["url"] = {
                "raw": raw_url,
                "host": ["{{baseUrl}}"],
                "path": path_parts
            }

        if "item" in item:
            repair_urls(item["item"], current_path)

def main(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "item" in data:
        repair_urls(data["item"])
    else:
        print("❌ Invalid Postman collection: no top-level 'item' found.")
        sys.exit(1)

    output_file = path.with_name(path.stem + ".fixed_urls.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"✅ URLs repaired and saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/repair_urls.py <collection_file>")
        sys.exit(1)
    main(sys.argv[1])
