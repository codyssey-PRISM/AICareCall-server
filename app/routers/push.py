from fastapi import APIRouter, Depends
from app.schemas.push import PushRequest, VoipPushRequest, PushResponse
from app.services.apns import APNsService
from app.core.config import get_settings

router = APIRouter(prefix="/push", tags=["push"])


def get_apns_service() -> APNsService:
    """의존성 주입용 APNs 서비스 팩토리"""
    return APNsService()


@router.post("/", response_model=PushResponse)
async def send_push(
    req: PushRequest,
    apns_service: APNsService = Depends(get_apns_service)
):
    """
    일반 알림 푸시 전송
    
    - **title**: 알림 제목
    - **body**: 알림 내용
    """
    settings = get_settings()
    return await apns_service.send_alert_push(
        device_token=settings.DEVICE_TOKEN,
        title=req.title,
        body=req.body
    )


@router.post("/voip", response_model=PushResponse)
async def send_voip_push(
    req: VoipPushRequest,
    apns_service: APNsService = Depends(get_apns_service)
):
    """
    VoIP 푸시 전송
    
    - **ai_call_id**: AI 통화 ID (선택)
    """
    settings = get_settings()
    return await apns_service.send_voip_push(
        device_token=settings.VOIP_DEVICE_TOKEN,
        ai_call_id=req.ai_call_id
    )

