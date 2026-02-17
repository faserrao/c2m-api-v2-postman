# Common EBNF Tasks

Task-based tutorials for the most frequent data dictionary editing scenarios.

## Prerequisites

- Read [EBNF_QUICK_REFERENCE.md](EBNF_QUICK_REFERENCE.md) for syntax basics
- Read [NEW_DEVELOPER_QUICKSTART.md](NEW_DEVELOPER_QUICKSTART.md) for initial setup

## Before You Start

**ALWAYS run these commands before editing:**

```bash
# 1. Pull latest changes
git pull origin main

# 2. Check current state
./scripts/validate-before-commit.sh
```

**ALWAYS run these commands after editing:**

```bash
# 1. Validate your changes
./scripts/validate-before-commit.sh

# 2. Preview what will change
./scripts/preview-ebnf-changes.sh

# 3. Push your changes (interactive workflow)
./scripts/safe-push.sh "Your commit message"
```

## Task 1: Add a New Optional Field

**When to use**: Adding a new optional parameter to an existing endpoint.

### Step 1: Find the Endpoint Definition

Open `data_dictionary/c2mapiv2-dd.ebnf` and search for your endpoint.

**Example**: Adding `priority` to `submitSingleDocParams`

```bash
# Find the endpoint
grep -n "submitSingleDocParams =" data_dictionary/c2mapiv2-dd.ebnf
```

### Step 2: Add Field to Endpoint

Add the field in square brackets (makes it optional).

**BEFORE** (around line 616):
```ebnf
submitSingleDocParams =
      [ jobTemplate ]
    + docSourceAll
    + recipientAddressSource
    + [ paymentDetails ]
    + [ returnAddress ]
    + [ jobOptions ]
    + [ tags ] ;
```

**AFTER**:
```ebnf
submitSingleDocParams =
      [ jobTemplate ]
    + docSourceAll
    + recipientAddressSource
    + [ paymentDetails ]
    + [ returnAddress ]
    + [ priority ]         (* NEW FIELD - priority level *)
    + [ jobOptions ]
    + [ tags ] ;
```

**Key Points**:
- Square brackets `[ ]` = optional
- Plus signs `+` separate fields
- Comment `(* *)` explains what the field does
- Maintain consistent indentation

### Step 3: Define the Field Type

Add the field definition somewhere after the endpoint (typically nearby).

**Add after line 650**:
```ebnf
priority = "standard" | "rush" | "overnight" ;
```

**Field Type Options**:
- Enum (one of): `"value1" | "value2" | "value3"`
- String: `string`
- Integer: `integer`
- Boolean: `boolean`
- Array: `{ element }`
- Reference: Another defined identifier

### Step 4: Validate and Test

```bash
# 1. Validate EBNF syntax
./scripts/validate-before-commit.sh

# 2. Preview OpenAPI changes
./scripts/preview-ebnf-changes.sh

# 3. Test locally (optional but recommended)
make postman-instance-build-without-tests
```

### Step 5: Commit and Push

```bash
./scripts/safe-push.sh "Add priority field to submitSingleDocParams"
```

**Expected Result**:
- OpenAPI spec will have new optional field
- Postman collections will include field in requests
- Mock server will accept field in requests
- Documentation will show field as optional

### Common Pitfalls

**WRONG** - Missing semicolon:
```ebnf
priority = "standard" | "rush" | "overnight"
```

**WRONG** - Forgot to add to endpoint:
```ebnf
(* Field defined but never used in any endpoint *)
priority = "standard" | "rush" | "overnight" ;
```

**WRONG** - Wrong brackets (makes it required):
```ebnf
submitSingleDocParams =
    + priority    (* Missing [ ] makes it required! *)
```

---

## Task 2: Add a New Enum Value

**When to use**: Extending an existing enum with new options.

### Step 1: Find the Enum Definition

```bash
grep -n "priority =" data_dictionary/c2mapiv2-dd.ebnf
```

### Step 2: Add New Value

**BEFORE**:
```ebnf
priority = "standard" | "rush" | "overnight" ;
```

**AFTER**:
```ebnf
priority = "standard" | "rush" | "overnight" | "urgent" ;
```

**Key Points**:
- Pipe symbol `|` separates options
- Values must be in double quotes
- Add comment if value needs explanation

### Step 3: Validate and Test

```bash
./scripts/validate-before-commit.sh
./scripts/preview-ebnf-changes.sh
```

### Step 4: Commit

```bash
./scripts/safe-push.sh "Add urgent priority option"
```

