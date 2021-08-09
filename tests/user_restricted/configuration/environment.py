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
        # Apigee
        "environment": "APIGEE_ENVIRONMENT",
        # PDS
        "pds_base_path": "PDS_BASE_PATH",
        # OAUTH
        "client_id": "CLIENT_ID",
        "client_secret": "CLIENT_SECRET",
        "redirect_uri": "REDIRECT_URI",
        "authenticate_url": "AUTHENTICATE_URL",
        "test_patient_id": "TEST_PATIENT_ID",
    }
)
