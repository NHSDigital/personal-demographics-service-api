import os


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
    "service_base_path": get_env("SERVICE_BASE_PATH"),
    "environment": get_env("APIGEE_ENVIRONMENT"),
    "container_ip": get_env("CONTAINER_IP"),
}
