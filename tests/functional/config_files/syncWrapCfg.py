from ...scripts.enviroment import EnvVarWrapper


ENV = EnvVarWrapper(
    **{
        "environment": "APIGEE_ENVIRONMENT",
        "test_patient_id": "TEST_PATIENT_ID",
        "auth_token_expiry_ms": "AUTH_TOKEN_EXPIRY_MS",
        "auth_token_expiry_ms_int": "AUTH_TOKEN_EXPIRY_MS_INT",
        "oauth_proxy": "OAUTH_PROXY",
        "oauth_base_uri": "OAUTH_BASE_URI",
        "pds_base_path": "PDS_BASE_PATH",
    }
)

CONFIG = {
    "ENVIRONMENT": ENV["environment"],
    "TEST_PATIENT_ID": ENV['test_patient_id'],
    "AUTH_TOKEN_EXPIRY_MS": (
        ENV['auth_token_expiry_ms'] if ENV["environment"] == "internal-dev" else ENV['auth_token_expiry_ms_int']
    ),
    "OAUTH_PROXY": ENV["oauth_proxy"],
    "OAUTH_BASE_URI": ENV["oauth_base_uri"],
    "BASE_URL": f"https://{ENV['environment']}.api.service.nhs.uk",
    "PDS_BASE_PATH": ENV["pds_base_path"]
}
