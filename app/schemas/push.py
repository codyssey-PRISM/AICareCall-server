from pydantic import BaseModel


class PushRequest(BaseModel):
    """일반 알림 푸시 요청 모델"""
    title: str = "테스트 푸시"
    body: str = "FastAPI에서 보낸 APNs 푸시입니다!"


class VoipPushRequest(BaseModel):
    """VoIP 푸시 요청 모델"""
    ai_call_id: str | None = None


class PushResponse(BaseModel):
    """푸시 전송 응답 모델"""
    status_code: int
    apns_id: str | None
    body: str

