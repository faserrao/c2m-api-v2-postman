import itertools
import json
import os
import re

# Path to the EBNF data dictionary
EBNF_FILE = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "data_dictionary", "c2mapiv2-dd.ebnf"
)
EBNF_FILE = os.path.abspath(EBNF_FILE)

OUTPUT_DIR = "permutations"


def parse_use_cases(ebnf_file):
    """Parse top-level use case definitions from the EBNF file."""
    endpoints = {}
    with open(ebnf_file, "r") as f:
        lines = f.readlines()

    current_name = None
    current_def = []
    for line in lines:
        match = re.match(r"^(\w+)\s*=", line.strip())
        if match and match.group(1).endswith("Params"):
            # save previous if exists
            if current_name and current_def:
                endpoints[current_name] = current_def
            # start new block
            current_name = match.group(1)
            current_def = [line.rstrip("\n")]
        elif current_name:
            if line.strip() == "":
                continue
            current_def.append(line.rstrip("\n"))
            if line.strip().endswith(";"):
                endpoints[current_name] = current_def
                current_name = None
                current_def = []

    return endpoints


def parse_component_options(component):
    """Return possible choices for each component (pruned realistic options)."""
    mapping = {
        "documentSourceIdentifier": [
            {"documentId": 1234},
            {"externalUrl": "https://example.com/doc.pdf"},
            {
                "uploadRequestId": 987,
                "documentName": "invoice.pdf"
            },
            {
                "uploadRequestId": 654,
                "zipId": 321,
                "documentName": "contract.pdf"
            },
            {
                "zipId": 111,
                "documentName": "newsletter.pdf"
            }
        ],
        "recipientAddressSource": [
            {
                "firstName": "John",
                "lastName": "Doe",
                "address1": "123 Main Street",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            {"addressListId": 42},
            {"addressId": 99}
        ],
        "jobTemplate": ["legal_certified_mail", "invoice_batch", "newsletter_monthly"],
        "paymentDetails": [
            {"creditCardDetails": {
                "cardType": "visa",
                "cardNumber": "4111111111111111",
                "expirationDate": {"month": 12, "year": 2025},
                "cvv": 123
            }},
            {"invoiceDetails": {"invoiceNumber": "INV-1001", "amountDue": 200.50}},
            {"achDetails": {"routingNumber": "111000025", "accountNumber": "123456789", "checkDigit": 7}},
            {"userCreditPayment": {"amount": 50, "currency": "USD"}},
            {"applePayPayment": "TBD"},
            {"googlePayPayment": "TBD"}
        ],
        "tags": [["legal", "certified"], ["batch", "invoice"], ["campaign", "newsletter"]],
    }
    return mapping.get(component, [f"<{component}>"])


def generate_permutations(endpoint):
    """Generate permutations for a given endpoint."""
    endpoint_components = {
        "submitSingleDocWithTemplateParams": [
            "documentSourceIdentifier",
            "recipientAddressSource",
            "jobTemplate",
            "paymentDetails",
            "tags"
        ],
        "submitMultiDocWithTemplateParams": [
            "documentSourceIdentifier",
            "recipientAddressSource",
            "jobTemplate",
            "paymentDetails",
            "tags"
        ],
        "mergeMultiDocWithTemplateParams": [
            "documentSourceIdentifier",
            "recipientAddressSource",
            "jobTemplate",
            "paymentDetails",
            "tags"
        ],
        "singleDocJobParams": [
            "documentSourceIdentifier",
            "recipientAddressSource",
            "jobTemplate",
            "paymentDetails",
            "tags"
        ],
        "submitMultiDocParams": [
            "documentSourceIdentifier",
            "recipientAddressSource",
            "jobTemplate",
            "paymentDetails",
            "tags"
        ],
        "mergeMultiDocParams": [
            "documentSourceIdentifier",
            "recipientAddressSource",
            "paymentDetails",
            "tags"
        ],
        "splitPdfParams": [
            "documentSourceIdentifier",
            "recipientAddressSource",
            "paymentDetails",
            "tags"
        ],
        "splitPdfWithCaptureParams": [
            "documentSourceIdentifier",
            "recipientAddressSource",
            "paymentDetails",
            "tags"
        ],
        "multiPdfWithCaptureParams": [
            "documentSourceIdentifier",
            "recipientAddressSource",
            "paymentDetails",
            "tags"
        ]
    }

    components = endpoint_components.get(endpoint)
    if not components:
        raise ValueError(f"Unknown endpoint: {endpoint}")

    options = [parse_component_options(c) for c in components]
    product = list(itertools.product(*options))

    results = []
    for combo in product:
        obj = {}
        for i, c in enumerate(components):
            obj[c] = combo[i]
        results.append(obj)

    return results


def save_permutations(endpoint, params_def, permutations):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, f"{endpoint}.json")

    output_data = {
        "endpoint": endpoint,
        "paramsDefinition": params_def,
        "permutations": permutations
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"✅ Generated {len(permutations)} permutations for {endpoint} → {output_file}")


def main():
    endpoints = parse_use_cases(EBNF_FILE)
    if not endpoints:
        print("❌ No endpoints found in EBNF file.")
        return

    print("=== Available Endpoints ===")
    endpoint_names = list(endpoints.keys())
    for i, ep in enumerate(endpoint_names, 1):
        print(f"{i}) {ep}")

    choice = int(input(f"Choose 1-{len(endpoint_names)}: "))
    endpoint = endpoint_names[choice - 1]
    params_def = endpoints[endpoint]

    perms = generate_permutations(endpoint)
    save_permutations(endpoint, params_def, perms)


if __name__ == "__main__":
    main()
