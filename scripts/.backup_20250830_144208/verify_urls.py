import json
import sys

def verify_urls(item, parent_path=""):
    if isinstance(item, dict):
        if "url" in item and isinstance(item["url"], dict):
            host = "/".join(item["url"].get("host", []))
            path = "/".join(item["url"].get("path", []))
            expected_raw = f"{host}/{path}" if host and path else host or path
            raw = item["url"].get("raw", "")
            if raw != expected_raw:
                print(f"[URL MISMATCH] {parent_path} -> raw: {raw} | expected: {expected_raw}")
        for key, val in item.items():
            verify_urls(val, f"{parent_path}/{key}")
    elif isinstance(item, list):
        for idx, val in enumerate(item):
            verify_urls(val, f"{parent_path}[{idx}]")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_urls.py <path_to_postman_collection.json>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, "r") as f:
        data = json.load(f)

    print(f"Checking URLs in {filename}...\n")
    verify_urls(data)
