from ...scripts.environment import EnvVarWrapper


ENV = EnvVarWrapper(
    **{
        "id_token_nhs_login_private_key_absolute_path": "ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH",
        "jwt_private_key_absolute_path": "JWT_PRIVATE_KEY_ABSOLUTE_PATH",
        "client_id": "CLIENT_ID",
        "client_secret": "CLIENT_SECRET",
        "redirect_uri": "REDIRECT_URI",
    }
)

CONFIG = {
    "ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH": ENV["id_token_nhs_login_private_key_absolute_path"],
    "JWT_PRIVATE_KEY_ABSOLUTE_PATH": ENV["jwt_private_key_absolute_path"],
    "CLIENT_ID": ENV['client_id'],
    "CLIENT_SECRET": ENV['client_secret'],
    "REDIRECT_URI": ENV['redirect_uri'],
}
