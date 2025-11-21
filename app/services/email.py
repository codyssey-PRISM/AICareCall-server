"""이메일 전송 서비스 (Gmail SMTP)"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from app.core.config import get_settings

settings = get_settings()


async def send_auth_code_email(email: str, code: str) -> bool:
    """
    인증 코드 이메일 전송 (Gmail SMTP 비동기)
    
    Args:
        email: 수신자 이메일
        code: 6자리 인증 코드
        
    Returns:
        bool: 전송 성공 여부
    """
    try:
        # HTML 템플릿 로드
        template_path = Path(__file__).parent.parent / "templates" / "auth_code_email.html"
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # 코드 치환
        html_content = html_content.replace("{{CODE}}", code)
        
        # 이메일 메시지 생성
        message = MIMEMultipart("alternative")
        message["From"] = f"소리ai <{settings.EMAIL_FROM}>"
        message["To"] = email
        message["Subject"] = f"[소리ai] 인증 코드: {code}"
        
        # HTML 파트 추가
        html_part = MIMEText(html_content, "html", "utf-8")
        message.attach(html_part)
        
        # Gmail SMTP 서버로 비동기 전송
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            username=settings.EMAIL_FROM,
            password=settings.GMAIL_APP_PASSWORD,
            start_tls=True,
        )
        
        print(f"📧 Email sent successfully to {email}")
        print(f"   Code: {code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {email}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
