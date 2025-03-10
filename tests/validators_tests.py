import re

PHONE_REGEX = r"^\+?\s*(\(?\d{3}\)?)\s*[\s-]*\d{3}[\s-]*\d{4}\s*$"

phone_numbers = [
    "+1 (555) 123 4567",  # Valid
    "+1 555 123 4567",  # Valid
    "555 123 4567",  # Valid
    "(555) 123 4567",  # Valid
    "555  123 4567",  # Valid
    "555--123 4567",  # Valid
    "555-123 4567",  # Valid
    "555 123  4567",  # Valid
    "555 123-4567",  # Valid
    "1234567890",  # Valid
    "invalid",  # Invalid
    "+1(555)1234567", # Valid
    "+1 555-123-4567", # Valid
    "555 123 4567 ", # Valid
    "  555 123 4567", # Valid
    "+1 (555) 123 4567  ", #Valid - trailing spaces
    "  +1 (555) 123 4567", #Valid - leading spaces
    "+1(555)123 4567", # Valid -no spaces inside
    "+1 (555)1234567", #Valid - no spaces after parenthesis
    "+1(555) 1234567", #Valid - no spaces between codes
]


for number in phone_numbers:
    if re.match(PHONE_REGEX, number):
        print(f"{number} is a valid phone number.")
    else:
        print(f"{number} is not a valid phone number.")
