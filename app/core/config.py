from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Apple APNs
    TEAM_ID: str
    KEY_ID: str
    BUNDLE_ID: str
    P8_PRIVATE_KEY_PATH: str
    
    # 디바이스 토큰 (개발용, 실제로는 DB에서 관리)
    DEVICE_TOKEN: str
    VOIP_DEVICE_TOKEN: str
    
    # APNs 환경
    APNS_ENV: str = "sandbox"  # sandbox or production
    
    # 서버 설정
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"
    # PostgreSQL로 전환 시: postgresql+asyncpg://user:password@localhost/dbname
    
    # Email (Gmail SMTP)
    EMAIL_FROM: str
    GMAIL_APP_PASSWORD: str
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    
    @property
    def voip_topic(self) -> str:
        """VoIP 토픽 = Bundle ID + .voip"""
        return f"{self.BUNDLE_ID}.voip"
    
    @property
    def apns_host(self) -> str:
        """APNs 서버 호스트 (환경에 따라 분기)"""
        if self.APNS_ENV == "production":
            return "https://api.push.apple.com"
        return "https://api.sandbox.push.apple.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """싱글톤 패턴으로 설정 객체 반환"""
    return Settings()

