"""대시보드 비즈니스 로직"""
from datetime import datetime, time, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.call import Call
from app.db.models.call_schedule import CallSchedule
from app.db.models.elder import Elder
from app.schemas.dashboard import (
    ElderBasicInfo,
    TodayHighlight,
    WeeklyStats,
    CallAttemptsStats,
    CallSuccessStats,
    AvgDurationStats,
    RecentCallItem,
    NextScheduledCall,
    WeeklyScheduleItem,
    CallMessageItem,
    CallDetailResponse,
)


def calculate_service_days(begin_date: datetime) -> int:
    """서비스 경과일 계산"""
    today = datetime.now().date()
    begin = begin_date.date() if isinstance(begin_date, datetime) else begin_date
    delta = today - begin
    return delta.days


def get_week_range(target_date: datetime | None = None) -> tuple[datetime, datetime]:
    """
    이번 주 월요일 00:00 ~ 다음 주 월요일 00:00 계산
    
    Args:
        target_date: 기준 날짜 (None이면 오늘)
    
    Returns:
        (week_start, week_end) 튜플
    """
    if target_date is None:
        target_date = datetime.now()
    
    # 이번 주 월요일 (weekday: 0=월요일, 6=일요일)
    days_since_monday = target_date.weekday()
    week_start = (target_date - timedelta(days=days_since_monday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    
    # 다음 주 월요일
    week_end = week_start + timedelta(days=7)
    
    return week_start, week_end


async def get_weekly_stats(
    db: AsyncSession,
    elder_id: int,
    week_start: datetime,
    week_end: datetime
) -> WeeklyStats:
    """
    주간 통화 통계 계산
    
    Args:
        db: DB 세션
        elder_id: 어르신 ID
        week_start: 주 시작 (월요일 00:00)
        week_end: 주 종료 (다음 주 월요일 00:00)
    
    Returns:
        WeeklyStats 객체
    """
    # 이번 주 모든 통화 조회
    result = await db.execute(
        select(Call)
        .where(Call.elder_id == elder_id)
        .where(Call.started_at >= week_start)
        .where(Call.started_at < week_end)
    )
    week_calls = result.scalars().all()
    
    # 통화 시도 횟수
    call_attempts_count = len(week_calls)
    
    # 통화 성공 횟수
    success_calls = [c for c in week_calls if c.status == "completed"]
    call_success_count = len(success_calls)
    
    # 평균 통화 시간 계산 (분 단위)
    durations = []
    for call in success_calls:
        if call.ended_at:
            duration_seconds = (call.ended_at - call.started_at).total_seconds()
            durations.append(duration_seconds / 60)  # 분으로 변환
    
    avg_duration_minutes = int(sum(durations) / len(durations)) if durations else 0
    
    return WeeklyStats(
        call_attempts=CallAttemptsStats(count=call_attempts_count),
        call_success_count=CallSuccessStats(count=call_success_count),
        avg_duration=AvgDurationStats(minutes=avg_duration_minutes)
    )


async def get_recent_calls(
    db: AsyncSession,
    elder_id: int,
    limit: int = 10
) -> list[RecentCallItem]:
    """
    최근 통화 기록 조회
    
    Args:
        db: DB 세션
        elder_id: 어르신 ID
        limit: 조회할 최대 개수
    
    Returns:
        RecentCallItem 리스트
    """
    result = await db.execute(
        select(Call)
        .where(Call.elder_id == elder_id)
        .order_by(Call.started_at.desc())
        .limit(limit)
    )
    calls = result.scalars().all()
    
    recent_call_items = []
    for call in calls:
        # 날짜/시간 포맷
        date_str = call.started_at.strftime("%Y.%m.%d")
        time_str = call.started_at.strftime("%H:%M")
        
        # 통화 시간 계산
        duration_minutes = 0
        if call.ended_at:
            duration_seconds = (call.ended_at - call.started_at).total_seconds()
            duration_minutes = int(duration_seconds / 60)
        
        # tags가 None이면 빈 리스트
        tags = call.tags if call.tags else []
        
        recent_call_items.append(
            RecentCallItem(
                id=call.id,
                date=date_str,
                time=time_str,
                duration_minutes=duration_minutes,
                summary=call.summary or "",
                tags=tags,
                emotion=call.emotion,
                status=call.status
            )
        )
    
    return recent_call_items


async def get_call_list_paginated(
    db: AsyncSession,
    elder_id: int,
    page: int = 1,
    page_size: int = 5
) -> tuple[list[RecentCallItem], int]:
    """
    통화 기록 페이지네이션 조회
    
    Args:
        db: DB 세션
        elder_id: 어르신 ID
        page: 페이지 번호 (1부터 시작)
        page_size: 페이지당 항목 수
    
    Returns:
        (RecentCallItem 리스트, 전체 개수) 튜플
    """
    from sqlalchemy import func
    
    # 전체 개수 조회
    count_result = await db.execute(
        select(func.count(Call.id))
        .where(Call.elder_id == elder_id)
    )
    total_count = count_result.scalar() or 0
    
    # 페이지네이션 데이터 조회
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Call)
        .where(Call.elder_id == elder_id)
        .order_by(Call.started_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    calls = result.scalars().all()
    
    # RecentCallItem으로 변환
    recent_call_items = []
    for call in calls:
        # 날짜/시간 포맷
        date_str = call.started_at.strftime("%Y.%m.%d")
        time_str = call.started_at.strftime("%H:%M")
        
        # 통화 시간 계산
        duration_minutes = 0
        if call.ended_at:
            duration_seconds = (call.ended_at - call.started_at).total_seconds()
            duration_minutes = int(duration_seconds / 60)
        
        # tags가 None이면 빈 리스트
        tags = call.tags if call.tags else []
        
        recent_call_items.append(
            RecentCallItem(
                id=call.id,
                date=date_str,
                time=time_str,
                duration_minutes=duration_minutes,
                summary=call.summary or "",
                tags=tags,
                emotion=call.emotion,
                status=call.status
            )
        )
    
    return recent_call_items, total_count


def get_today_highlight(recent_calls: list[RecentCallItem]) -> TodayHighlight | None:
    """
    오늘 통화 중 하이라이트 추출
    
    Args:
        recent_calls: 최근 통화 리스트
    
    Returns:
        TodayHighlight 또는 None
    """
    today_str = datetime.now().strftime("%Y.%m.%d")
    
    # 오늘 통화 중 가장 최근 것 (이미 최신순 정렬되어 있음)
    for call in recent_calls:
        if call.date == today_str and call.status == "completed":
            return TodayHighlight(
                message=call.summary,
                call_time=call.time,
                emotion=call.emotion or "평온",
                tags=call.tags
            )
    
    return None


# 요일 영문 -> 한글 매핑
WEEKDAY_KR = {
    "monday": "월요일",
    "tuesday": "화요일",
    "wednesday": "수요일",
    "thursday": "목요일",
    "friday": "금요일",
    "saturday": "토요일",
    "sunday": "일요일",
}

WEEKDAY_EN = {
    "월요일": "monday",
    "화요일": "tuesday",
    "수요일": "wednesday",
    "목요일": "thursday",
    "금요일": "friday",
    "토요일": "saturday",
    "일요일": "sunday",
}


def find_next_scheduled_call(
    call_schedules: list[CallSchedule],
    now: datetime | None = None
) -> NextScheduledCall | None:
    """
    다음 예정 통화 찾기
    
    Args:
        call_schedules: CallSchedule 리스트
        now: 현재 시각 (None이면 지금)
    
    Returns:
        NextScheduledCall 또는 None
    """
    if not call_schedules:
        return None
    
    if now is None:
        now = datetime.now()
    
    # 모든 예정 통화를 datetime으로 변환하여 정렬
    upcoming_calls = []
    
    for schedule in call_schedules:
        # 오늘부터 최대 7일 이내의 예정 통화 찾기
        for day_offset in range(8):
            target_date = now.date() + timedelta(days=day_offset)
            target_weekday = target_date.strftime("%A").lower()  # 'monday', 'tuesday', ...
            
            # CallSchedule의 day_of_week와 매칭 확인
            if schedule.day_of_week.lower() == target_weekday:
                # datetime 생성
                scheduled_datetime = datetime.combine(target_date, schedule.time)
                
                # 현재 시각 이후인 것만
                if scheduled_datetime > now:
                    upcoming_calls.append((scheduled_datetime, schedule))
    
    if not upcoming_calls:
        return None
    
    # 가장 가까운 미래 통화
    upcoming_calls.sort(key=lambda x: x[0])
    next_datetime, _ = upcoming_calls[0]
    
    # 날짜/시간 포맷
    date_display = next_datetime.strftime("%Y년 %m월 %d일").lstrip("0").replace("월 0", "월 ")
    time_display = next_datetime.strftime("%H:%M")
    is_today = next_datetime.date() == now.date()
    
    return NextScheduledCall(
        datetime=next_datetime,
        date_display=date_display,
        time_display=time_display,
        is_today=is_today
    )


def build_weekly_schedule(
    call_schedules: list[CallSchedule],
    week_start: datetime
) -> list[WeeklyScheduleItem]:
    """
    이번 주 월~일 일정 구성
    
    Args:
        call_schedules: CallSchedule 리스트
        week_start: 이번 주 월요일 00:00
    
    Returns:
        WeeklyScheduleItem 리스트 (7개, 월~일)
    """
    weekly_items = []
    
    # 월요일부터 일요일까지 7일
    for day_offset in range(7):
        target_date = week_start.date() + timedelta(days=day_offset)
        target_weekday_en = target_date.strftime("%A").lower()  # 'monday', 'tuesday', ...
        
        # 한글 요일
        weekday_kr = WEEKDAY_KR.get(target_weekday_en, target_weekday_en)
        
        # 날짜 포맷
        date_str = target_date.strftime("%Y-%m-%d")
        date_display = target_date.strftime("%m월 %d일").lstrip("0").replace("월 0", "월 ")
        
        # 해당 요일의 예정 시간들 찾기
        scheduled_times = []
        for schedule in call_schedules:
            if schedule.day_of_week.lower() == target_weekday_en:
                time_str = schedule.time.strftime("%H:%M")
                scheduled_times.append(time_str)
        
        # 시간순 정렬
        scheduled_times.sort()
        
        weekly_items.append(
            WeeklyScheduleItem(
                day_of_week=weekday_kr,
                date=date_str,
                date_display=date_display,
                scheduled_times=scheduled_times
            )
        )
    
    return weekly_items


async def build_elder_basic_info(elder: Elder) -> ElderBasicInfo:
    """
    어르신 기본 정보 구성
    
    Args:
        elder: Elder 모델 객체
    
    Returns:
        ElderBasicInfo 객체
    """
    service_days = calculate_service_days(elder.begin_date)
    
    return ElderBasicInfo(
        id=elder.id,
        name=elder.name,
        relation=elder.relation,
        service_days=service_days
    )


async def get_call_detail_by_id(
    db: AsyncSession,
    call_id: int
) -> tuple[Call | None, str]:
    """
    통화 상세 조회 (Call + CallMessage 함께 조회)
    
    Args:
        db: DB 세션
        call_id: 통화 ID
    
    Returns:
        (Call 객체 또는 None, 어르신 이름) 튜플
    """
    # Call과 관련된 CallMessage, Elder를 함께 조회 (eager loading)
    result = await db.execute(
        select(Call)
        .options(
            selectinload(Call.messages),
            selectinload(Call.elder)
        )
        .where(Call.id == call_id)
    )
    call = result.scalar_one_or_none()
    
    if not call:
        return None, ""
    
    elder_name = call.elder.name if call.elder else "알 수 없음"
    
    return call, elder_name

