# EBNF Quick Reference

One-page cheat sheet for editing the C2M API V2 data dictionary.

## File Location

```
data_dictionary/c2mapiv2-dd.ebnf
```

## Basic Syntax

### Definition Format
```ebnf
identifier = definition ;
```

Every definition ends with semicolon `;`

### Comments
```ebnf
(* This is a comment *)
(* Comments can span
   multiple lines *)
```

## Field Types

### String
```ebnf
myField = string ;
```

### Integer
```ebnf
myField = integer ;
```

### Boolean
```ebnf
myField = boolean ;
```

### Enum (One Of)
```ebnf
myField = "value1" | "value2" | "value3" ;
```

Example:
```ebnf
priority = "standard" | "rush" | "overnight" ;
```

## Structures

### Required Field
```ebnf
myEndpoint = requiredField ;
```

No brackets = field is required

### Optional Field
```ebnf
myEndpoint = [ optionalField ] ;
```

Square brackets `[ ]` = field is optional

### Multiple Fields
```ebnf
myEndpoint =
      field1
    + field2
    + field3 ;
```

Plus sign `+` separates fields

### Array
```ebnf
myArray = { arrayElement } ;
```

Curly braces `{ }` = array of elements (zero or more)

Example:
```ebnf
tags = { string } ;  (* Array of strings *)
```

### Nested Object
```ebnf
myObject =
      subField1
    + subField2 ;

parentObject =
      topField
    + myObject ;
```

## Complex Patterns

### Optional Field with Default
```ebnf
myEndpoint =
      requiredField
    + [ optionalField ]  (* Defaults to null if not provided *)
    + anotherRequired ;
```

### Choice (OneOf)
```ebnf
documentSource =
      documentIdSource
    | urlSource
    | requestIdSource ;
```

Pipe `|` = choose one of these options

### Mix Required and Optional
```ebnf
submitJobParams =
      [ jobTemplate ]      (* optional *)
    + docSourceAll         (* required *)
    + [ paymentDetails ]   (* optional *)
    + [ returnAddress ]    (* optional *)
    + [ jobOptions ]       (* optional - mutually exclusive with jobTemplate *)
    + [ tags ] ;           (* optional *)
```

## Common Patterns

### Address Object
```ebnf
address =
      firstName
    + lastName
    + address1
    + [ address2 ]
    + city
    + state
    + zip
    + country ;
```

### Nested Choice (OneOf in Object)
```ebnf
paymentDetails =
      creditCard
    | invoice
    | ach
    | userCredit ;

(* Use exactly ONE of these payment methods *)
```

### Array of Objects
```ebnf
jobItem =
      docSource
    + recipientAddress ;

multiDocJobs = { jobItem } ;
```

## Validation Rules

### Before You Commit

✓ Run validation:
```bash
./scripts/validate-before-commit.sh
```

### What Gets Checked

1. **Syntax Errors**
   - Missing semicolons
   - Unmatched parentheses
   - Invalid characters

2. **Duplicate Definitions**
   - Same identifier defined twice
   - Validation shows line numbers

3. **Undefined References**
   - Reference to non-existent identifier
   - OpenAPI generation will fail

## Common Errors

### Error: "Parse error at line X"

**Cause**: Syntax error in EBNF

**Common Issues**:
- Missing semicolon at end
- Unmatched parentheses in comment
- Dictionary syntax `{ string : string }` (NOT SUPPORTED)

**Fix**:
```ebnf
(* WRONG - Not supported *)
errorDetails = { string : string } ;

(* RIGHT - Use string type *)
errorDetails = string ;  (* JSON object with key-value pairs *)
```

### Error: "0 productions parsed"

**Cause**: Critical syntax error preventing parsing

**Check**:
1. Dictionary syntax (use `string` not `{ key : value }`)
2. Unclosed comments
3. Missing semicolons

### Error: "Duplicate definition"

**Cause**: Same identifier defined multiple times

**Find duplicates**:
```bash
grep "^identifierName =" data_dictionary/c2mapiv2-dd.ebnf
```

**Fix**: Keep only one definition, delete others

## Style Guidelines

### Field Naming
- Use camelCase: `firstName`, `paymentDetails`
- Be descriptive: `recipientAddressSource` not `recAddr`
- Match existing conventions

### Comments
- Explain WHY, not WHAT
- Document business rules
- Note mutual exclusions

Example:
```ebnf
(* jobTemplate and jobOptions are mutually exclusive
   IF both present THEN reject as validation error *)
```

### Organization
- Group related definitions
- Keep endpoint definitions together
- Put helper types before they're used

## Testing Your Changes

### Step 1: Validate
```bash
./scripts/validate-before-commit.sh
```

### Step 2: Preview
```bash
./scripts/preview-ebnf-changes.sh
```

### Step 3: Test Locally (Optional)
```bash
make postman-instance-build-without-tests
```

### Step 4: Commit & Push
```bash
./scripts/safe-push.sh "Your commit message"
```

## What NOT to Do

### DON'T Use Dictionary Syntax
```ebnf
(* WRONG *)
myField = { string : string } ;

(* RIGHT *)
myField = string ;
```

### DON'T Forget Semicolons
```ebnf
(* WRONG *)
myField = string

(* RIGHT *)
myField = string ;
```

### DON'T Create Circular References
```ebnf
(* WRONG - A depends on B, B depends on A *)
fieldA = fieldB ;
fieldB = fieldA ;
```

### DON'T Commit Without Validation
Always run `./scripts/validate-before-commit.sh` first!

## Quick Examples

### Add Simple Field
```ebnf
(* Add to endpoint definition *)
myEndpoint =
      existingField
    + [ newField ]    (* Add this line *)
    + anotherField ;

(* Define the field *)
newField = string ;
```

### Add Enum Field
```ebnf
(* Add to endpoint *)
myEndpoint =
      existingField
    + [ priority ]    (* Add this *)
    + anotherField ;

(* Define enum values *)
priority = "low" | "medium" | "high" ;
```

### Add Nested Object
```ebnf
(* Define nested object first *)
contactInfo =
      email
    + phone ;

(* Then use in endpoint *)
myEndpoint =
      existingField
    + [ contactInfo ]
    + anotherField ;
```

## Getting Help

**Validation fails?**
- Read error message carefully
- Check line number mentioned
- Look for common errors above

**Unsure about syntax?**
- Find similar pattern in existing EBNF
- Copy and modify
- See COMMON_EBNF_TASKS.md for examples

**Need to rollback?**
- See ROLLBACK.md for emergency procedures

## Pro Tips

1. **Copy existing patterns** - Don't reinvent the wheel
2. **Validate early, validate often** - Catch errors fast
3. **Small changes first** - Easier to debug
4. **Add comments** - Help future developers (including you!)
5. **Preview changes** - See what OpenAPI will look like

## Remember

- EBNF = Single source of truth
- Everything else auto-generated
- Validation catches 80% of errors
- Preview shows what will change
- CI/CD does the rest

**Keep this cheat sheet open while editing!**
