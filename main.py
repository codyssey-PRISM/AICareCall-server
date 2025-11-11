from fastapi import FastAPI
from routers import push, register_callee

app = FastAPI()
app.include_router(push.router)
app.include_router(register_callee.router)

@app.get("/")
def health():
    return {"status": "ok"}