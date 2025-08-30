#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def fix_url(url):
    """Rebuild url.raw from host + path if it's missing or inconsistent."""
    if not isinstance(url, dict):
        return

    host = "/".join(url.get("host", []))
    path = "/".join(url.get("path", []))
    expected_raw = f"{host}/{path}" if host and path else host or path

    if not url.get("raw") or url["raw"] != expected_raw:
        url["raw"] = expected_raw



def process_item(item):
    """Recursively fix URLs in request and response blocks."""
    if isinstance(item, dict):
        if "request" in item and "url" in item["request"]:
            fix_url(item["request"]["url"])
        if "response" in item and isinstance(item["response"], list):
            for resp in item["response"]:
                if "originalRequest" in resp and "url" in resp["originalRequest"]:
                    fix_url(resp["originalRequest"]["url"])
        if "item" in item and isinstance(item["item"], list):
            for sub_item in item["item"]:
                process_item(sub_item)


def main(input_file, output_file):
    data = json.loads(Path(input_file).read_text(encoding="utf-8"))
    process_item(data)
    Path(output_file).write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"✅ URLs fixed in {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: fix_collection_urls_v2.py <input.json> <output.json>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
