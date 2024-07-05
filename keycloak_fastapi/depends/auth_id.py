from core.settings import load_settings, AuthSettings

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID


auth: AuthSettings = load_settings("AuthSettings")

# Read environment variables
# keycloak_server_url = os.getenv('KEYCLOAK_SERVER_URL', 'http://localhost:8080/auth/')
# client_id = os.getenv('KEYCLOAK_CLIENT_ID', 'your_client_id')
# realm_name = os.getenv('KEYCLOAK_REALM_NAME', 'your_realm_name')
# client_secret = os.getenv('KEYCLOAK_CLIENT_SECRET', 'your_client_secret')

# Configure Keycloak
keycloak_openid = KeycloakOpenID(
    server_url=auth.server_url,
    client_id=auth.keycloak_client_id,
    realm_name=auth.realm_name,
    client_secret_key=auth.keycloak_client_secret,
    verify=True
)