import httpx
from app.core.config import get_settings
from app.core.security import create_apns_jwt


class APNsService:
    """APNs 푸시 전송 서비스"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def send_alert_push(self, device_token: str, title: str, body: str) -> dict:
        """
        일반 알림 푸시 전송
        
        Args:
            device_token: APNs 디바이스 토큰
            title: 알림 제목
            body: 알림 내용
            
        Returns:
            dict: APNs 응답 (status_code, apns_id, body)
        """
        jwt_token = create_apns_jwt()
        url = f"{self.settings.apns_host}/3/device/{device_token}"
        
        payload = {
            "aps": {
                "alert": {
                    "title": title,
                    "body": body,
                },
                "sound": "default",
            }
        }
        
        headers = {
            "authorization": f"bearer {jwt_token}",
            "apns-topic": self.settings.BUNDLE_ID,
            "apns-push-type": "alert",
            "apns-priority": "10",
        }
        
        async with httpx.AsyncClient(http2=True) as client:
            resp = await client.post(url, json=payload, headers=headers)
            return {
                "status_code": resp.status_code,
                "apns_id": resp.headers.get("apns-id"),
                "body": resp.text,
            }
    
    async def send_voip_push(self, device_token: str, ai_call_id: str | None = None) -> dict:
        """
        VoIP 푸시 전송
        
        Args:
            device_token: VoIP 디바이스 토큰
            ai_call_id: AI 통화 ID (선택)
            
        Returns:
            dict: APNs 응답 (status_code, apns_id, body)
        """
        jwt_token = create_apns_jwt()
        url = f"{self.settings.apns_host}/3/device/{device_token}"
        
        # VoIP 푸시는 보통 알림 UI를 쓰지 않고, content-available로 앱만 깨우는 패턴
        payload = {
            "aps": {
                "content-available": 1
            },
            "data": {
                "type": "ai_call",
                "ai_call_id": ai_call_id or "test"
            }
        }
        
        headers = {
            "authorization": f"bearer {jwt_token}",
            "apns-topic": self.settings.voip_topic,
            "apns-push-type": "voip",
            "apns-priority": "10",
        }
        
        async with httpx.AsyncClient(http2=True) as client:
            resp = await client.post(url, json=payload, headers=headers)
            return {
                "status_code": resp.status_code,
                "apns_id": resp.headers.get("apns-id"),
                "body": resp.text,
            }

