import argparse
import itertools
import json

def expand_options(options, prune=None):
    expanded = []
    for opt in options:
        if isinstance(opt, list):
            expanded.extend(expand_options(opt, prune))
        else:
            expanded.append(opt)
    return expanded

def generate_permutations(prune=False):
    # Example structure for Use Case 1
    documentSourceIdentifier = [
        "documentId (integer)",
        "externalUrl (string)",
        "uploadRequestId + documentName",
        "uploadRequestId + zipId + documentName",
        "zipId + documentName"
    ]
    recipientAddressSource = [
        "recipientAddress",
        "addressListId (integer)",
        "addressId (integer)"
    ]
    jobTemplate = ["jobTemplate (string)"]
    paymentDetails = [
        "creditCardPayment",
        "invoicePayment",
        "achPayment",
        "userCreditPayment",
        "applePayPayment",
        "googlePayPayment"
    ]
    tags = ["tags (optional)"]

    # Build permutations for submitSingleDocWithTemplateParams
    cases = [
        ("doc only", [documentSourceIdentifier, jobTemplate, paymentDetails, tags]),
        ("recipient only", [recipientAddressSource, jobTemplate, paymentDetails, tags]),
        ("doc + recipient", [documentSourceIdentifier, recipientAddressSource, jobTemplate, paymentDetails, tags]),
    ]

    results = {}
    for label, groups in cases:
        if prune:
            # Only include minimal representative from each group
            pruned_groups = [[g[0]] for g in groups]
            perms = list(itertools.product(*pruned_groups))
        else:
            perms = list(itertools.product(*groups))

        results[label] = [list(p) for p in perms]

    return results

def main():
    parser = argparse.ArgumentParser(description="Generate parameter permutations from EBNF")
    parser.add_argument("--interactive", action="store_true", help="Enable pruning mode")
    args = parser.parse_args()

    results = generate_permutations(prune=args.interactive)

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
