from ...scripts.environment import EnvVarWrapper


ENV = EnvVarWrapper(
    **{
        "signing_key": "APPLICATION_RESTRICTED_SIGNING_KEY_PATH",
        "application_restricted_api_key": "APPLICATION_RESTRICTED_API_KEY",
        "application_restricted_with_asid_api_key": "APPLICATION_RESTRICTED_WITH_ASID_API_KEY",
        "key_id": "KEY_ID",
    }
)

CONFIG = {
    "SIGNING_KEY": ENV["signing_key"],
    "APPLICATION_RESTRICTED_API_KEY": ENV["application_restricted_api_key"],
    "APPLICATION_RESTRICTED_WITH_ASID_API_KEY": ENV["application_restricted_with_asid_api_key"],
    "KEY_ID": ENV["key_id"],
}
