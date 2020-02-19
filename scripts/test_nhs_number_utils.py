"""
Tests for nhs_number_utils module
"""
import unittest
from nhs_number_utils import calculate_check_digit, nhs_number_is_valid

VALID_NHS_NUMBERS = (
    "4010232137",
    "9111231114",
    "9111231122",
    "9111231130",
    "9111231149",
    "9111231157",
)

INVALID_NHS_NUMBERS = (
    "9111111111",
    "9111111112",
    "9111111113",
    "9111111114",
    "1000000000",
)


class CheckDigitCalculatorTestCase(unittest.TestCase):
    """Test cases covering check digit validation"""

    def test_check_digits_calculate(self):
        """Check that the check digit is correct"""
        for number in VALID_NHS_NUMBERS:
            self.assertEqual(calculate_check_digit(number[:-1]), int(number[9]))

    def test_too_short_nhs_numbers_raise_exception(self):
        """Check that if the number is too short, an error is raised"""
        with self.assertRaisesRegex(ValueError, "Expecting nine digits"):
            calculate_check_digit("12345678")

    def test_too_long_nhs_numbers_raise_exception(self):
        """Check that if the number is too long, an error is raised"""
        with self.assertRaisesRegex(ValueError, "Expecting nine digits"):
            calculate_check_digit("1234567890")

    def test_providing_something_not_a_number_raises_exception(self):
        """Check that if the string is not numeric, an error is raised"""
        with self.assertRaisesRegex(ValueError, "nhs_number must comprise only digits"):
            calculate_check_digit("A")

    def test_invalid_nhs_number_detection(self):
        """Check that invalid nhs numbers will be rejected"""
        with self.assertRaisesRegex(ValueError, "Number is invalid"):
            calculate_check_digit("123456789")


class NhsNumberValidatorTestCase(unittest.TestCase):
    """Test cases covering NHS number validation"""

    def test_valid_numbers_validate(self):
        """Check that valid numbers validate"""
        for number in VALID_NHS_NUMBERS:
            self.assertTrue(nhs_number_is_valid(number))

    def test_invalid_nhs_numbers_are_detected(self):
        """Check that nvalid numbers don't validate"""
        for number in INVALID_NHS_NUMBERS:
            self.assertFalse(nhs_number_is_valid(number))

    def test_too_short_nhs_numbers_raise_exception(self):
        """Check that too short nhs numbers will raise an exception"""
        with self.assertRaisesRegex(ValueError, "Expecting ten digits"):
            nhs_number_is_valid("12345678")

    def test_too_long_nhs_numbers_raise_exception(self):
        """Check that too long nhs numbers will raise an exception"""
        with self.assertRaisesRegex(ValueError, "Expecting ten digits"):
            nhs_number_is_valid("12345678901")

    def test_providing_something_not_a_number_raises_exception(self):
        """Check that non-numeric nhs numbers will raise an exception"""
        with self.assertRaisesRegex(ValueError, "nhs_number must comprise only digits"):
            nhs_number_is_valid("A")
