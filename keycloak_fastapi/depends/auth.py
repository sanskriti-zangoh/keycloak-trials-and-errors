from core.settings import load_settings, AuthSettings

from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID, KeycloakAdmin
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from fastapi.responses import RedirectResponse


auth: AuthSettings = load_settings("AuthSettings")

router = APIRouter()

# Configure Keycloak
keycloak_openid = KeycloakOpenID(
    server_url=auth.server_url,
    client_id=auth.keycloak_client_id,
    realm_name=auth.realm_name,
    client_secret_key=auth.keycloak_client_secret,
    verify=True
)

keycloak_admin = KeycloakAdmin(
    server_url=auth.server_url,
    username="admin",
    password="admin",
    realm_name=auth.realm_name,
    client_id=auth.keycloak_client_id,
    client_secret_key=auth.keycloak_client_secret,
    verify=True
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_idp_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/auth",
    tokenUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/token",
    refreshUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/token"
)

oauth2_scheme_google = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/auth",
    tokenUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/token",
    refreshUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/token"
)

@router.get("/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "Authorization code not found in the callback URL"}

    # Exchange the authorization code for an access token
    token = await keycloak_openid.token(
        grant_type='authorization_code',
        code=code,
        redirect_uri="http://fastapi:5000/myauth/callback"
    )

    # You can now use the token to access userinfo or other protected resources
    userinfo = keycloak_openid.userinfo(token['access_token'])

    return {"access_token": token, "userinfo": userinfo}

@router.get("/login")
async def login():
    auth_url = keycloak_openid.auth_url(
        redirect_uri="http://fastapi:5000/myauth/callback",
        scope="openid email profile",
        state="random_state_string"
    )
    return RedirectResponse(auth_url)