from ...scripts.environment import EnvVarWrapper


ENV = EnvVarWrapper(
    **{
        "environment": "APIGEE_ENVIRONMENT",
        "test_patient_id": "TEST_PATIENT_ID",
        "pds_base_path": "PDS_BASE_PATH",
    }
)

CONFIG = {
    "ENVIRONMENT": ENV["environment"],
    "TEST_PATIENT_ID": ENV['test_patient_id'],
    "PDS_BASE_PATH": ENV["pds_base_path"],
    "BASE_URL": f"https://{ENV['environment']}.api.service.nhs.uk",
}
