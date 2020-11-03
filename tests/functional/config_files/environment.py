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


def get_env_path(variable_name: str) -> str:
    """Returns a environment variable as path"""
    try:
        var = os.path.abspath(os.environ[variable_name])
        if not var:
            raise RuntimeError(f"Variable is null, Check {variable_name}.")
        return var
    except KeyError:
        raise RuntimeError(f"Variable is not set, Check {variable_name}.")


ENV = {
    "unattended_access_signing_key_path": get_env_path("UNATTENDED_ACCESS_SIGNING_KEY_PATH"),
    "unattended_access_api_key": get_env("UNATTENDED_ACCESS_API_KEY"),
    "pds_base_path": get_env("PDS_BASE_PATH"),
    "environment": get_env("APIGEE_ENVIRONMENT"),
    "key_id": get_env("KEY_ID")
}
