function validate(nhsNumberInput) {
  if (nhsNumberInput === undefined || nhsNumberInput === null) {
    return false;
  }

  // Normalise input to a trimmed string
  const nhsNumberString = String(nhsNumberInput).trim();

  // NHS number must be exactly 10 digits
  if (!/^\d{10}$/.test(nhsNumberString)) {
    return false;
  }

  // Convert the string into an array of digits
  const digits = nhsNumberString.split('').map(Number);

  // Weighted sum of the first 9 digits
  const weightedSum = digits
    .slice(0, 9)
    .map((digit, index) => {
      const weight = 10 - index; // NHS spec: weights 10,9,8,...,2
      return digit * weight;
    })
    .reduce((sum, weightedValue) => sum + weightedValue, 0);

  const remainder = weightedSum % 11;
  const calculatedCheckDigit = (11 - remainder) % 11; // converts 11 → 0

  const providedCheckDigit = digits[9];

  return calculatedCheckDigit === providedCheckDigit;
}
