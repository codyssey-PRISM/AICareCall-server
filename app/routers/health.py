from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/")
def health():
    """기본 헬스체크 엔드포인트"""
    return {"status": "ok"}


@router.get("/health")
def health_check():
    """
    상세 헬스체크
    
    서버 상태 및 설정 정보를 반환합니다.
    """
    settings = get_settings()
    return {
        "status": "healthy",
        "service": "APNs Push Server",
        "apns_environment": settings.APNS_ENV,
        "apns_host": settings.apns_host,
        "bundle_id": settings.BUNDLE_ID,
    }

