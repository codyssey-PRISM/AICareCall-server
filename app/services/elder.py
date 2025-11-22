"""Elder 서비스 레이어"""
import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.elder import Elder
from app.db.models.call_schedule import CallSchedule
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
        # 0. 보호자 존재 여부 확인
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if user is None:
            raise ValueError(f"존재하지 않는 보호자입니다. (user_id: {user_id})")
        
        # 1. Elder 레코드 생성
        new_elder = Elder(
            user_id=user_id,
            name=elder_data.name,
            relationship=elder_data.relationship,
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
            invite_code=ElderService._generate_invite_code(),
        )
        
        db.add(new_elder)
        await db.flush()  # elder.id 생성을 위해 flush
        
        # 2. CallSchedule 레코드들 생성
        # 각 요일별 × 각 시간별 조합으로 생성
        for weekday in elder_data.call_weekdays:
            for call_time in elder_data.call_times:
                schedule = CallSchedule(
                    elder_id=new_elder.id,
                    day_of_week=weekday,
                    time=call_time
                )
                db.add(schedule)
        
        await db.commit()
        await db.refresh(new_elder)
        
        return new_elder
    
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

