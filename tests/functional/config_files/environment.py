from ...scripts.enviroment import EnvVarWrapper


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
