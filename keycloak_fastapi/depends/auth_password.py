# ./auth.py
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID # pip require python-keycloak
from core.settings import load_settings, AuthSettings
from fastapi import Security, HTTPException, status, Depends
from pydantic import Json
from database.models import Users

auth: AuthSettings = load_settings("AuthSettings")

# This is just for fastapi docs
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/auth",
    tokenUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/token",
    refreshUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/token",
)

# This actually does the auth checks
keycloak_openid = KeycloakOpenID(
    server_url=auth.server_url,
    client_id=auth.keycloak_client_id,
    realm_name=auth.realm_name,
    client_secret_key=auth.keycloak_client_secret,
    verify=True
)


async def get_idp_public_key():
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        f"{keycloak_openid.public_key()}"
        "\n-----END PUBLIC KEY-----"
    )

async def get_auth(token: str = Security(oauth2_scheme)) -> Json:
    try:
        return keycloak_openid.decode_token(
            token,
            key= await get_idp_public_key(),
            options={
                "verify_signature": True,
                "verify_aud": True,
                "exp": True
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e), # "Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    identity: Json = Depends(get_auth)
) -> dict:
    return identity # get your user form the DB using identity['sub']
    
