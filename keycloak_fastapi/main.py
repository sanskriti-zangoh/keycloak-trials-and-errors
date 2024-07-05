# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from api.routers import (
#     auth_router,
# )
# from api.routers.keyauth import router as keyauth_router
from api.routers.myauth import router as myauth_router


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# app.include_router(auth_router)
# app.include_router(keyauth_router)
app.include_router(myauth_router)