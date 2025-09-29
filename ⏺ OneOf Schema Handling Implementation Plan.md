# OneOf Schema Handling Implementation Plan

## Pipeline Overview

The C2M API uses a unique data-driven pipeline:

```
EBNF Data Dictionary 
  → OpenAPI Spec Generation (ebnf_to_openapi_dynamic_v3.py)
  → Add SDK Examples (add-sdk-samples-to-spec.py) 
  → Add Data Examples (add_examples_to_spec_v2.py)
  → Postman Collection (openapi-to-postmanv2)
  → Add Test Data (addRandomDataToRaw.js)
  → Flatten & Add Tests
  → Upload to Postman
```

## The OneOf Problem

### 1. EBNF Definition

In `data_dictionary/c2mapiv2-dd.ebnf`, documentSourceIdentifier is defined as:

```ebnf
documentSourceIdentifier = 
      documentId                          (* Unique ID for a document previously uploaded *)
    | externalUrl                         (* Full HTTP/HTTPS URL *)
    | (uploadRequestId + documentName)    (* Document uploaded in a session *)
    | (uploadRequestId + zipId + documentName) (* File inside zip *)
    | (zipId + documentName) ;            (* Document inside archived zip *)
```

### 2. EBNF to OpenAPI Conversion Issue

In `scripts/active/ebnf_to_openapi_dynamic_v3.py`, when processing alternations (the `|` operator):

```python
def _generate_oneof_schema(self, choices: List[Any], context: str) -> Dict[str, Any]:
    for choice in choices:
        if choice_type == 'symbol':
            # Generates: {"$ref": "#/components/schemas/documentId"}
            schemas.append({"$ref": f"#/components/schemas/{symbol_name}"})
        
        elif choice_type == 'concatenation':
            # Problem: Generates anonymous inline schema!
            schemas.append(self._expression_to_schema(choice, context))
```

This results in:

```yaml
documentSourceIdentifier:
  oneOf:
    - $ref: '#/components/schemas/documentId'        # ✅ Named schema
    - $ref: '#/components/schemas/externalUrl'       # ✅ Named schema
    - type: object                                    # ❌ Anonymous schema!
      properties:
        uploadRequestId:
          $ref: '#/components/schemas/uploadRequestId'
        documentName:
          $ref: '#/components/schemas/documentName'
      required:
        - uploadRequestId
        - documentName
```

### 3. openapi-to-postmanv2 Limitation

When openapi-to-postmanv2 encounters oneOf with mixed named/anonymous schemas:
- It defaults to the first option's type
- Generates `<integer>` because documentId is an integer
- Ignores the other variants

## Solutions

### Option 1: Fix in EBNF to OpenAPI Converter (Recommended)

Modify `ebnf_to_openapi_dynamic_v3.py` to generate named schemas for concatenations:

```python
elif choice_type == 'concatenation':
    # Generate a named schema instead of inline
    schema_name = f"{context}_{self._generate_concatenation_name(choice)}"
    self.schemas[schema_name] = self._expression_to_schema(choice, context)
    schemas.append({"$ref": f"#/components/schemas/{schema_name}"})
```

### Option 2: Post-Process OpenAPI Spec

Add a step after OpenAPI generation to convert anonymous oneOf schemas to named schemas.

### Option 3: Define Named Types in EBNF

Modify the EBNF to explicitly name complex types:

```ebnf
uploadDocument = uploadRequestId + documentName;
zipDocument = uploadRequestId + zipId + documentName;
archivedZipDocument = zipId + documentName;

documentSourceIdentifier = 
      documentId
    | externalUrl
    | uploadDocument
    | zipDocument
    | archivedZipDocument ;
```

## Impact on Collections

### Linked Collection (Schema View)
- Should show type placeholders
- With proper oneOf handling: `<oneOf>` instead of `<integer>`
- Helps developers understand the field accepts multiple types

### Test Collection (Example Data)
- Should rotate through all oneOf variants
- Already handled by `addRandomDataToRaw_oneOf.js`
- Provides comprehensive test coverage

## Recommended Implementation

1. **Immediate Fix**: Post-process the OpenAPI spec to convert anonymous schemas
2. **Long-term Fix**: Modify `ebnf_to_openapi_dynamic_v3.py` to generate named schemas
3. **Pipeline Integration**: Add the fix as a standard step after OpenAPI generation

## Testing Strategy

1. Verify all oneOf schemas use named references
2. Confirm openapi-to-postmanv2 generates proper placeholders
3. Ensure test collections rotate through all variants
4. Validate against mock servers (Prism and Postman)

## Next Steps

1. Implement the OpenAPI oneOf fix in the pipeline
2. Update Makefile to include the fix step
3. Test with full pipeline run
4. Document the solution in CLAUDE.md