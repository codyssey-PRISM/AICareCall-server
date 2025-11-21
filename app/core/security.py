import time
import jwt
from app.core.config import get_settings


def create_apns_jwt() -> str:
    """
    APNs용 JWT 생성 (1시간마다 새로 만드는게 권장)
    
    Returns:
        str: APNs 인증용 JWT 토큰
    """
    settings = get_settings()
    
    with open(settings.P8_PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()
    
    now = int(time.time())
    headers = {
        "alg": "ES256",
        "kid": settings.KEY_ID,
    }
    payload = {
        "iss": settings.TEAM_ID,
        "iat": now,
    }
    
    token = jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers=headers,
    )
    return token

