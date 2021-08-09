import os


# Configure Test Environment
def get_env(variable_name: str) -> str:
    """Returns a environment variable"""
    try:
        var = os.environ[variable_name]
        if not var:
            raise RuntimeError(f"Variable is null, Check {variable_name}.")
        return var
    except KeyError:
        raise RuntimeError(f"Variable is not set, Check {variable_name}.")


def get_env_file(variable_name: str) -> str:
    """Returns a environment variable as path"""
    try:
        path = os.path.abspath(os.environ[variable_name])
        if not path:
            raise RuntimeError(f"Variable is null, Check {variable_name}.")
        with open(path, "r") as f:
            contents = f.read()
        if not contents:
            raise RuntimeError(f"Contents of file empty. Check {variable_name}.")
        return contents
    except KeyError:
        raise RuntimeError(f"Variable is not set, Check {variable_name}.")


ENV = {
    "signing_key": get_env_file("APPLICATION_RESTRICTED_SIGNING_KEY_PATH"),
    "signing_key_with_asid": get_env_file("APPLICATION_RESTRICTED_WITH_ASID_SIGNING_KEY_PATH"),
    "application_restricted_api_key": get_env("APPLICATION_RESTRICTED_API_KEY"),
    "application_restricted_with_asid_api_key": get_env("APPLICATION_RESTRICTED_WITH_ASID_API_KEY"),
    "pds_base_path": get_env("PDS_BASE_PATH"),
    "environment": get_env("APIGEE_ENVIRONMENT"),
    "key_id": get_env("KEY_ID"),
    'client_id': get_env('CLIENT_ID'),
    'client_secret': get_env('CLIENT_SECRET'),
    'nhs_login_private_key': get_env('ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH'),
    'jwt_private_key': get_env('JWT_PRIVATE_KEY_ABSOLUTE_PATH'),
    'test_patient_id': get_env('TEST_PATIENT_ID'),
}
