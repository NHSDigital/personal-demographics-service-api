from ...scripts.environment import EnvVarWrapper


ENV = EnvVarWrapper(
    **{
        # This is only used to decide which auth_token_expiry to use
        "environment": "APIGEE_ENVIRONMENT",
        "auth_token_expiry_ms": "AUTH_TOKEN_EXPIRY_MS",
    }
)

CONFIG = {
    "AUTH_TOKEN_EXPIRY_MS": (
        ENV['auth_token_expiry_ms'] if ENV["environment"] == "internal-dev" else ENV['auth_token_expiry_ms_int']
    ),
}
