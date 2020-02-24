#!/usr/bin/env python3

"""
Python functions to generate [NHS Number](https://www.nhs.uk/using-the-nhs/about-the-nhs/what-is-an-nhs-number/)
check digits, or validate NHS Numbers.

Check digit generation algorithm is described here:
https://www.datadictionary.nhs.uk/data_dictionary/attributes/n/nhs/nhs_number_de.asp?shownav=1

Sean Kelly has an version implemented as a spreadsheet that can be used to generate 'valid' (but not real) NHS numbers
for testing purpoes. This was the source of the NHS numbers in the tests.

This is unused and provided as a convenience/reference implementation.
"""
import argparse


def calculate_check_digit(nhs_number: str) -> int:
    """Given a nine-digit NHS Number calculate the tenth check digit."""

    if not nhs_number.isdigit():
        raise ValueError("nhs_number must comprise only digits")
    if len(nhs_number) != 9:
        raise ValueError("Expecting nine digits")

    # https://www.datadictionary.nhs.uk/data_dictionary/attributes/n/nhs/nhs_number_de.asp?shownav=1
    digits_weighted = [int(v) for v in list(nhs_number)]
    for i in range(9):
        digits_weighted[i] = digits_weighted[i] * (10 - i)
    check_digit = 11 - (sum(digits_weighted) % 11)
    if check_digit == 11:
        check_digit = 0

    if check_digit == 10:
        raise ValueError("Number is invalid")

    return check_digit


def nhs_number_is_valid(nhs_number: str) -> bool:
    """Validate a full (ten-digit) NHS Number by recalculating the check digit."""

    if not nhs_number.isdigit():
        raise ValueError("nhs_number must comprise only digits")
    if len(nhs_number) != 10:
        raise ValueError("Expecting ten digits")

    return calculate_check_digit(nhs_number[:9]) == int(nhs_number[9])


def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(
        description="Validate NHS Numbers or generate check digit for a number"
    )
    parser.add_argument(
        "operation",
        help="generate a check digit given 9-digit prefix, or validate a 10-digit NHS number",
        choices=("generate", "validate"),
    )
    parser.add_argument("nhs_number", type=str)
    args = parser.parse_args()

    if args.operation == "generate":
        print(calculate_check_digit(args.nhs_number))
    elif args.operation == "validate":
        print(nhs_number_is_valid(args.nhs_number))


if __name__ == "__main__":
    main()
