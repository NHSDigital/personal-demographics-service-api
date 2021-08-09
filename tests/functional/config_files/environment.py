import os


class EnvVarWrapper(object):
    """Dictionary-like interface for accessing environment variables.

    Values are lazy-loaded so need not exist when EnvVarWrapper is created.
    If the value points to a file on disk the contents are returned."""

    def __init__(self, **kwargs):
        """Supply keyword arguments specifying environment variables to wrap.
        """
        self._env = kwargs

    def __getitem__(self, key):
        environment_variable = self._env[key]
        value = os.environ[environment_variable]
        if os.path.isfile(value):
            with open(value) as f:
                file_content = f.read()
            if not file_content:
                raise RuntimeError("File appears to be empty")
            return file_content
        else:
            return value


ENV = EnvVarWrapper(
    **{
        "signing_key": "APPLICATION_RESTRICTED_SIGNING_KEY_PATH",
        "signing_key_with_asid": "APPLICATION_RESTRICTED_WITH_ASID_SIGNING_KEY_PATH",
        "application_restricted_api_key": "APPLICATION_RESTRICTED_API_KEY",
        "application_restricted_with_asid_api_key": "APPLICATION_RESTRICTED_WITH_ASID_API_KEY",
        "pds_base_path": "PDS_BASE_PATH",
        "environment": "APIGEE_ENVIRONMENT",
        "key_id": "KEY_ID",
        "client_id": "CLIENT_ID",
        "client_secret": "CLIENT_SECRET",
        "nhs_login_private_key": "ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH",
        "jwt_private_key": "JWT_PRIVATE_KEY_ABSOLUTE_PATH",
        "test_patient_id": "TEST_PATIENT_ID",
        "auth_token_expiry_ms": "AUTH_TOKEN_EXPIRY_MS",
        "auth_token_expiry_ms_int": "AUTH_TOKEN_EXPIRY_MS_INT"
    }
)
