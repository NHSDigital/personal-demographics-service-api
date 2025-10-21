
/**
 * Multiply a value by its position, using the NHS number strategy
 * @param {Number} digit the single-digit portion of the number
 * @param {Number} index The 0-indexed position of `digit` within the NHS number
 * @returns {Number} the result of the 'multiply by (11-position)' calculation
 **/
function multiplyByPosition(digit, index) {
    // multiple each digit by 11  minus its position (indexed from 1)
    return digit * (11 - (index+1));
}

/**
 * Add two values together. Useful for use in `reduce` calls
 * @param {Number} previousValue the initial value
 * @param {Number} currentValue the value to add to the initial value
 * @returns {Number} the sum of the two parameters
 **/
function addTogether(previousValue, currentValue){
    return previousValue + currentValue;
}

/**
 * Validate an NHS number
 * https://github.com/spikeheap/nhs-number-validator/blob/develop/index.js
 * 
 * @param {Number,  String} nhsNumber The NHS number to validate. This may be a String or a number.
 * @returns {Boolean} `true` IFF the NHS number validates, else `false`
 **/
function validate(nhsNumber){
    // pre-flight checks
    if(
      nhsNumber === undefined ||
      nhsNumber === null ||
      Number.isNaN(Number(nhsNumber)) ||
      nhsNumber.toString().length !== 10
    ){
      return false;
    }
  
    // convert numbers to strings, for internal consistency
    if(Number.isInteger(nhsNumber)){
      nhsNumber = nhsNumber.toString();
    }
  
    // Step 1: Multiply each of the first 9 numbers by (11 - position indexed from 1)
    // Step 2: Add the results together
    // Step 3: Divide the total by 11 to get the remainder
    const nhsNumberAsArray = nhsNumber.split('');
    const remainder = nhsNumberAsArray.slice(0,9)
                              .map(multiplyByPosition)
                              .reduce(addTogether, 0) % 11;

    let checkDigit = 11 - remainder;

    // replace 11 for 0
    if(checkDigit === 11){
      checkDigit = 0;
    }
  
    const providedCheckDigit = nhsNumberAsArray[9];

    // Do the check digits match?
    return checkDigit === Number(providedCheckDigit);
  }