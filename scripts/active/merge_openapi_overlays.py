#!/usr/bin/env python3
"""
Merge OpenAPI overlays while preserving complex structures like oneOf
"""

import yaml
import sys
from collections import OrderedDict

def ordered_load(stream, Loader=yaml.FullLoader):
    class OrderedLoader(Loader):
        pass
    
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return OrderedDict(loader.construct_pairs(node))
    
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    
    return yaml.load(stream, OrderedLoader)

def ordered_dump(data, stream=None, **kwds):
    class OrderedDumper(yaml.Dumper):
        pass
    
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    
    return yaml.dump(data, stream, OrderedDumper, **kwds)

def deep_merge(base, overlay):
    """
    Deep merge overlay into base, preserving complex structures
    """
    if isinstance(base, dict) and isinstance(overlay, dict):
        merged = base.copy()
        for key, value in overlay.items():
            if key in merged:
                # Special handling for paths to preserve base endpoint definitions
                if key == 'paths' and isinstance(merged[key], dict) and isinstance(value, dict):
                    # Only add new paths from overlay, don't override existing ones
                    for path, path_def in value.items():
                        if path not in merged[key]:
                            merged[key][path] = path_def
                else:
                    merged[key] = deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
    else:
        # For non-dict types, overlay wins
        return overlay

def main():
    if len(sys.argv) != 4:
        print("Usage: merge_openapi_overlays.py <base.yaml> <overlay.yaml> <output.yaml>")
        sys.exit(1)
    
    base_file = sys.argv[1]
    overlay_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Load files
    with open(base_file, 'r') as f:
        base = ordered_load(f)
    
    with open(overlay_file, 'r') as f:
        overlay = ordered_load(f)
    
    # Merge
    merged = deep_merge(base, overlay)
    
    # Write output
    with open(output_file, 'w') as f:
        ordered_dump(merged, f, default_flow_style=False, sort_keys=False, width=1000)
    
    print(f"✅ Merged {overlay_file} into {base_file} -> {output_file}")

if __name__ == "__main__":
    main()