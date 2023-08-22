import os


def api_env() -> str:
    env = os.environ.get('APIGEE_ENVIRONMENT', 'internal-dev').strip().lower()
    return env


def api_base_domain() -> str:
    env = os.environ.get('API_BASE_DOMAIN', 'api.service.nhs.uk').strip().lower()
    return env


def api_host(
        env: str = None,  base_domain: str = None
) -> str:
    env = (env or api_env()).strip().lower()
    base_domain = (base_domain or api_base_domain()).strip().lower()
    host = (base_domain if env == 'prod' else f'{env}.{base_domain}').lower().strip()
    return host


def api_base_path() -> str:
    base_path = os.environ.get('SERVICE_BASE_PATH', '').strip().strip('/')
    return base_path


def api_base_uri(
        host: str = None,  env: str = None,  base_path: str = None, base_domain: str = None
) -> str:

    env = (env or api_env()).strip().lower()
    base_path = (base_path or api_base_path()).strip().strip('/')
    host = (host or api_host(env=env, base_domain=base_domain)).lower().strip().strip('/')
    base_uri = os.path.join(f"https://{host}", base_path)
    return base_uri


def source_commit_id():
    return os.environ.get('SOURCE_COMMIT_ID', 'not-set')


def status_endpoint_api_key():
    return os.environ.get('STATUS_ENDPOINT_API_KEY', 'not-set')
