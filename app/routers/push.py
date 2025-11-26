from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.push import PushRequest, VoipPushRequest, PushResponse
from app.services.apns import APNsService
from app.services.elder import ElderService
from app.core.config import get_settings
from app.db.session import get_db

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
    db: AsyncSession = Depends(get_db),
    apns_service: APNsService = Depends(get_apns_service)
):
    """
    VoIP 푸시 전송
    
    - **elder_id**: 어르신 ID (필수)
    - **ai_call_id**: AI 통화 ID (선택)
    """
    print(f"\n{'='*60}")
    print(f"📞 VoIP 푸시 전송 시작: elder_id={req.elder_id}")
    print(f"{'='*60}")
    
    # 어르신 정보 조회
    elder = await ElderService.get_elder_by_id(db=db, elder_id=req.elder_id)
    
    if not elder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"어르신을 찾을 수 없습니다. (elder_id: {req.elder_id})"
        )
    
    if not elder.voip_device_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"어르신의 VoIP 디바이스 토큰이 등록되지 않았습니다. (elder_id: {req.elder_id})"
        )
    
    print(f"✅ 어르신 정보: {elder.name}")
    print(f"📱 VoIP 토큰: {elder.voip_device_token[:20]}...{elder.voip_device_token[-20:]}")
    
    # VoIP 푸시 데이터 구성
    push_data = {
        "elder_id": elder.id,
        "elder_name": elder.name,
    }
    
    if req.ai_call_id:
        push_data["ai_call_id"] = req.ai_call_id
    
    result = await apns_service.send_voip_push(
        device_token=elder.voip_device_token,
        data=push_data
    )
    
    print(f"\n📬 APNs 응답:")
    print(f"  Status Code: {result['status_code']}")
    print(f"  APNs ID: {result['apns_id']}")
    print(f"  Body: {result['body'] if result['body'] else '(empty - success)'}")
    print(f"{'='*60}\n")
    
    return result

