const Boom = require('boom');

const mockSpinePollingErrors = {
    // When polling an id, a message was found to be in a failed state
    422: () => {
        throw Boom.badData(
            "An internal polling message ID was found however the processing of the request failed" +
            " in an unexpected way or was cancelled, so the update failed. Please raise these occurrences with our team (via https://digital.nhs.uk/developer/help-and-support)" +
            " so we can investigate the issue. When raising, quote the message ID.",
            {
                operationOutcomeCode: "processing",
                apiErrorCode: "POLLING_MESSAGE_FAILURE",
                display: "The polling id was found however the processing of the request failed in an unexpected way or was cancelled"
            })
    }
};

/**
 *  Checks if the environment is local or internal-dev
 * @returns {Boolean}
 */
const isInternalDevOrLocal = () => {
    if("VERSION_INFO" in process.env){
        const versionInfo = JSON.parse(process.env.VERSION_INFO);
        return /internal-dev/.test(JSON.stringify(versionInfo.apigee_base_uri)) ? true : false;
    } else {
        return true;
    }
}

/**
 * Simulate a spine polling error based on the error code passed in
 * Works on local and internal-dev only
 * @param {String} errorCode
 */
const simulateSpinePollingError = (errorCode) => {
    if (isInternalDevOrLocal()) {
        errorCode in mockSpinePollingErrors && mockSpinePollingErrors[errorCode]();
    }
};

exports.simulateSpinePollingError = simulateSpinePollingError;
