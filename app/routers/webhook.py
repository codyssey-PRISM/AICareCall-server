import json
from fastapi import APIRouter, Request

router = APIRouter(prefix="/vapi", tags=["webhook"])


@router.post("/webhook")
async def vapi_webhook(request: Request):
    """
    Vapi 웹훅 수신
    
    Vapi로부터 통화 관련 이벤트를 수신합니다.
    - status-update
    - transcript-update
    - end-of-call-report (통화 종료 시 전체 트랜스크립트)
    """
    body = await request.json()
    
    # 1) 전체 payload 출력 (디버깅용)
    print("\n===== RAW VAPI WEBHOOK =====")
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    message = body.get("message", {})
    message_type = message.get("type")
    
    # 2) end-of-call-report 일 때 transcript 출력
    if message_type == "end-of-call-report":
        transcript = message.get("transcript")
        
        # transcript가 다른 위치에 있을 수도 있음
        if not transcript:
            artifact = message.get("artifact") or {}
            transcript = artifact.get("transcript") or artifact.get("text")
        
        print("\n===== FULL CALL TRANSCRIPT =====")
        if transcript:
            print(transcript)
        else:
            print("⚠️ transcript 필드를 찾지 못함. RAW payload 구조를 확인하세요.")
    else:
        # 다른 타입은 일단 무시
        print(f"받은 message.type = {message_type} (현재는 무시)")
    
    # Vapi는 200 OK만 받으면 됨
    return {"ok": True}

