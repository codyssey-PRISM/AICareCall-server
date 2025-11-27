"""Elder 서비스 레이어"""
import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.elder import Elder
from app.db.models.user import User
from app.schemas.elder import ElderCreate


class ElderService:
    """어르신 관련 비즈니스 로직"""
    
    @staticmethod
    def _generate_invite_code() -> str:
        """
        6자리 초대 코드 생성 (대문자 알파벳 + 숫자)
        
        Returns:
            6자리 초대 코드 (예: "A1B2C3", "XY9Z01")
        """
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=6))
    
    @staticmethod
    async def create_elder(
        db: AsyncSession,
        user_id: int,
        elder_data: ElderCreate
    ) -> Elder:
        """
        새로운 어르신 등록
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            elder_data: 어르신 등록 데이터
            
        Returns:
            생성된 Elder 객체
            
        Raises:
            ValueError: 보호자(User)가 존재하지 않을 경우
        """
        try:
            # 0. 보호자 존재 여부 확인
            print(f"🔍 [Step 1] 보호자 존재 여부 확인 (user_id: {user_id})")
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if user is None:
                raise ValueError(f"존재하지 않는 보호자입니다. (user_id: {user_id})")
            
            print(f"✅ 보호자 확인 완료: {user.email}")
            
            # 1. Elder 레코드 생성
            print(f"🔍 [Step 2] Elder 레코드 생성 시작")
            invite_code = ElderService._generate_invite_code()
            print(f"   생성된 초대 코드: {invite_code}")
            
            new_elder = Elder(
                user_id=user_id,
                name=elder_data.name,
                gender=elder_data.gender,
                age=elder_data.age,
                relation=elder_data.relation,
                phone=elder_data.phone,
                residence_type=elder_data.residence_type,
                health_condition=elder_data.health_condition,
                begin_date=elder_data.begin_date,
                end_date=elder_data.end_date,
                ask_meal=elder_data.ask_meal,
                ask_medication=elder_data.ask_medication,
                ask_emotion=elder_data.ask_emotion,
                ask_special_event=elder_data.ask_special_event,
                additional_info=elder_data.additional_info,
                invite_code=invite_code,
            )
            
            db.add(new_elder)
            print(f"🔍 [Step 3] DB flush 시작 (elder.id 생성)")
            await db.flush()  # elder.id 생성을 위해 flush
            print(f"✅ Elder 레코드 생성 완료 (elder_id: {new_elder.id})")
            
            # 2. CallSchedule 레코드들 생성 (CallScheduleService 사용)
            print(f"🔍 [Step 4] CallSchedule 생성 시작")
            print(f"   weekdays: {elder_data.call_weekdays}")
            print(f"   times: {elder_data.call_times}")
            
            from app.services.call_schedule import CallScheduleService
            await CallScheduleService.create_schedules(
                db=db,
                elder_id=new_elder.id,
                weekdays=elder_data.call_weekdays,
                times=elder_data.call_times
            )
            print(f"✅ CallSchedule 생성 완료")
            
            print(f"🔍 [Step 5] DB commit 시작")
            await db.commit()
            await db.refresh(new_elder)
            print(f"✅ 최종 커밋 완료")
            
            return new_elder
            
        except ValueError:
            # ValueError는 그대로 재발생
            raise
        except Exception as e:
            # 다른 예외는 상세 로그 출력 후 재발생
            print(f"❌ [ElderService] 예외 발생:")
            print(f"   타입: {type(e).__name__}")
            print(f"   메시지: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 롤백 시도
            await db.rollback()
            print(f"🔄 DB 롤백 완료")
            
            raise
    
    @staticmethod
    async def get_elder_by_id(db: AsyncSession, elder_id: int) -> Elder | None:
        """
        ID로 어르신 정보 조회
        
        Args:
            db: 데이터베이스 세션
            elder_id: 어르신 ID
            
        Returns:
            Elder 객체 또는 None
        """
        result = await db.execute(
            select(Elder).where(Elder.id == elder_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_elders_by_user(db: AsyncSession, user_id: int) -> list[Elder]:
        """
        특정 사용자의 모든 어르신 목록 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            Elder 객체 리스트
        """
        result = await db.execute(
            select(Elder).where(Elder.user_id == user_id)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def regenerate_invite_code(
        db: AsyncSession,
        elder_id: int,
        user_id: int
    ) -> Elder:
        """
        초대 코드 재생성
        
        Args:
            db: 데이터베이스 세션
            elder_id: 어르신 ID
            user_id: 사용자 ID (권한 확인용)
            
        Returns:
            업데이트된 Elder 객체
            
        Raises:
            ValueError: 어르신을 찾을 수 없거나 권한이 없는 경우
        """
        elder = await ElderService.get_elder_by_id(db, elder_id)
        
        if not elder:
            raise ValueError("어르신을 찾을 수 없습니다")
        
        if elder.user_id != user_id:
            raise ValueError("권한이 없습니다")
        
        # 새로운 초대 코드 생성 및 할당
        elder.invite_code = ElderService._generate_invite_code()
        
        await db.commit()
        await db.refresh(elder)
        
        return elder
    
    @staticmethod
    async def verify_and_register_device(
        db: AsyncSession,
        invite_code: str,
        voip_device_token: str
    ) -> Elder:
        """
        초대 코드를 검증하고 VoIP 디바이스 토큰을 등록
        
        Args:
            db: 데이터베이스 세션
            invite_code: 초대 코드
            voip_device_token: VoIP 디바이스 토큰
            
        Returns:
            업데이트된 Elder 객체
            
        Raises:
            ValueError: 초대 코드가 유효하지 않거나 이미 사용된 경우
        """
        # 1. invite_code로 Elder 조회
        result = await db.execute(
            select(Elder).where(Elder.invite_code == invite_code)
        )
        elder = result.scalar_one_or_none()
        
        # 2. 존재하지 않으면 에러
        if not elder:
            raise ValueError("초대 코드가 유효하지 않습니다")
        
        # 3. voip_device_token이 이미 있으면 에러 (이미 등록됨)
        if elder.voip_device_token is not None:
            raise ValueError("이미 등록된 초대 코드입니다")
        
        # 4. voip_device_token 업데이트
        elder.voip_device_token = voip_device_token
        
        # 5. commit 및 refresh
        await db.commit()
        await db.refresh(elder)
        
        return elder

