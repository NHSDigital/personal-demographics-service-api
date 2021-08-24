from ...scripts.enviroment import EnvVarWrapper


ENV = EnvVarWrapper(
    **{
        "id_token_nhs_login_private_key_absolute_path": "ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH",
        "test_patient_id": "TEST_PATIENT_ID",
        "oauth_proxy": "OAUTH_PROXY",
        "oauth_base_uri": "OAUTH_BASE_URI",
        "environment": "APIGEE_ENVIRONMENT",
        "jwt_private_key_absolute_path": "JWT_PRIVATE_KEY_ABSOLUTE_PATH",
        "pds_base_path": "PDS_BASE_PATH",
    }
)

CONFIG = {
    "ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH": ENV["id_token_nhs_login_private_key_absolute_path"],
    "TEST_PATIENT_ID": ENV['test_patient_id'],
    "OAUTH_PROXY": ENV["oauth_proxy"],
    "OAUTH_BASE_URI": ENV["oauth_base_uri"],
    "BASE_URL": f"https://{ENV['environment']}.api.service.nhs.uk",
    "JWT_PRIVATE_KEY_ABSOLUTE_PATH": ENV["jwt_private_key_absolute_path"],
    "PDS_BASE_PATH": ENV["pds_base_path"],
}

