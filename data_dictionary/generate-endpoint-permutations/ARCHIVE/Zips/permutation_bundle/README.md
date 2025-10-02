# Permutation Generator

This tool expands permutations of API parameter structures from the EBNF specification.

## Usage

Generate **all permutations**:

```bash
./run_permutations.sh
```

Run in **interactive pruning mode** (minimal representative cases only):

```bash
./run_permutations.sh --interactive
```

## Output

Results are printed as JSON to the console.

Example (pruned mode):
```json
{
  "doc only": [["documentId (integer)", "jobTemplate (string)", "creditCardPayment", "tags (optional)"]],
  "recipient only": [["recipientAddress", "jobTemplate (string)", "creditCardPayment", "tags (optional)"]],
  "doc + recipient": [["documentId (integer)", "recipientAddress", "jobTemplate (string)", "creditCardPayment", "tags (optional)"]]
}
```
