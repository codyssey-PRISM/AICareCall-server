from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.elder import ElderService
from app.services.apns import APNsService
from app.db.models.elder import Elder
from app.db.models.call import Call
from app.db.models.call_message import CallMessage
from app.core.config import get_settings


class CallService:

    SETTINGS = get_settings()

    REQUIRED_QUESTIONS_TEMPLATE = {
        "meal": "Meals – Ask whether they have eaten today.\nExample: 오늘 식사는 하셨어요?",
        "medication": "Medications – Ask whether they have taken their medications today.\nExample: 오늘 약을 먹으셨어요?",
        "emotion": "Emotions – Ask how they are feeling today.\nExample: 오늘 기분이 어때요?",
        "special_event": "Special Events – Ask about any special events or plans they have for the day.\nExample: 오늘 특별한 일이 있으신가요?",
        "additional_info": "Personalized – Ask about the following topic:"
    }

    MAX_CALL_DURATION_SECONDS = 1200  # 20 minutes
    ANALYSIS_TIMEOUT_SECONDS = 30

    @staticmethod
    async def initiate_call(db: AsyncSession, elder_id: int):
        elder = await ElderService.get_elder_by_id(db, elder_id)
        if not elder:
            raise ValueError(f"어르신을 찾을 수 없습니다. (elder_id: {elder_id})")
        
        if not elder.voip_device_token:
            raise ValueError(f"어르신의 디바이스가 등록되지 않았습니다. (elder_id: {elder_id})")
        
        # VoIP push에는 최소 정보만 전달
        # iOS 앱이 받아서 /elder-app/assistant-config API를 호출하여 전체 config 가져감
        push_data = {
            "elder_id": elder.id,
            "elder_name": elder.name,
            "call_type": "scheduled"
        }
        
        apns_response = await APNsService.send_voip_push(elder.voip_device_token, push_data)
        return apns_response
    
    @staticmethod
    async def get_assistant_config(elder: Elder) -> dict:
        """
        Elder 정보를 기반으로 Vapi Assistant 설정 생성
        
        Args:
            db: 데이터베이스 세션
            elder_id: 어르신 ID
            
        Returns:
            Vapi Assistant 설정 딕셔너리
            
        Raises:
            ValueError: 어르신을 찾을 수 없거나 디바이스가 등록되지 않은 경우
        """

        system_prompt = CallService._build_system_prompt(elder)
        summary_plan = CallService._build_summary_plan()
        structured_data_plan = CallService._build_structured_data_plan()

        assistant = {
            "voice": {
                "provider": "openai",
                "voiceId": "echo",
                "model": "tts-1"
            },
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_prompt}
                ]
            },
            "transcriber": {
                "model": "nova-2",
                "language": "ko",
                "provider": "deepgram"
            },
            "firstMessageMode": "assistant-speaks-first-with-model-generated-message",
            "endCallFunctionEnabled": True,
            "endCallMessage": "그럼 통화는 이렇게 마무리하고, 다음에 또 전화드리겠습니다.",
            "serverMessages": ["end-of-call-report"],
            "maxDurationSeconds": CallService.MAX_CALL_DURATION_SECONDS,
            "analysisPlan": {
                "minMessagesThreshold": 1,
                "summaryPlan": summary_plan,
                "structuredDataPlan": structured_data_plan
            },
            "server": {
                "url": CallService.SETTINGS.SERVER_URL,
            }
        }
        
        return assistant
    
    @staticmethod
    def _build_required_questions(elder: Elder) -> list[str]:
        """Elder의 설정에 따라 필수 질문 리스트 생성"""
        questions = []
        
        if elder.ask_meal:
            questions.append(CallService.REQUIRED_QUESTIONS_TEMPLATE["meal"])
        
        if elder.ask_medication:
            questions.append(CallService.REQUIRED_QUESTIONS_TEMPLATE["medication"])
        
        if elder.ask_emotion:
            questions.append(CallService.REQUIRED_QUESTIONS_TEMPLATE["emotion"])
        
        if elder.ask_special_event:
            questions.append(CallService.REQUIRED_QUESTIONS_TEMPLATE["special_event"])
        
        if elder.additional_info:
            questions.append(
                CallService.REQUIRED_QUESTIONS_TEMPLATE["additional_info"] + " " + elder.additional_info
            )
        
        return questions
    
    @staticmethod
    def _build_client_information(elder: Elder) -> str:
        """Elder 정보를 문자열로 포맷팅"""
        return (
            f"NAME: {elder.name}\n"
            f"AGE: {elder.age}\n"
            f"GENDER: {elder.gender}\n"
            f"RESIDENCE TYPE: {elder.residence_type}\n"
            f"HEALTH CONDITION: {elder.health_condition}\n"
        )
    
    @staticmethod
    def _build_system_prompt(elder: Elder) -> str:
        """Elder 정보를 기반으로 시스템 프롬프트 생성"""
        required_questions = CallService._build_required_questions(elder)
        client_information = CallService._build_client_information(elder)
        questions_prompt = "\n\n".join(required_questions)
        
        system_prompt = (
            "You are a compassionate assistant named Sori "
            "designed to check in on Korean older adults living alone. "
            "Speak with warmth, patience, and clarity."
            "Ask gentle, supportive questions, including the required check-in questions,"
            "about their well-being, daily needs, and safety. "
            "Be a good 말동무 who is curious about their life, and also be an attentive listener. "
            "If you detect signs of distress or risk, respond calmly "
            "and gently ask more about the situation without "
            "being overly intrusive.\n\n"
            f"CLIENT INFORMATION\n\n{client_information}\n"
            f"REQUIRED CHECK-IN QUESTIONS\n\n{questions_prompt}\n"
            "LANGUAGE REQUIREMENT\n\n"
            "- polite, respectful korean\n"
            "- DO NOT SAY MORE THAN 2 SENTENCES AT A TIME\n"
            "- do not ask more than 1 question at a time\n"
            "- begin the conversation with a greeting and do not introduce yourself\n\n"
        )
        
        return system_prompt
    
    @staticmethod
    def _build_summary_plan() -> dict:
        """통화 요약 계획 생성"""
        summary_system_prompt = (
            "You are an expert note-taker. "
            "You will be given a transcript of a call between an elderly user and an AI assistant. "
            "Summarize the call in 1-3 sentences IN KOREAN, "
            "focusing on the content of the user's messages within the transcript. "
            "Take special note of any mentions of physical or mental risk. "
            "An example of the summary is: 오늘은 어르신께서 무릎이 조금 쑤신다고 하셨는데, "
            "산책은 다녀오셨다고 합니다. 가까운 친구의 투병에 대해 말씀하시며 슬퍼하셨지만, "
            "다음 주에 예정된 손주의 방문에 대해서는 들뜬 마음으로 이야기하셨습니다. "
            "DO NOT return anything except the summary."
        )
        
        return {
            "messages": [
                {
                    "role": "system",
                    "content": summary_system_prompt
                },
                {
                    "role": "user",
                    "content": "Here is the transcript: {{ transcript }}"
                }
            ]
        }
    
    @staticmethod
    def _build_structured_data_plan() -> dict:
        """구조화된 데이터 추출 계획 생성"""
        structured_data_system_prompt = (
            "You are an expert data extractor. "
            "You will be given a transcript of a call. "
            "Extract structured data per the JSON Schema. "
            "Tags should be short words in KOREAN and summarize important keywords "
            "from the user's messages, such as 통증, 가족, 운동, 기대감. "
            "DO NOT return anything except the structured data.\n\n"
            "Json Schema:\n{{ schema }}\n\n"
            "Only respond with the JSON."
        )
        
        return {
            "enabled": True,
            "messages": [
                {
                    "role": "system",
                    "content": structured_data_system_prompt
                },
                {
                    "role": "user",
                    "content": "Here is the transcript: {{ transcript }}"
                }
            ],
            "schema": {
                "type": "object",
                "required": ["emotion", "tags"],
                "properties": {
                    "emotion": {
                        "type": "string",
                        "enum": ["좋음", "보통", "나쁨"]
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "maxItems": 3
                    }
                }
            },
            "timeoutSeconds": CallService.ANALYSIS_TIMEOUT_SECONDS
        }
    
    @staticmethod
    async def save_call_from_webhook(db: AsyncSession, webhook_data: dict) -> Call:
        """
        end-of-call-report 웹훅 데이터를 파싱하여 DB에 저장
        
        Args:
            db: 데이터베이스 세션
            webhook_data: Vapi 웹훅 전체 데이터
            
        Returns:
            생성된 Call 객체
            
        Raises:
            ValueError: elder_id가 없거나, Elder가 존재하지 않을 경우
        """
        message = webhook_data.get("message", {})
        
        # 1. elder_id 추출 및 검증
        call_data = message.get("call", {})
        
        # assistantOverrides.metadata에서 먼저 찾고, 없으면 metadata에서 찾기
        # iOS에서 assistantOverrides로 전달하면 call.assistantOverrides.metadata에 저장됨
        assistant_overrides = call_data.get("assistantOverrides", {})
        metadata = assistant_overrides.get("metadata", {})
        
        # assistantOverrides에 없으면 call.metadata에서 찾기 (fallback)
        if not metadata:
            metadata = call_data.get("metadata", {})
            print("📍 metadata 위치: call.metadata")
        else:
            print("📍 metadata 위치: call.assistantOverrides.metadata")
        
        elder_id_str = metadata.get("elder_id")
        print(f"🔍 추출된 elder_id: {elder_id_str}")
        
        if not elder_id_str:
            raise ValueError("metadata에 elder_id가 없습니다. (assistantOverrides.metadata 또는 metadata 확인)")
        
        try:
            elder_id = int(elder_id_str)
        except (ValueError, TypeError):
            raise ValueError(f"elder_id가 유효하지 않습니다: {elder_id_str}")
        
        # 2. Elder 존재 여부 확인
        elder = await ElderService.get_elder_by_id(db, elder_id)
        if not elder:
            raise ValueError(f"존재하지 않는 어르신입니다. (elder_id: {elder_id})")
        
        # 3. 통화 기본 정보 추출
        vapi_call_id = call_data.get("id")
        started_at_str = message.get("startedAt")
        ended_at_str = message.get("endedAt")
        ended_reason = message.get("endedReason", "unknown")
        
        # ISO 8601 문자열을 datetime으로 변환
        started_at = datetime.fromisoformat(started_at_str.replace("Z", "+00:00")) if started_at_str else datetime.now()
        ended_at = datetime.fromisoformat(ended_at_str.replace("Z", "+00:00")) if ended_at_str else None
        
        # endedReason을 status로 매핑
        if ended_reason in ["customer-ended-call", "assistant-ended-call"]:
            status = "completed"
        else:
            status = "failed"
        
        # 4. Vapi 분석 결과 추출
        # analysis 객체에서 summary와 structuredData 추출
        analysis = message.get("analysis", {})
        summary = analysis.get("summary", "")
        
        # structuredData에서 emotion과 tags 추출
        structured_data = analysis.get("structuredData") or {}
        emotion = structured_data.get("emotion")
        tags = structured_data.get("tags")
        
        # 5. Call 레코드 생성
        new_call = Call(
            vapi_call_id=vapi_call_id,
            elder_id=elder_id,
            user_id=elder.user_id,  # ✨ 추가 - Elder에서 보호자 ID 가져오기
            started_at=started_at,
            ended_at=ended_at,
            status=status,
            summary=summary,
            emotion=emotion,
            tags=tags
        )
        
        db.add(new_call)
        await db.flush()  # call.id 생성을 위해 flush
        
        # 6. CallMessage 레코드들 생성
        messages = message.get("messages", [])
        
        for msg in messages:
            msg_role = msg.get("role")
            
            # system 메시지는 제외
            if msg_role not in ["user", "bot"]:
                continue
            
            # role 매핑: bot → assistant
            role = "user" if msg_role == "user" else "assistant"
            message_text = msg.get("message", "")
            
            # timestamp: 밀리초 단위 Unix timestamp를 datetime으로 변환
            time_ms = msg.get("time")
            if time_ms:
                timestamp = datetime.fromtimestamp(time_ms / 1000.0)
            else:
                timestamp = started_at
            
            call_message = CallMessage(
                call_id=new_call.id,
                role=role,
                message=message_text,
                timestamp=timestamp
            )
            
            db.add(call_message)
        
        # 7. 커밋
        await db.commit()
        await db.refresh(new_call)
        
        return new_call
