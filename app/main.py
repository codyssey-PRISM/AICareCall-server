from fastapi import FastAPI
from app.routers import push, webhook, health
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="APNs Push Server",
    description="iOS APNs 푸시 + Vapi 웹훅 서버",
    version="1.0.0",
    debug=settings.DEBUG
)

# 라우터 등록
app.include_router(health.router)
app.include_router(push.router)
app.include_router(webhook.router)


# 서버 시작 시 로그
@app.on_event("startup")
async def startup_event():
    print("=" * 50)
    print("🚀 APNs Push Server Started")
    print(f"📱 APNs Environment: {settings.APNS_ENV}")
    print(f"🔗 APNs Host: {settings.apns_host}")
    print(f"📦 Bundle ID: {settings.BUNDLE_ID}")
    print(f"🎯 VoIP Topic: {settings.voip_topic}")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    print("\n👋 Server shutting down...")

