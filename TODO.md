
## Merge Dual Template Systems

**Priority**: Medium
**Created**: 2026-03-12

**Problem**: 
We currently maintain TWO separate template systems for collections:
1. **getting-started-template.yaml** → Used by main build for Getting Started collections
2. **curated-examples-catalog.yaml** → Used for Real World Use Cases collection

Both templates define similar endpoints but in different formats, requiring duplicate maintenance.

**Current State**:
- `getting-started-template.yaml` - Template-based system using `scripts/utilities/generate_getting_started_collections.py`
- `curated-examples-catalog.yaml` - Curated v4 system using `scripts/active/generate_curated_collections_v4.py`

**Goal**: 
Consolidate into a single template system that can generate:
- Getting Started collection (placeholders + examples)
- Real World Use Cases collection
- Any other curated collections

**Benefits**:
- Single source of truth for endpoint examples
- Easier maintenance (one file to update)
- Consistent structure across collections
- Reduced risk of drift between templates

**Approach**:
1. Evaluate which system is more flexible (likely getting-started-template.yaml)
2. Add tag-based filtering to selected system
3. Migrate all examples from both files to unified template
4. Update Makefile targets
5. Test all collection generation
6. Archive deprecated system

**Files Involved**:
- `config/getting-started-template.yaml`
- `config/curated-examples-catalog.yaml`
- `scripts/utilities/generate_getting_started_collections.py`
- `scripts/active/generate_curated_collections_v4.py`
- Makefile targets: `postman-generate-getting-started-all`, `postman-generate-use-case-collection`

**Effort Estimate**: 4-6 hours
