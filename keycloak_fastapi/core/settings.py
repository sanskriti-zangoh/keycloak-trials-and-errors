"""
Settings Module.
"""

from functools import lru_cache
from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    """
    Database settings class.

    Attributes:
        url (str): Database URL.
        pool_size (int): Connection pool size.
        max_overflow (int): Max overflow.
        echo (bool): If True, print SQL statements. For debugging.
        pool_pre_ping (bool): If True, ping the database before each query.
        pool_recycle (int): Connection pool recycle time in seconds.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="DB_", case_sensitive=False, extra="ignore"
    )
    url: str
    pool_size: int
    max_overflow: int
    echo: bool
    pool_pre_ping: bool
    pool_recycle: int

class AuthSettings(BaseSettings):
    """
    Auth settings class.

    Attributes:
        server_url (str): Server URL.
        client_id (str): Client ID.
        realm_name (str): Realm name.
        client_secret (str): Client secret.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="AUTH_", case_sensitive=False, extra="ignore"
    )
    server_url: str
    realm_name: str
    keycloak_client_id: str
    keycloak_client_secret: str
    google_client_id: str
    google_client_secret: str
    github_client_id: str
    github_client_secret: str
    keycloak_client_url_id: str


@lru_cache
def load_settings(settings_cls_name: str) -> BaseSettings:
    """
    Load settings.

    Args:
        settings_cls_name (str): Settings class name.

    Returns:
        BaseSettings: Settings class.
    """
    load_dotenv(find_dotenv())
    settings_cls = globals()[settings_cls_name]
    return settings_cls()
