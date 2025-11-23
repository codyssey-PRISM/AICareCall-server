"""CallSchedule 서비스 레이어"""
from datetime import datetime, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models.call_schedule import CallSchedule


class CallScheduleService:
    """통화 스케줄 관련 비즈니스 로직"""
    
    # 요일 매핑 (한글 → 영어)
    WEEKDAY_MAP = {
        "월요일": "Monday",
        "화요일": "Tuesday", 
        "수요일": "Wednesday",
        "목요일": "Thursday",
        "금요일": "Friday",
        "토요일": "Saturday",
        "일요일": "Sunday"
    }
    
    # 영어 요일 → 숫자 (Python weekday: Monday=0, Sunday=6)
    WEEKDAY_TO_NUM = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }
    
    @staticmethod
    async def create_schedules(
        db: AsyncSession,
        elder_id: int,
        weekdays: list[str],
        times: list[time]
    ) -> list[CallSchedule]:
        """
        여러 스케줄을 한번에 생성 (요일 × 시간 조합)
        
        Args:
            db: 데이터베이스 세션
            elder_id: 어르신 ID
            weekdays: 요일 리스트 (예: ["월요일", "수요일", "금요일"])
            times: 시간 리스트 (예: [time(9, 0), time(18, 0)])
            
        Returns:
            생성된 CallSchedule 객체 리스트
        """
        schedules = []
        
        for weekday in weekdays:
            for call_time in times:
                schedule = CallSchedule(
                    elder_id=elder_id,
                    day_of_week=CallScheduleService.WEEKDAY_MAP[weekday],
                    time=call_time
                )
                db.add(schedule)
                schedules.append(schedule)
        
        await db.flush()  # ID 생성을 위해 flush
        return schedules
    
    @staticmethod
    async def get_schedules_by_elder(
        db: AsyncSession,
        elder_id: int
    ) -> list[CallSchedule]:
        """
        특정 어르신의 모든 스케줄 조회
        
        Args:
            db: 데이터베이스 세션
            elder_id: 어르신 ID
            
        Returns:
            CallSchedule 객체 리스트
        """
        result = await db.execute(
            select(CallSchedule)
            .where(CallSchedule.elder_id == elder_id)
            .order_by(CallSchedule.day_of_week, CallSchedule.time)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_scheduled_calls_for_next_hour(
        db: AsyncSession
    ) -> list[tuple[int, datetime]]:
        """
        다음 1시간 동안 예정된 통화 스케줄 조회
        
        현재 시간 기준 다음 1시간 이내에 예정된 스케줄을 조회합니다.
        예: 현재가 9:55이면 10:00~10:59 사이의 스케줄을 조회
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            (elder_id: int, run_time: datetime) 튜플의 리스트
        """
        now = datetime.now()
        
        # 다음 정시 (예: 9:55 → 10:00)
        next_hour_start = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        next_hour_end = next_hour_start + timedelta(hours=1)
        
        # 현재 요일 (Python weekday: 0=Monday, 6=Sunday)
        current_weekday_num = next_hour_start.weekday()
        
        # 숫자를 요일 문자열로 변환
        weekday_str = None
        for day_str, day_num in CallScheduleService.WEEKDAY_TO_NUM.items():
            if day_num == current_weekday_num:
                weekday_str = day_str
                break
        
        # DB 조회: 해당 요일이면서 시간이 next_hour 범위 내인 것
        result = await db.execute(
            select(CallSchedule)
            .where(
                and_(
                    CallSchedule.day_of_week == weekday_str,
                    CallSchedule.time >= next_hour_start.time(),
                    CallSchedule.time < next_hour_end.time()
                )
            )
        )
        
        return list(
            map(
                lambda x: (x.elder_id, datetime.combine(next_hour_start.date(), x.time)), 
                result.scalars().all()
            )
        )
    
    @staticmethod
    async def delete_schedules_by_elder(
        db: AsyncSession,
        elder_id: int
    ) -> int:
        """
        특정 어르신의 모든 스케줄 삭제
        
        Args:
            db: 데이터베이스 세션
            elder_id: 어르신 ID
            
        Returns:
            삭제된 스케줄 개수
        """
        result = await db.execute(
            select(CallSchedule).where(CallSchedule.elder_id == elder_id)
        )
        schedules = result.scalars().all()
        
        count = 0
        for schedule in schedules:
            await db.delete(schedule)
            count += 1
        
        return count
    
    @staticmethod
    async def update_schedules(
        db: AsyncSession,
        elder_id: int,
        weekdays: list[str],
        times: list[time]
    ) -> list[CallSchedule]:
        """
        스케줄 업데이트 (기존 삭제 후 재생성)
        
        Args:
            db: 데이터베이스 세션
            elder_id: 어르신 ID
            weekdays: 새로운 요일 리스트
            times: 새로운 시간 리스트
            
        Returns:
            새로 생성된 CallSchedule 객체 리스트
        """
        # 1. 기존 스케줄 삭제
        await CallScheduleService.delete_schedules_by_elder(db, elder_id)
        
        # 2. 새 스케줄 생성
        new_schedules = await CallScheduleService.create_schedules(
            db, elder_id, weekdays, times
        )
        
        return new_schedules