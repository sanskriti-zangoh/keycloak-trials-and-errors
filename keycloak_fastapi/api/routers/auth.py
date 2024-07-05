from fastapi import APIRouter, Depends, HTTPException, Request
from api.schemas import Token, User
from fastapi.security import OAuth2PasswordRequestForm
from depends.auth import keycloak_openid, keycloak_admin, auth
from keycloak.exceptions import KeycloakAuthenticationError

router = APIRouter(prefix="/auth", tags=["auth"])
from pydantic import BaseModel




# @router.get("/secure-endpoint")
# async def secure_endpoint(current_user: dict = Depends(valid_access_token)):
#     return {"message": "Secure content", "user": current_user}


@router.post("/login/password")
async def login_password():
    return {"message": "Login with password"}

@router.post("/login/google")
async def login_google():
    return {"message": "Login with google"}

@router.post("/login/github")
async def login_github():
    return {"message": "Login with github"}

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login route for username and password"""
    try:
        token = keycloak_openid.token(form_data.username, form_data.password)
        return token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
@router.post("/signup")
async def signup(user: User):
    """Signup route to create a new user"""
    try:
        user_id = keycloak_admin.create_user({
            "username": user.username,
            "email": user.email,
            "enabled": True,
            "credentials": [{"type": "password", "value": "defaultpassword", "temporary": False}]
        })
        return {"user_id": user_id}
    except KeycloakAuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
