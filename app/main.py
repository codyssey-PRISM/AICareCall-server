from fastapi import FastAPI
from app.routers import push, webhook, health, elders, auth, elder_app, dashboard
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.scheduler.scheduler import start_scheduler, shutdown_scheduler
from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()

app = FastAPI(
    title="APNs Push Server",
    description="iOS APNs 푸시 + Vapi 웹훅 서버",
    version="1.0.0",
    debug=settings.DEBUG
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://sori-call.vercel.app",
    "https://ai-care-call-web.vercel.app",  # 실제 배포 URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # or ["*"] (개발 중에는 편하게)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(push.router)
app.include_router(webhook.router)
app.include_router(elders.router)
app.include_router(elder_app.router)
app.include_router(dashboard.router)


# 서버 시작 시 로그
@app.on_event("startup")
async def startup_event():
    # DB 테이블 생성 (개발 편의용 - 프로덕션에서는 alembic 사용 권장)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("=" * 50)
    print("🚀 APNs Push Server Started")
    print(f"📱 APNs Environment: {settings.APNS_ENV}")
    print(f"🔗 APNs Host: {settings.apns_host}")
    print(f"📦 Bundle ID: {settings.BUNDLE_ID}")
    print(f"🎯 VoIP Topic: {settings.voip_topic}")
    print(f"🗄️  Database: {settings.DATABASE_URL}")
    print("=" * 50)
    
    # 스케줄러 시작
    start_scheduler()
    print("⏰ Scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    print("\n👋 Server shutting down...")
    
    # 스케줄러 종료
    shutdown_scheduler()
    print("⏰ Scheduler stopped")

