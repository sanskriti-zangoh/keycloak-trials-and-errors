import os
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import httpx
from jose import JWTError, jwt

router = APIRouter(prefix="/keyauth", tags=["keyauth"])

# Environment variables
AUTH_SERVER_URL = os.getenv('AUTH_SERVER_URL')
AUTH_REALM_NAME = os.getenv('AUTH_REALM_NAME')
AUTH_KEYCLOAK_CLIENT_ID = os.getenv('AUTH_KEYCLOAK_CLIENT_ID')
AUTH_KEYCLOAK_CLIENT_SECRET = os.getenv('AUTH_KEYCLOAK_CLIENT_SECRET')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{AUTH_SERVER_URL}/realms/{AUTH_REALM_NAME}/protocol/openid-connect/token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

# Helper function to get a token

async def get_token(username: str, password: str):
    url = "http://keycloak:8080/realms/keyauth/protocol/openid-connect/token"
    payload = {
        'client_id': 'open_id_client',
        'client_secret': 'your_client_secret',
        'grant_type': 'password',
        'username': username,
        'password': password
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try: 
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, headers=headers)  # Await the async post request
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

# Helper function to verify a token
def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, AUTH_KEYCLOAK_CLIENT_SECRET, algorithms=["RS256"])
        username: str = payload.get("preferred_username")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)

# Authentication endpoint
@router.post("/token", response_model=Token)
async def login(username: str, password: str):
    token = await get_token(username, password)
    return Token(access_token=token["access_token"], token_type="bearer")

# Protected endpoint
@router.get("/users/me", response_model=TokenData)
async def read_users_me(current_user: TokenData = Depends(get_current_user)):
    return current_user

# Registration endpoint (this would typically be done via Keycloak directly)
@router.post("/register")
async def register(username: str, password: str, email: str, first_name: str, last_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVER_URL}/admin/realms/{AUTH_REALM_NAME}/users",
            json={
                "username": username,
                "enabled": True,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "credentials": [{"type": "password", "value": password, "temporary": False}]
            },
            headers={"Authorization": f"Bearer {await get_admin_token()}"}
        )
        response.raise_for_status()
        return {"status": "User created"}

async def get_admin_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVER_URL}/realms/{AUTH_REALM_NAME}/protocol/openid-connect/token",
            data={
                'grant_type': 'client_credentials',
                'client_id': AUTH_KEYCLOAK_CLIENT_ID,
                'client_secret': AUTH_KEYCLOAK_CLIENT_SECRET,
            }
        )
        response.raise_for_status()
        return response.json()["access_token"]

# Logout endpoint (revoking tokens via Keycloak)
@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVER_URL}/realms/{AUTH_REALM_NAME}/protocol/openid-connect/logout",
            data={'client_id': AUTH_KEYCLOAK_CLIENT_ID, 'client_secret': AUTH_KEYCLOAK_CLIENT_SECRET, 'refresh_token': token}
        )
        response.raise_for_status()
        return {"status": "Logged out"}
