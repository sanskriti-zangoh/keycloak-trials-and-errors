from keycloak import KeycloakOpenID, KeycloakAdmin, KeycloakOpenIDConnection
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer

from fastapi import HTTPException
from keycloak.exceptions import KeycloakAuthenticationError
from jwt import PyJWKClient
import jwt

from core.settings import load_settings, AuthSettings
auth: AuthSettings = load_settings("AuthSettings")

keycloak_connection = KeycloakOpenIDConnection(
                        server_url="http://keycloak:8080",
                        username='admin',
                        password='admin',
                        realm_name="keyauth",
                        user_realm_name="master",
                        client_id="admin-cli",
                        verify=True)

keycloak_admin = KeycloakAdmin(connection=keycloak_connection)

keycloak_openid = KeycloakOpenID(
    server_url="http://keycloak:8080",
    client_id="open_id_client",
    realm_name="keyauth",
    client_secret_key="iBIGHeORlxkTvuTM1Ef81ZbMsistOL5f",
    verify=True)

oauth2_idp_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/auth",
    tokenUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/token",
    refreshUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/token"
)

router = APIRouter(prefix="/myauth", tags=["myauth"])

async def get_current_user(token: str = Depends(oauth2_idp_scheme)):
    try:
        user_info = keycloak_openid.userinfo(token)
        return user_info
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    
async def get_token_saml_user(token: str = Depends(oauth2_idp_scheme)):
    pass

class User(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str


@router.post("/signup")
async def signup(user: User):
    """Signup route to create a new user"""
    try:
        user_id = keycloak_admin.create_user({
            "username": user.username,
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "enabled": True,
            "credentials": [{"type": "password", "value": f"{user.password}", "temporary": False},],
        },
        exist_ok=False)
        return {"user_id": user_id}
    except KeycloakAuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return user

@router.get("/logout")
async def logout(user: dict = Depends(get_current_user)):
    try: 
        keycloak_openid.logout(user['access_token'])
        return {"status": "Logged out"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    