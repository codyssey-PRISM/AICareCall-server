import time
import jwt  # pyjwt
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from push_router import router as push_router
from vapi_router import router as vapi_router

app = FastAPI()
app.include_router(push_router)
app.include_router(vapi_router)

@app.get("/")
def health():
    return {"status": "ok"}