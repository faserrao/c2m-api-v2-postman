# addRandomDataToRaw.js

This Node.js script modifies a Postman collection JSON by inserting **randomized test data** into all `request.body.raw` fields. It replaces placeholders such as `<string>`, `<number>`, `<integer>`, and `<boolean>` with realistic random values using [@faker-js/faker](https://github.com/faker-js/faker).

## Features

- **Smart placeholder replacement** - Replaces `<string>`, `<number>`, `<integer>`, `<boolean>` with context-aware random values
- **Context-aware generation** - Detects field names (email, phone, name, etc.) and generates appropriate data
- **Error injection** - Configurable error rate (`--error-rate`) to inject malformed data for testing error handling
- **Preview mode** - Use `--preview` to see changes without saving
- **Recursive processing** - Handles nested folders and complex collection structures
- **Multiple targets** - Processes request bodies, response bodies, and originalRequest bodies

## Installation

```bash
npm install
```

## Usage

```bash
node addRandomDataToRaw.js --input <file> --output <file> [options]
```

### Options

- `--input <file>` - Input Postman collection JSON file (required)
- `--output <file>` - Output file path (defaults to `{input}-randomized.json`)
- `--error-rate <0-100>` - Percentage chance to inject erroneous data (default: 0)
- `--preview` - Show first modification and exit without saving

### Examples

Basic usage:
```bash
node addRandomDataToRaw.js --input collection.json --output collection-test.json
```

With 20% error injection:
```bash
node addRandomDataToRaw.js --input collection.json --output collection-test.json --error-rate 20
```

Preview mode:
```bash
node addRandomDataToRaw.js --input collection.json --preview
```

## Placeholder Types

- `<string>` - Generates contextual strings based on field name
- `<number>` - Generates floating-point numbers
- `<integer>` - Generates whole numbers
- `<boolean>` - Generates true/false values

## Context-Aware Generation

The script intelligently generates data based on field names:

| Field Name Contains | Generated Data Type |
|-------------------|-------------------|
| email | Valid email address |
| phone, tel | Phone number |
| firstName, fname | First name |
| lastName, lname | Last name |
| name | Full name |
| username, user | Username |
| password, pwd | Password |
| city | City name |
| country | Country name |
| state, province | State/Province |
| zip, postal | Zip/Postal code |
| address, street | Street address |
| company, organization | Company name |
| title | Short sentence |
| jobtitle, position | Job title |
| description, desc | Paragraph text |
| url, website | URL |
| date | Date (YYYY-MM-DD) |
| time | Timestamp (ISO) |
| uuid, guid | UUID |
| id | Alphanumeric ID |
| price, cost, amount | Price (float) |
| quantity, count | Quantity (1-100) |
| age | Age (18-80) |
| year | Year (2000-2024) |

## Error Injection

When using `--error-rate`, the script can inject various types of erroneous data:

- null values
- Empty strings
- Invalid formats (e.g., "192.168.1.999" for dates)
- SQL injection attempts
- XSS attempts
- Very long strings
- Special characters
- Invalid dates

## Output

The script provides statistics showing:
- Number of modified requests
- Number of modified responses
- Number of modified original requests

## Example Transformation

**Before:**
```json
{
  "firstName": "<string>",
  "email": "<string>",
  "age": "<integer>",
  "isActive": "<boolean>"
}
```

**After:**
```json
{
  "firstName": "John",
  "email": "john.doe@example.com",
  "age": 35,
  "isActive": true
}
```

## Limitations

- Only processes `raw` body mode (JSON format)
- Does not process `formdata`, `urlencoded`, or `graphql` modes
- Requires valid JSON in raw bodies
- Only replaces exact placeholders (`<string>`, `<number>`, `<integer>`, `<boolean>`)

## Future Enhancements

- `--force` flag to add default bodies to requests without bodies
- `--default-template <file>` to specify custom default body templates
- Support for additional body modes (formdata, urlencoded)
- Custom placeholder definitions
- Logging of all modifications with request names