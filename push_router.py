"""
Router for push notification endpoints
"""
import time
import jwt
import httpx
from fastapi import APIRouter
from pydantic import BaseModel

# Create a router instance
router = APIRouter()

# These would typically come from a config file, but keeping them here for now
# to match your current structure
TEAM_ID = "U77SWC9NZT"
KEY_ID = "5XFZZ6ZD2H"
BUNDLE_ID = "com.stevenkim.CallClient"
VOIP_TOPIC = BUNDLE_ID + ".voip"
VOIP_DEVICE_TOKEN = "693e9a147dfb8ebbb5ed31eff419313d4af80607f63255dd673c61b33be1c1d7"
DEVICE_TOKEN = "486858be7798863889c2f4980cb4bbd27301e3916b0c8ce15839eea087f125d4"
P8_PRIVATE_KEY_PATH = "AuthKey_5XFZZ6ZD2H.p8"
APNS_HOST = "https://api.sandbox.push.apple.com"


class PushRequest(BaseModel):
    title: str = "테스트 푸시"
    body: str = "FastAPI에서 보낸 APNs 푸시입니다!"


class VoipPushRequest(BaseModel):
    ai_call_id: str | None = None


def _create_apns_jwt():
    """
    APNs용 JWT 생성 (1시간마다 새로 만드는게 권장)
    """
    with open(P8_PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()

    now = int(time.time())
    headers = {
        "alg": "ES256",
        "kid": KEY_ID,
    }
    payload = {
        "iss": TEAM_ID,
        "iat": now,
    }
    token = jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers=headers,
    )
    return token


@router.post("/push")
async def send_push(req: PushRequest):
    jwt_token = _create_apns_jwt()

    url = f"{APNS_HOST}/3/device/{DEVICE_TOKEN}"

    # APNs payload (알림 내용)
    payload = {
        "aps": {
            "alert": {
                "title": req.title,
                "body": req.body,
            },
            "sound": "default",
        }
    }

    headers = {
        "authorization": f"bearer {jwt_token}",
        "apns-topic": BUNDLE_ID,
    }

    async with httpx.AsyncClient(http2=True) as client:
        resp = await client.post(url, json=payload, headers=headers)
        return {
            "status_code": resp.status_code,
            "apns_id": resp.headers.get("apns-id"),
            "body": resp.text,
        }


@router.post("/voip-push")
async def send_voip_push(req: VoipPushRequest):
    jwt_token = _create_apns_jwt()
    url = f"{APNS_HOST}/3/device/{VOIP_DEVICE_TOKEN}"

    # VoIP 푸시는 보통 알림 UI를 쓰지 않고, content-available로 앱만 깨우는 패턴
    payload = {
        "aps": {
            "content-available": 1
        },
        "data": {
            "type": "ai_call",
            "ai_call_id": req.ai_call_id or "test"
        }
    }

    headers = {
        "authorization": f"bearer {jwt_token}",
        "apns-topic": VOIP_TOPIC,
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

