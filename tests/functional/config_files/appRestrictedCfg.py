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
        "test_patient_id": "TEST_PATIENT_ID",
    }
)

CONFIG = {
    "BASE_URL": f"https://{ENV['environment']}.api.service.nhs.uk",
    "APPLICATION_RESTRICTED_API_KEY": ENV["application_restricted_api_key"],
    "SIGNING_KEY": ENV["signing_key"],
    "KEY_ID": ENV["key_id"],
    "PDS_BASE_PATH": ENV["pds_base_path"],
    "TEST_PATIENT_ID": ENV['test_patient_id'],
}