**Expected Result**:
- OpenAPI spec will have 4 enum values
- API will accept "urgent" as valid value
- Mock server will accept new value

---

## Task 3: Add a New Required Field

**When to use**: Adding mandatory parameter to endpoint.

WARNING: This is a BREAKING CHANGE. All clients must provide this field.

### Step 1: Add Field WITHOUT Brackets

**BEFORE**:
```ebnf
submitSingleDocParams =
      docSourceAll
    + recipientAddressSource ;
```

**AFTER**:
```ebnf
submitSingleDocParams =
      docSourceAll
    + recipientAddressSource
    + confirmationEmail ;    (* NEW REQUIRED FIELD *)
```

**Key Points**:
- NO square brackets = required
- All requests must include this field
- Breaking change for existing clients

### Step 2: Define the Field

```ebnf
confirmationEmail = string ;
```

### Step 3: Consider Migration Strategy

**Option A: Make it optional first, then required later**
```ebnf
(* Phase 1: Optional - add field with [ ] *)
submitSingleDocParams =
    + [ confirmationEmail ] ;

(* Phase 2: Required - remove [ ] after clients updated *)
submitSingleDocParams =
    + confirmationEmail ;
```

**Option B: Provide default value in documentation**
```ebnf
confirmationEmail = string ;  (* Defaults to account email if not provided *)
```

### Step 4: Update Documentation

Add migration notes explaining:
- When field becomes required
- Default behavior if omitted
- Example values

### Step 5: Validate and Test

```bash
./scripts/validate-before-commit.sh
./scripts/preview-ebnf-changes.sh
```

**Check Preview for Breaking Changes**:
- Look for "WARNING: Changes to required fields detected"
- Verify added to required fields list in OpenAPI

---

## Task 4: Change Field Type

**When to use**: Converting field from one type to another.

WARNING: Usually a BREAKING CHANGE unless types are compatible.

### Example: String to Enum

**BEFORE**:
```ebnf
priority = string ;
```

**AFTER**:
```ebnf
priority = "standard" | "rush" | "overnight" ;
```

**Impact**:
- BREAKING: Clients sending other strings will fail validation
- Consider: Keep both for transition period

### Example: Single Value to Array

**BEFORE**:
```ebnf
tag = string ;
```

**AFTER**:
```ebnf
tags = { string } ;  (* Changed: Single tag -> Array of tags *)
```

**Impact**:
- BREAKING: Field name changed (tag -> tags)
- BREAKING: Structure changed (string -> array)
- Requires client code updates

### Safe Transition Strategy

