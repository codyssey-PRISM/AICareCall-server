"""Elder 서비스 레이어"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.elder import Elder
from app.db.models.call_schedule import CallSchedule
from app.schemas.elder import ElderCreate


class ElderService:
    """어르신 관련 비즈니스 로직"""
    
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
        """
        # 1. Elder 레코드 생성
        new_elder = Elder(
            user_id=user_id,
            name=elder_data.name,
            relationship=elder_data.relationship,
            phone=elder_data.phone,
            residence_type=elder_data.residence,
            health_condition=elder_data.health_condition,
            begin_date=elder_data.begin_date,
            end_date=elder_data.end_date,
            ask_meal=elder_data.ask_meal,
            ask_medication=elder_data.ask_medication,
            ask_emotion=elder_data.ask_emotion,
            ask_special_event=elder_data.ask_special_event,
            additional_info=elder_data.additional_info,
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

