from ...scripts.enviroment import EnvVarWrapper


ENV = EnvVarWrapper(
    **{
        "pds_base_path": "PDS_BASE_PATH",
        "environment": "APIGEE_ENVIRONMENT",
        "oauth_proxy": "OAUTH_PROXY",
        "oauth_base_uri": "OAUTH_BASE_URI",
        "test_patient_id": "TEST_PATIENT_ID",
    }
)

CONFIG = {
    "BASE_URL": f"https://{ENV['environment']}.api.service.nhs.uk",
    "PDS_BASE_PATH": ENV["pds_base_path"],
    "ENVIRONMENT": ENV["environment"],
    "OAUTH_PROXY": ENV["oauth_proxy"],
    "OAUTH_BASE_URI": ENV["oauth_base_uri"],
    "TEST_PATIENT_ID": ENV['test_patient_id'],
}

