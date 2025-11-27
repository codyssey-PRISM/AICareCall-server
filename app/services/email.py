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
    
    DEBUG=True일 때는 실제 전송 없이 콘솔에만 출력
    
    Args:
        email: 수신자 이메일
        code: 6자리 인증 코드
        
    Returns:
        bool: 전송 성공 여부
    """
    try:
        # DEBUG 모드일 때는 콘솔에만 출력
        if settings.DEBUG:
            print("=" * 60)
            print("🔍 [DEBUG MODE] 이메일 전송 스킵 (콘솔 출력만)")
            print("=" * 60)
            print(f"📧 To: {email}")
            print(f"📝 Subject: [소리AI] 인증 코드: {code}")
            print(f"🔑 인증 코드: {code}")
            print("=" * 60)
            return True
        
        # 프로덕션: 실제 SendGrid로 전송
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


async def send_call_report_email(
    email: str,
    elder_name: str,
    call_id: int,
    elder_id: int,
    summary: str | None,
    emotion: str | None
) -> bool:
    """
    통화 리포트 이메일 전송 (SendGrid API)
    
    DEBUG=True일 때는 실제 전송 없이 콘솔에만 출력
    
    Args:
        email: 수신자 이메일 (보호자)
        elder_name: 어르신 이름
        call_id: 통화 ID
        elder_id: 어르신 ID
        summary: 통화 요약
        emotion: 감정 상태
        
    Returns:
        bool: 전송 성공 여부
    """
    try:
        # 감정 상태 매핑
        emotion_map = {
            "calm": ("평온", "calm"),
            "happy": ("행복", "happy"),
            "sad": ("슬픔", "sad"),
            "anxious": ("불안", "anxious"),
            "worried": ("걱정", "anxious"),
        }
        
        emotion_text, emotion_class = emotion_map.get(
            emotion.lower() if emotion else "",
            ("알 수 없음", "neutral")
        )
        
        # URL 생성
        call_detail_url = f"{settings.WEB_URL}/call-list/{elder_id}/{call_id}"
        dashboard_url = f"{settings.WEB_URL}/dashboard/{elder_id}"
        
        # 요약이 없으면 기본 메시지
        summary_text = summary if summary else "통화 요약을 생성하지 못했습니다. 자세한 내용은 통화 상세 페이지에서 확인하세요."
        
        # DEBUG 모드일 때는 콘솔에만 출력
        if settings.DEBUG:
            print("=" * 60)
            print("🔍 [DEBUG MODE] 통화 리포트 이메일 전송 스킵 (콘솔 출력만)")
            print("=" * 60)
            print(f"📧 To: {email}")
            print(f"📝 Subject: [소리AI] {elder_name}님과의 통화가 완료되었습니다")
            print(f"👤 어르신: {elder_name}")
            print(f"💭 감정: {emotion_text}")
            print(f"📄 요약: {summary_text[:100]}...")
            print(f"🔗 통화 상세: {call_detail_url}")
            print(f"🔗 대시보드: {dashboard_url}")
            print("=" * 60)
            return True
        
        # 프로덕션: 실제 SendGrid로 전송
        # HTML 템플릿 로드
        template_path = Path(__file__).parent.parent / "templates" / "call_report_email.html"
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # 템플릿 변수 치환
        html_content = html_content.replace("{{ELDER_NAME}}", elder_name)
        html_content = html_content.replace("{{EMOTION_TEXT}}", emotion_text)
        html_content = html_content.replace("{{EMOTION_CLASS}}", emotion_class)
        html_content = html_content.replace("{{SUMMARY}}", summary_text)
        html_content = html_content.replace("{{CALL_DETAIL_URL}}", call_detail_url)
        html_content = html_content.replace("{{DASHBOARD_URL}}", dashboard_url)
        
        # SendGrid 메시지 생성
        message = Mail(
            from_email=Email(settings.EMAIL_FROM),
            to_emails=To(email),
            subject=f"[소리AI] {elder_name}님과의 통화가 완료되었습니다",
            html_content=Content("text/html", html_content)
        )
        
        # SendGrid API 클라이언트 생성 및 전송
        # SendGrid는 동기 API이므로 asyncio.to_thread로 비동기 처리
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = await asyncio.to_thread(sg.send, message)
        
        print(f"📧 Call report email sent successfully to {email}")
        print(f"   Elder: {elder_name}")
        print(f"   Call ID: {call_id}")
        print(f"   SendGrid Status: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send call report email to {email}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
