from ...scripts.environment import EnvVarWrapper


ENV = EnvVarWrapper(
    **{
        "oauth_proxy": "OAUTH_PROXY",
        "oauth_base_uri": "OAUTH_BASE_URI",
    }
)

CONFIG = {
    "OAUTH_PROXY": ENV["oauth_proxy"],
    "OAUTH_BASE_URI": ENV["oauth_base_uri"],
}
