# Permutation Generator (Extended)

This bundle generates **all possible permutations** of request bodies for the API endpoints defined in the EBNF (`c2mapiv2-dd.ebnf`).

## 📦 Contents
- `permutation_generator.py` → Python script that generates wrapper-based JSON permutations (not inline strings).
- `run_permutations.sh` → Shell script to generate a sample output (`submitSingleDocWithTemplateParams`).
- `permutations/` → Folder where JSON output is written.

## ▶️ Usage
1. Ensure Python 3.9+ is installed.
2. Run the shell script:

```bash
chmod +x run_permutations.sh
./run_permutations.sh
```

This will generate:
- `permutations/submitSingleDocWithTemplateParams.json`

##  Notes
- Each `documentSourceIdentifier`, `recipientAddressSource`, `paymentDetails`, and optional `tags` permutation is fully expanded as **wrapper objects**.
- Current implementation: **submitSingleDocWithTemplateParams** endpoint only.
- Extendable: Add functions for other endpoints (see `endpoint_generators` in the code).
