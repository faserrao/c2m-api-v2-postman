#!/usr/bin/env python3
import json
import argparse

# --- Definitions extracted from EBNF ---
# Wrapper object structures (simplified for demonstration)

documentSourceIdentifier_variants = [
    {"documentSourceIdentifier": {"documentId": 1234}},
    {"documentSourceIdentifier": {"externalUrl": "https://example.com/doc.pdf"}},
    {"documentSourceIdentifier": {"uploadRequestId": 5678, "documentName": "file.pdf"}},
    {"documentSourceIdentifier": {"uploadRequestId": 5678, "zipId": 42, "documentName": "file.pdf"}},
    {"documentSourceIdentifier": {"zipId": 42, "documentName": "file.pdf"}}
]

recipientAddressSource_variants = [
    {"recipientAddress": {
        "firstName": "John",
        "lastName": "Doe",
        "address1": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "country": "USA"
    }},
    {"addressListId": 99},
    {"addressId": 77}
]

paymentDetails_variants = [
    {"paymentDetails": {"creditCardDetails": {
        "cardType": "visa",
        "cardNumber": "4111111111111111",
        "expirationDate": {"month": 12, "year": 2025},
        "cvv": 123
    }}},
    {"paymentDetails": {"invoiceDetails": {
        "invoiceNumber": "INV-1001",
        "amountDue": 250.0
    }}},
    {"paymentDetails": {"achDetails": {
        "routingNumber": "021000021",
        "accountNumber": "123456789",
        "checkDigit": 7
    }}},
    {"paymentDetails": {"creditAmount": {
        "amount": 100.0,
        "currency": "USD"
    }}},
    {"paymentDetails": {"applePayPayment": "TBD"}},
    {"paymentDetails": {"googlePayPayment": "TBD"}}
]

tags_variants = [
    {"tags": ["legal", "certified"]},
    {"tags": ["marketing", "postcard"]},
    {}
]

# --- Endpoint permutations ---
def generate_submitSingleDocWithTemplateParams():
    results = []
    for doc in documentSourceIdentifier_variants:
        for rec in recipientAddressSource_variants:
            for pay in paymentDetails_variants:
                for tags in tags_variants:
                    obj = {}
                    obj.update(doc)
                    obj.update({"recipientAddressSources": [rec]})
                    obj["jobTemplate"] = "example_template"
                    obj.update(pay)
                    if tags:
                        obj.update(tags)
                    results.append(obj)
    return results

# TODO: Add similar functions for other 8 endpoints…
# For demo: only SingleDocWithTemplate fully implemented

endpoint_generators = {
    "submitSingleDocWithTemplateParams": generate_submitSingleDocWithTemplateParams,
    # "submitMultiDocWithTemplateParams": generate_submitMultiDocWithTemplateParams,
    # ...
}

def main():
    parser = argparse.ArgumentParser(description="Generate permutations for API endpoints from EBNF")
    parser.add_argument("--endpoint", required=True, help="Endpoint name to generate permutations for")
    parser.add_argument("--out", required=True, help="Output JSON file")
    args = parser.parse_args()

    if args.endpoint not in endpoint_generators:
        raise ValueError(f"Endpoint {args.endpoint} not supported yet.")

    generator = endpoint_generators[args.endpoint]
    permutations = generator()
    with open(args.out, "w") as f:
        json.dump(permutations, f, indent=2)
    print(f"✅ Generated {len(permutations)} permutations for {args.endpoint} → {args.out}")

if __name__ == "__main__":
    main()
