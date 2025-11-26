"""대시보드 API 테스트용 시드 데이터 생성

모든 테이블에 더미 데이터를 생성합니다:
- Users (보호자)
- Elders (어르신)
- CallSchedules (통화 스케줄)
- Calls (통화 기록)
- CallMessages (대화 내용)

사용법:
    cd server
    rm data/app.db  # 기존 DB 삭제 (선택사항)
    alembic upgrade head
    python -m seed.dashboard_test_seed
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, time
from random import choice, randint

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.db.models.elder import Elder
from app.db.models.call_schedule import CallSchedule
from app.db.models.call import Call
from app.db.models.call_message import CallMessage


# 더미 대화 데이터
SAMPLE_CONVERSATIONS = [
    {
        "summary": "오늘 아침 식사를 잘 하셨고, 약도 제때 드셨습니다. 날씨가 좋아서 산책을 다녀오셨다고 하십니다.",
        "emotion": "평온",
        "tags": ["식사완료", "약복용", "산책"],
        "messages": [
            ("assistant", "안녕하세요! 오늘 하루는 어떠셨어요?"),
            ("user", "아, 잘 지냈어요. 아침에 일찍 일어나서 산책도 다녀왔어요."),
            ("assistant", "산책 다녀오셨군요! 날씨는 어땠어요?"),
            ("user", "날씨가 참 좋더라고요. 햇살도 따듯하고."),
            ("assistant", "그거 참 좋으시네요. 오늘 식사는 잘 하셨나요?"),
            ("user", "네, 아침에 밥이랑 된장찌개 먹었어요."),
            ("assistant", "잘 드셨네요. 약은 드셨어요?"),
            ("user", "네, 아침약도 잘 먹었습니다."),
            ("assistant", "잘하셨어요. 오늘도 건강하게 보내세요!"),
        ]
    },
    {
        "summary": "오늘은 몸이 조금 피곤하다고 하십니다. 저녁 약을 깜빡하셨다고 하여 상기시켜 드렸습니다.",
        "emotion": "피곤",
        "tags": ["피로", "약복용누락"],
        "messages": [
            ("assistant", "안녕하세요! 오늘은 어떻게 지내셨어요?"),
            ("user", "오늘은 좀 피곤하네요. 잠을 잘 못 잤나봐요."),
            ("assistant", "그러셨군요. 밤에 편히 주무시지 못하셨나요?"),
            ("user", "응, 자다 깨고 그랬어요."),
            ("assistant", "식사는 잘 하셨어요?"),
            ("user", "점심은 간단하게 먹었어요."),
            ("assistant", "약은 드셨나요?"),
            ("user", "앗, 저녁약을 아직 안 먹었네."),
            ("assistant", "저녁 약 꼭 드시는 거 잊지 마세요!"),
            ("user", "네네, 고맙습니다."),
        ]
    },
    {
        "summary": "손자가 방문해서 즐거운 시간을 보내셨습니다. 건강 상태는 양호하시고 기분이 좋으십니다.",
        "emotion": "기쁨",
        "tags": ["가족방문", "식사완료", "약복용"],
        "messages": [
            ("assistant", "안녕하세요! 오늘 기분이 좋아 보이시는데요?"),
            ("user", "네! 오늘 손자가 다녀갔어요."),
            ("assistant", "아, 정말요? 얼마나 좋으셨겠어요!"),
            ("user", "같이 밥도 먹고 산책도 하고 그랬어요."),
            ("assistant", "정말 좋은 시간 보내셨네요. 식사는 잘 하셨고요?"),
            ("user", "네, 손자가 사온 치킨도 먹었어요. 하하."),
            ("assistant", "즐거운 식사 시간이었겠어요. 약은 드셨나요?"),
            ("user", "네, 아침저녁 다 먹었어요."),
            ("assistant", "잘하셨어요! 오늘도 행복한 하루 되세요."),
        ]
    },
    {
        "summary": "무릎이 좀 아프다고 하십니다. 병원 예약은 내일로 잡으셨고, 식사와 약은 잘 챙기고 계십니다.",
        "emotion": "불편",
        "tags": ["통증", "병원예약", "식사완료", "약복용"],
        "messages": [
            ("assistant", "안녕하세요! 오늘은 어떠세요?"),
            ("user", "오늘은 무릎이 좀 아파요."),
            ("assistant", "아이고, 괜찮으세요? 많이 아프신가요?"),
            ("user", "걸을 때 좀 불편해요. 내일 병원 가기로 했어요."),
            ("assistant", "잘 하셨어요. 병원 예약은 하셨나요?"),
            ("user", "네, 내일 오전에 가기로 했어요."),
            ("assistant", "그럼 다행이에요. 식사는 하셨어요?"),
            ("user", "네, 점심 잘 먹었어요."),
            ("assistant", "약도 제때 드셨나요?"),
            ("user", "네, 아까 먹었어요."),
            ("assistant", "잘하셨어요. 내일 병원 잘 다녀오세요!"),
        ]
    },
    {
        "summary": "이웃과 함께 점심 식사를 하셨습니다. 기분이 좋으시고 건강 상태도 양호하십니다.",
        "emotion": "평온",
        "tags": ["사회활동", "식사완료", "약복용"],
        "messages": [
            ("assistant", "안녕하세요! 오늘 하루는 어떠셨어요?"),
            ("user", "오늘은 아래층 이웃분이랑 같이 밥 먹었어요."),
            ("assistant", "아, 좋으시겠어요! 어디 가서 드셨나요?"),
            ("user", "근처 한식당 갔어요. 음식이 맛있더라고요."),
            ("assistant", "즐거운 식사 시간이었겠네요."),
            ("user", "네, 이야기도 하고 좋았어요."),
            ("assistant", "약은 잘 챙겨 드셨나요?"),
            ("user", "네, 집에 와서 바로 먹었어요."),
            ("assistant", "잘하셨어요! 앞으로도 건강하게 지내세요."),
        ]
    },
]

EMOTIONS = ["평온", "기쁨", "피곤", "불편", "우울", "불안"]
TAGS_POOL = ["식사완료", "약복용", "산책", "통증", "병원예약", "가족방문", "사회활동", "약복용누락", "피로"]


async def create_sample_data():
    """샘플 데이터 생성"""

    print("🌱 대시보드 테스트용 시드 데이터 생성 시작...\n")

    async with AsyncSessionLocal() as session:
        try:
            # 1. Users (보호자) 생성
            print("👤 Users 생성 중...")
            users = [
                User(email="guardian1@example.com"),
                User(email="guardian2@example.com"),
                User(email="guardian3@example.com"),
            ]

            for user in users:
                session.add(user)

            await session.flush()

            for user in users:
                print(f"  ✅ {user.email} (ID: {user.id})")

            # 2. Elders 생성
            print("\n👴 Elders 생성 중...")
            elders = [
                Elder(
                    user_id=users[0].id,
                    name="김영희",
                    gender="여",
                    age=75,
                    relation="어머니",
                    phone="010-1111-1111",
                    residence_type="독거",
                    health_condition="양호",
                    begin_date=datetime.now() - timedelta(days=90),
                    end_date=None,
                    ask_meal=True,
                    ask_medication=True,
                    ask_emotion=True,
                    ask_special_event=True,
                    additional_info="특이사항 없음",
                    invite_code="ABC001",
                    voip_device_token="dummy_token_1"
                ),
                Elder(
                    user_id=users[0].id,
                    name="김철수",
                    gender="남",
                    age=78,
                    relation="아버지",
                    phone="010-2222-2222",
                    residence_type="독거",
                    health_condition="당뇨 관리 중",
                    begin_date=datetime.now() - timedelta(days=60),
                    end_date=None,
                    ask_meal=True,
                    ask_medication=True,
                    ask_emotion=True,
                    ask_special_event=False,
                    additional_info="매일 오전 약 복용 필요",
                    invite_code="ABC002",
                    voip_device_token="dummy_token_2"
                ),
                Elder(
                    user_id=users[1].id,
                    name="박순자",
                    gender="여",
                    age=82,
                    relation="할머니",
                    phone="010-3333-3333",
                    residence_type="요양원",
                    health_condition="치매 초기 증상",
                    begin_date=datetime.now() - timedelta(days=120),
                    end_date=None,
                    ask_meal=True,
                    ask_medication=True,
                    ask_emotion=True,
                    ask_special_event=True,
                    additional_info="요양원 입소 중",
                    invite_code="ABC003",
                    voip_device_token="dummy_token_3"
                ),
                Elder(
                    user_id=users[1].id,
                    name="이만수",
                    gender="남",
                    age=80,
                    relation="할아버지",
                    phone="010-4444-4444",
                    residence_type="배우자 동거",
                    health_condition="고혈압",
                    begin_date=datetime.now() - timedelta(days=30),
                    end_date=None,
                    ask_meal=True,
                    ask_medication=True,
                    ask_emotion=True,
                    ask_special_event=True,
                    additional_info="혈압약 복용 중",
                    invite_code="ABC004",
                    voip_device_token="dummy_token_4"
                ),
                Elder(
                    user_id=users[2].id,
                    name="최영란",
                    gender="여",
                    age=73,
                    relation="어머니",
                    phone="010-5555-5555",
                    residence_type="독거",
                    health_condition="양호",
                    begin_date=datetime.now() - timedelta(days=15),
                    end_date=None,
                    ask_meal=True,
                    ask_medication=False,
                    ask_emotion=True,
                    ask_special_event=True,
                    additional_info="활동적이심",
                    invite_code="ABC005",
                    voip_device_token="dummy_token_5"
                ),
            ]

            for elder in elders:
                session.add(elder)

            await session.flush()

            for elder in elders:
                print(f"  ✅ {elder.name} ({elder.relation}) - User ID: {elder.user_id}, Elder ID: {elder.id}")

            # 3. CallSchedules 생성
            print("\n📅 CallSchedules 생성 중...")
            schedules = []

            # 각 elder마다 스케줄 생성
            for elder in elders:
                # 아침 9시 스케줄 (월~금)
                for day in ["월", "화", "수", "목", "금"]:
                    schedules.append(
                        CallSchedule(
                            elder_id=elder.id,
                            day_of_week=day,
                            time=time(9, 0)
                        )
                    )

                # 저녁 8시 스케줄 (매일)
                for day in ["월", "화", "수", "목", "금", "토", "일"]:
                    schedules.append(
                        CallSchedule(
                            elder_id=elder.id,
                            day_of_week=day,
                            time=time(20, 0)
                        )
                    )

            for schedule in schedules:
                session.add(schedule)

            await session.flush()

            print(f"  ✅ {len(schedules)}개의 스케줄 생성 완료")

            # 4. Calls 및 CallMessages 생성
            print("\n📞 Calls 및 CallMessages 생성 중...")

            total_calls = 0
            total_messages = 0

            # 각 elder마다 최근 14일간의 통화 기록 생성
            for elder in elders:
                print(f"\n  Elder: {elder.name}")

                for days_ago in range(14):
                    # 하루에 1-2번 통화
                    num_calls = randint(1, 2)

                    for call_num in range(num_calls):
                        # 랜덤 시간 설정 (오전 9시 or 저녁 8시)
                        hour = 9 if call_num == 0 else 20
                        started_at = datetime.now() - timedelta(days=days_ago, hours=24-hour, minutes=randint(0, 30))

                        # 통화 시간 5-15분
                        duration_minutes = randint(5, 15)
                        ended_at = started_at + timedelta(minutes=duration_minutes)

                        # 랜덤 대화 선택
                        conversation = choice(SAMPLE_CONVERSATIONS)

                        # 80% 확률로 성공, 20% 확률로 실패
                        status = "completed" if randint(1, 10) <= 8 else choice(["no_answer", "failed"])

                        call = Call(
                            vapi_call_id=f"vapi_call_{elder.id}_{days_ago}_{call_num}",
                            elder_id=elder.id,
                            user_id=elder.user_id,  # ✨ 보호자 ID 추가
                            started_at=started_at,
                            ended_at=ended_at if status == "completed" else None,
                            status=status,
                            summary=conversation["summary"] if status == "completed" else None,
                            emotion=conversation["emotion"] if status == "completed" else None,
                            tags=conversation["tags"] if status == "completed" else None,
                        )

                        session.add(call)
                        await session.flush()

                        total_calls += 1

                        # 통화 성공 시에만 메시지 생성
                        if status == "completed":
                            for idx, (role, message_text) in enumerate(conversation["messages"]):
                                message_time = started_at + timedelta(seconds=30 * idx)

                                message = CallMessage(
                                    call_id=call.id,
                                    role=role,
                                    message=message_text,
                                    timestamp=message_time
                                )

                                session.add(message)
                                total_messages += 1

                print(f"    ✅ {num_calls * 14}개의 통화 기록 생성")

            await session.commit()

            print("\n" + "="*60)
            print("✨ 시드 데이터 생성 완료!")
            print("="*60)
            print(f"📊 생성 요약:")
            print(f"  - Users: {len(users)}명")
            print(f"  - Elders: {len(elders)}명")
            print(f"  - CallSchedules: {len(schedules)}개")
            print(f"  - Calls: {total_calls}개")
            print(f"  - CallMessages: {total_messages}개")
            print("="*60)

            print("\n🔑 테스트 계정:")
            for user in users:
                print(f"  - {user.email}")

            print("\n📋 다음 단계:")
            print("  1. API 서버 시작: uvicorn app.main:app --reload")
            print("  2. 대시보드에서 위 계정으로 로그인")
            print("  3. 어르신 목록, 통화 기록 등 확인")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ 에러 발생: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(create_sample_data())