1. Add new field (don't remove old one)
2. Deprecate old field in documentation
3. Remove old field after transition period

```ebnf
(* Deprecated - use tags array instead *)
tag = string ;

(* NEW - supports multiple tags *)
tags = { string } ;
```

---

## Task 5: Add Array Field

**When to use**: Field can have multiple values.

### Step 1: Define Array Element

**Simple Array** (primitives):
```ebnf
tags = { string } ;
```

**Complex Array** (objects):
```ebnf
(* Define the element first *)
recipient =
      firstName
    + lastName
    + address ;

(* Then make it an array *)
recipients = { recipient } ;
```

### Step 2: Add to Endpoint

```ebnf
submitMultiDocParams =
      docSourceAll
    + [ recipients ]     (* Array of recipients *)
    + [ tags ] ;         (* Array of tags *)
```

### Examples

**Array of Strings**:
```ebnf
tags = { string } ;
```
JSON: `["tag1", "tag2", "tag3"]`

**Array of Integers**:
```ebnf
pageNumbers = { integer } ;
```
JSON: `[1, 2, 3, 5, 7]`

**Array of Objects**:
```ebnf
document =
      documentId
    + filename ;

documents = { document } ;
```
JSON:
```json
[
  {"documentId": 123, "filename": "doc1.pdf"},
  {"documentId": 456, "filename": "doc2.pdf"}
]
```

---

## Task 6: Add Nested Object

**When to use**: Grouping related fields together.

### Step 1: Define Nested Object

```ebnf
billingAddress =
      street
    + city
    + state
    + zipCode ;
```

### Step 2: Add to Parent Object

```ebnf
creditCard =
      cardNumber
    + expirationDate
    + cvv
    + [ billingAddress ] ;    (* Nested object *)
```

### Step 3: Add to Endpoint

```ebnf
paymentDetails =
      creditCard
    | ach
    | invoice ;

submitSingleDocParams =
      docSourceAll
    + recipientAddressSource
    + [ paymentDetails ] ;
```

### Result Structure

```json
{
  "paymentDetails": {
    "creditCard": {
      "cardNumber": "4111111111111111",
      "expirationDate": "12/25",
      "cvv": "123",
      "billingAddress": {
        "street": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "zipCode": "62701"
      }
    }
  }
}
```

---

## Task 7: Add OneOf Choice

**When to use**: Field accepts one of several different structures.

### Example: Document Source

```ebnf
(* Define each option *)
documentIdSource = documentId ;
requestIdSource = requestId + [ filename ] ;
urlSource = url ;

(* Combine with pipe | *)
docSourceStandard =
      documentIdSource
    | requestIdSource
    | urlSource ;
```

### Usage in Endpoint

```ebnf
submitSingleDocParams =
      docSourceStandard    (* User picks ONE of the three options *)
    + recipientAddressSource ;
```

### Result

Client can send ANY of these:

**Option 1**:
```json
{"documentId": 123}
```

**Option 2**:
```json
{"requestId": 456, "filename": "document.pdf"}
```

**Option 3**:
```json
{"url": "https://example.com/doc.pdf"}
```

---

## Task 8: Make Required Field Optional

**When to use**: Field initially required but should be optional.

WARNING: Not a breaking change (makes API more flexible).

### Step 1: Add Square Brackets

**BEFORE**:
```ebnf
submitSingleDocParams =
      docSourceAll
    + recipientAddressSource
    + paymentDetails ;    (* Required *)
```

**AFTER**:
```ebnf
submitSingleDocParams =
      docSourceAll
    + recipientAddressSource
    + [ paymentDetails ] ;    (* Now optional *)
```

### Step 2: Document Default Behavior

```ebnf
(* Payment charged to account if not provided *)
paymentDetails =
      creditCard
    | ach
    | invoice ;
```

### Impact

- NOT breaking: Old clients still work
- Improves flexibility: New clients can omit field
- Requires: Clear documentation of default behavior

---

## Task 9: Rename Field

**When to use**: Field name is confusing or inconsistent.

WARNING: This is a BREAKING CHANGE.

### Safe Renaming Strategy

**Phase 1: Add new field, deprecate old**
```ebnf
submitSingleDocParams =
      docSourceAll
    + recipientAddressSource
    + [ tags ]                    (* NEW name *)
    + [ tagList ] ;               (* DEPRECATED - use tags instead *)
```

**Phase 2: Remove old field after transition**
```ebnf
submitSingleDocParams =
      docSourceAll
    + recipientAddressSource
    + [ tags ] ;                  (* Old tagList removed *)
```

### Immediate Rename (Breaking Change)

If you must rename immediately:

```ebnf
(* OLD - REMOVED *)
(* tagList = { string } ; *)

(* NEW - REPLACES tagList *)
tags = { string } ;
```

Document migration:
```
BREAKING CHANGE: Field renamed
- Old name: tagList
- New name: tags
- Action required: Update client code
```

---

## Task 10: Remove Field

**When to use**: Field no longer needed.

WARNING: This is a BREAKING CHANGE.

### Safe Removal Strategy

**Phase 1: Make optional and deprecate**
```ebnf
submitSingleDocParams =
      docSourceAll
    + recipientAddressSource
    + [ deprecatedField ] ;    (* DEPRECATED - will be removed *)
```

**Phase 2: Comment out (don't delete)**
```ebnf
(* REMOVED: deprecatedField
   Last used in v2.3
   Reason: Replaced by newField
*)
(* deprecatedField = string ; *)
```

### Complete Removal

Only delete AFTER:
- All clients updated
- Sufficient transition period (3-6 months)
- Documented in release notes

---

## Validation Checklist

After ANY edit, run:

```bash
# 1. Syntax validation
./scripts/validate-before-commit.sh

# 2. What will change
./scripts/preview-ebnf-changes.sh

# 3. Breaking changes check
# Look for these warnings in preview:
#   - "endpoint(s) removed"
#   - "Changes to required fields"
#   - "schema properties removed/modified"
```

---

## Testing Your Changes

### Minimal Testing
```bash
./scripts/validate-before-commit.sh
```

### Recommended Testing
```bash
./scripts/preview-ebnf-changes.sh
make postman-instance-build-without-tests
```

### Complete Testing (Local)
```bash
./scripts/safe-push.sh "Your commit message"
# Answer "y" to run local build
```

### Complete Testing (CI/CD)
```bash
git push origin main
# Monitor: https://github.com/click2mail/c2m-api-v2-postman/actions
```

---

## Common Patterns Library

### Pattern: Optional with Default

```ebnf
submitSingleDocParams =
      docSourceAll
    + recipientAddressSource
    + [ priority ] ;        (* Defaults to "standard" if not provided *)

priority = "standard" | "rush" | "overnight" ;
```

### Pattern: Nested Arrays

```ebnf
page =
      pageNumber
    + documentId ;

document =
      filename
    + { page } ;            (* Array of pages *)

batch = { document } ;      (* Array of documents *)
```

### Pattern: Conditional Fields

```ebnf
(* Use ONE of these *)
docSourceAll =
      documentIdSource
    | requestIdSource
    | urlSource ;

(* documentId requires no additional fields *)
documentIdSource = documentId ;

(* requestId can include optional filename *)
requestIdSource = requestId + [ filename ] ;
```

### Pattern: Reusable Components

```ebnf
(* Define once *)
address =
      firstName
    + lastName
    + street
    + city
    + state
    + zipCode ;

(* Use many times *)
recipientAddress = address ;
returnAddress = address ;
billingAddress = address ;
```

---

## Troubleshooting

### Validation Fails: "0 productions parsed"

**Cause**: Critical syntax error

**Common Issues**:
- Missing semicolon
- Dictionary syntax `{ string : string }` (NOT SUPPORTED)
- Unmatched parentheses in comment

**Fix**:
```bash
# See detailed error
./scripts/validate-before-commit.sh

# Look for line number in error message
# Fix syntax error at that line
```

### Validation Fails: "Duplicate definition"

**Cause**: Same identifier defined twice

**Fix**:
```bash
# Find all occurrences
grep "^identifierName =" data_dictionary/c2mapiv2-dd.ebnf

# Keep only one definition, comment out others
```

### Preview Shows Unexpected Changes

**Cause**: Field referenced but not defined, or typo

**Fix**:
```bash
# Check definition exists
grep "newField =" data_dictionary/c2mapiv2-dd.ebnf

# Check all references
grep "newField" data_dictionary/c2mapiv2-dd.ebnf
```

---

## Best Practices

1. **Always comment your intent**
   ```ebnf
   (* Priority for processing - affects turnaround time *)
   priority = "standard" | "rush" | "overnight" ;
   ```

2. **Group related definitions**
   ```ebnf
   (* Document source options *)
   documentIdSource = documentId ;
   requestIdSource = requestId + [ filename ] ;
   urlSource = url ;

   docSourceStandard =
         documentIdSource
       | requestIdSource
       | urlSource ;
   ```

3. **Use descriptive names**
   - GOOD: `recipientAddressSource`
   - BAD: `recAddr`

4. **Match existing conventions**
   - Look at similar fields
   - Follow same naming pattern
   - Use consistent indentation

5. **Validate early and often**
   ```bash
   # After each significant change
   ./scripts/validate-before-commit.sh
   ```

6. **Test before pushing**
   ```bash
   # Preview what will change
   ./scripts/preview-ebnf-changes.sh

   # Test locally if possible
   make postman-instance-build-without-tests
   ```

---

## Quick Reference

| Task | Command | Time |
|------|---------|------|
| Validate EBNF | `./scripts/validate-before-commit.sh` | 10 sec |
| Preview changes | `./scripts/preview-ebnf-changes.sh` | 20 sec |
| Safe push | `./scripts/safe-push.sh "message"` | 5-10 min |
| Local build | `make postman-instance-build-without-tests` | 8 min |
| Local build with tests | `make postman-instance-build-with-tests` | 15 min |

---

## Next Steps

- Read [WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md) for visual pipeline flow
- Read [ROLLBACK.md](ROLLBACK.md) for emergency procedures
- See [EBNF_QUICK_REFERENCE.md](EBNF_QUICK_REFERENCE.md) for syntax details

---

## Getting Help

**Validation errors?**
- Read error message carefully (line number shown)
- Check [EBNF_QUICK_REFERENCE.md](EBNF_QUICK_REFERENCE.md) for syntax rules
- Look for similar patterns in existing EBNF

**Unsure about approach?**
- Find similar field in data dictionary
- Copy pattern and modify
- Ask team for review

**Need to rollback?**
- See [ROLLBACK.md](ROLLBACK.md) for emergency procedures

---

**Remember**: The data dictionary is your single source of truth. Get it right here, and everything else follows automatically.
