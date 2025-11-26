"""User와 Elder 시드 데이터 생성 (VoIP 토큰 없음)

사용법:
    cd server
    rm data/app.db
    alembic upgrade head
    python -m seed.user-elder-no-token-seed
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.db.models.elder import Elder


async def seed_users_and_elders():
    """User와 Elder 시드 데이터 생성 (voip_device_token 없이)"""
    
    print("🌱 시드 데이터 생성 시작...")
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. 보호자(User) 생성
            print("\n👤 User 생성 중...")
            user1 = User(email="guardian1@example.com")
            user2 = User(email="guardian2@example.com")
            
            session.add(user1)
            session.add(user2)
            await session.flush()  # ID 할당을 위해 flush
            
            print(f"  ✅ User 1: {user1.email} (ID: {user1.id})")
            print(f"  ✅ User 2: {user2.email} (ID: {user2.id})")
            
            # 2. 어르신(Elder) 생성 (voip_device_token 없이)
            print("\n👴 Elder 생성 중...")
            
            # Elder 1: user1의 어머니
            elder1 = Elder(
                user_id=user1.id,
                name="김영희",
                gender="여",
                age=75,
                relation="어머니",
                phone="010-1234-5678",
                residence_type="독거",
                health_condition="양호",
                begin_date=datetime.now(),
                end_date=None,
                ask_meal=True,
                ask_medication=True,
                ask_emotion=True,
                ask_special_event=True,
                additional_info="특이사항 없음",
                invite_code="ABC123",
                voip_device_token=None  # 명시적으로 None
            )
            
            # Elder 2: user1의 아버지
            elder2 = Elder(
                user_id=user1.id,
                name="김철수",
                gender="남",
                age=78,
                relation="아버지",
                phone="010-2345-6789",
                residence_type="독거",
                health_condition="당뇨 관리 중",
                begin_date=datetime.now(),
                end_date=None,
                ask_meal=True,
                ask_medication=True,
                ask_emotion=True,
                ask_special_event=False,
                additional_info="매일 오전 약 복용 필요",
                invite_code="DEF456",
                voip_device_token=None
            )
            
            # Elder 3: user2의 할머니
            elder3 = Elder(
                user_id=user2.id,
                name="박순자",
                gender="여",
                age=82,
                relation="할머니",
                phone="010-3456-7890",
                residence_type="요양원",
                health_condition="치매 초기 증상",
                begin_date=datetime.now() - timedelta(days=30),
                end_date=None,
                ask_meal=True,
                ask_medication=True,
                ask_emotion=True,
                ask_special_event=True,
                additional_info="요양원 입소 중, 주 2회 방문 가능",
                invite_code="GHI789",
                voip_device_token=None
            )
            
            session.add(elder1)
            session.add(elder2)
            session.add(elder3)
            await session.flush()
            
            print(f"  ✅ Elder 1: {elder1.name} ({elder1.relation}) - User {elder1.user_id}")
            print(f"     초대코드: {elder1.invite_code}, VoIP 토큰: {elder1.voip_device_token}")
            print(f"  ✅ Elder 2: {elder2.name} ({elder2.relation}) - User {elder2.user_id}")
            print(f"     초대코드: {elder2.invite_code}, VoIP 토큰: {elder2.voip_device_token}")
            print(f"  ✅ Elder 3: {elder3.name} ({elder3.relation}) - User {elder3.user_id}")
            print(f"     초대코드: {elder3.invite_code}, VoIP 토큰: {elder3.voip_device_token}")
            
            # 커밋
            await session.commit()
            
            print("\n✨ 시드 데이터 생성 완료!")
            print(f"   - User: 2명")
            print(f"   - Elder: 3명 (모두 voip_device_token=None)")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ 에러 발생: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_users_and_elders())

