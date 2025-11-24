import json
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.call import CallService

router = APIRouter(prefix="/vapi", tags=["webhook"])

# 로그 디렉토리 설정
WEBHOOK_LOG_DIR = Path(__file__).parent.parent.parent / "data" / "webhook_logs"
WEBHOOK_LOG_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/webhook")
async def vapi_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Vapi 웹훅 수신 및 로그 저장
    
    Vapi로부터 통화 관련 이벤트를 수신합니다.
    - status-update: 통화 상태 변경
    - transcript: 실시간 대화 메시지
    - end-of-call-report: 통화 종료 시 전체 트랜스크립트
    
    모든 웹훅은 server/data/webhook_logs/ 디렉토리에 JSON 파일로 저장됩니다.
    """
    body = await request.json()
    
    # 이벤트 타입 추출
    message = body.get("message", {})
    message_type = message.get("type", "unknown")
    
    # 타임스탬프 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    # 로그 파일명 생성
    log_filename = f"{timestamp}_{message_type}.json"
    log_path = WEBHOOK_LOG_DIR / log_filename
    
    # 로그 파일 저장
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(body, f, indent=2, ensure_ascii=False)
    
    # 콘솔 출력
    print(f"\n{'='*60}")
    print(f"📥 VAPI WEBHOOK RECEIVED - {message_type}")
    print(f"⏰ Time: {datetime.now().isoformat()}")
    print(f"💾 Saved to: {log_filename}")
    print(f"{'='*60}")
    
    # 이벤트 타입별 주요 필드 출력
    if message_type == "status-update":
        status = message.get("status")
        call_id = message.get("call", {}).get("id") or body.get("call", {}).get("id")
        print(f"📞 Call ID: {call_id}")
        print(f"📊 Status: {status}")
    
    elif message_type == "transcript":
        role = message.get("role")
        transcript_text = message.get("transcript", {}).get("text") or message.get("text", "")
        print(f"🗣️ Role: {role}")
        print(f"💬 Text: {transcript_text[:100]}..." if len(transcript_text) > 100 else transcript_text)
    
    elif message_type == "end-of-call-report":
        call_id = message.get("call", {}).get("id") or body.get("call", {}).get("id")
        duration = message.get("durationSeconds")
        print(f"📞 Call ID: {call_id}")
        print(f"⏱️ Duration: {duration}s")
        
        # transcript 확인
        transcript = message.get("transcript")
        if transcript:
            print(f"📝 Transcript length: {len(str(transcript))} chars")
        else:
            print("⚠️ No transcript found")
        
        # DB에 저장 시도
        print(f"\n💾 Saving to database...")
        try:
            saved_call = await CallService.save_call_from_webhook(db, body)
            
            # messages 카운트는 body에서 직접 계산 (lazy load 방지)
            messages = body.get("message", {}).get("messages", [])
            user_bot_messages = [m for m in messages if m.get("role") in ["user", "bot"]]
            
            print(f"✅ Successfully saved to DB!")
            print(f"   - Call ID (DB): {saved_call.id}")
            print(f"   - Vapi Call ID: {saved_call.vapi_call_id}")
            print(f"   - Elder ID: {saved_call.elder_id}")
            print(f"   - Status: {saved_call.status}")
            print(f"   - Messages count: {len(user_bot_messages)}")
        except ValueError as e:
            print(f"⚠️ Validation error: {e}")
            print(f"   Call not saved to DB (missing elder_id or invalid data)")
        except Exception as e:
            print(f"❌ Error saving to DB: {e}")
            print(f"   Call logged to file but not saved to DB")
            # DB 에러 시 rollback
            await db.rollback()
    
    else:
        print(f"ℹ️ Unknown message type: {message_type}")
        print(f"📄 Full payload keys: {list(body.keys())}")
    
    print(f"{'='*60}\n")
    
    # Vapi는 200 OK만 받으면 됨 (에러 발생해도 200 반환)
    return {"ok": True, "logged": log_filename}

