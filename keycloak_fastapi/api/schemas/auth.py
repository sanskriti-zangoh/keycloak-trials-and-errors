from pydantic import (
    BaseModel, 
    EmailStr, 
    AnyHttpUrl
)

class SignUpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class ResponseUser(BaseModel):
    username: str
    name: str
    email: EmailStr
    pic: AnyHttpUrl

class SignUpResponse(BaseModel):
    message: str
    user: ResponseUser

class LoginPasswordRequest(BaseModel):
    email: EmailStr
    password: str

class LoginPasswordResponse(BaseModel):
    message: str
    user: ResponseUser

class LoginGoogleRequest(BaseModel):
    token: str

class LoginGoogleResponse(BaseModel):
    message: str
    user: ResponseUser

class LoginGithubRequest(BaseModel):
    token: str

class LoginGithubResponse(BaseModel):
    message: str
    user: ResponseUser

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: str
