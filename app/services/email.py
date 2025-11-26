"""이메일 전송 서비스 (SendGrid)"""
import asyncio
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from pathlib import Path
from app.core.config import get_settings

settings = get_settings()


async def send_auth_code_email(email: str, code: str) -> bool:
    """
    인증 코드 이메일 전송 (SendGrid API)
    
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
        
        # SendGrid 메시지 생성
        message = Mail(
            from_email=Email(settings.EMAIL_FROM),
            to_emails=To(email),
            subject=f"[소리AI] 인증 코드: {code}",
            html_content=Content("text/html", html_content)
        )
        
        # SendGrid API 클라이언트 생성 및 전송
        # SendGrid는 동기 API이므로 asyncio.to_thread로 비동기 처리
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = await asyncio.to_thread(sg.send, message)
        
        print(f"📧 Email sent successfully to {email}")
        print(f"   Code: {code}")
        print(f"   SendGrid Status: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {email}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
