#!/usr/bin/env python3

# Test the RandomDataGenerator
import sys
sys.path.insert(0, '/Users/frankserrao/Dropbox/Customers/c2m/projects/c2m-api/C2M_API_v3/c2m-api-repo/scripts/test_data_genertor')

from add_examples import RandomDataGenerator

# Create generator
gen = RandomDataGenerator()

# Test string generation
print("=== String Generation ===")
print(f"Generic string: {gen.generate_string()}")
print(f"Email: {gen.generate_string('email')}")
print(f"Email 2: {gen.generate_string('userEmail')}")
print(f"Name: {gen.generate_string('name')}")
print(f"First Name: {gen.generate_string('firstName')}")
print(f"ID: {gen.generate_string('userId')}")
print(f"Description: {gen.generate_string('description')}")
print(f"URL: {gen.generate_string('websiteUrl')}")
print(f"Date: {gen.generate_string('createdDate')}")
print(f"Phone: {gen.generate_string('phoneNumber')}")

print("\n=== Integer Generation ===")
print(f"Generic integer: {gen.generate_integer()}")
print(f"Age: {gen.generate_integer('age')}")
print(f"ID: {gen.generate_integer('id')}")
print(f"Quantity: {gen.generate_integer('quantity')}")
print(f"Year: {gen.generate_integer('year')}")

print("\n=== Number Generation ===")
print(f"Generic number: {gen.generate_number()}")
print(f"Price: {gen.generate_number('price')}")
print(f"Rate: {gen.generate_number('interestRate')}")
print(f"Weight: {gen.generate_number('weight')}")

print("\n=== Boolean Generation ===")
print(f"Generic boolean: {gen.generate_boolean()}")
print(f"Active: {gen.generate_boolean('isActive')}")
print(f"Deleted: {gen.generate_boolean('isDeleted')}")
print(f"Enabled: {gen.generate_boolean('enabled')}")

print("\n=== Multiple Calls (Uniqueness Test) ===")
for i in range(5):
    print(f"Email {i+1}: {gen.generate_string('email')}")