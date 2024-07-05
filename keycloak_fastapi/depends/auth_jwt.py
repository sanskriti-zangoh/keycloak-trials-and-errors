from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from core.settings import load_settings, AuthSettings

from jwt import PyJWKClient
import jwt

auth: AuthSettings = load_settings("AuthSettings")

app = FastAPI()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/auth",
    tokenUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/token",
    refreshUrl=f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/token",
)


async def valid_access_token(
    access_token: str = Depends(oauth2_scheme)
):
    url = f"{auth.server_url}/realms/{auth.realm_name}/protocol/openid-connect/certs"
    optional_custom_headers = {"User-agent": "custom-user-agent"}
    jwks_client = PyJWKClient(url, headers=optional_custom_headers)

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        data = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=["RS256"],
            audience="open_id_client",
            options={"verify_exp": True},
        )
        return data
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Not authenticated")
