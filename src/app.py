from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from clerk_backend_api import Clerk, webhooks
import os

from .routes import challenge

# CORSMiddleware- making use frontend can send requests to backend

clerk_sdk= Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

app = FastAPI()

# allow_origins- Allowing any body to send requests to backend
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


app.include_router(challenge.router, prefix="/api")

# app.include_router(webhooks.router, prefix="/webhooks")
