"""대시보드 API 응답 스키마"""
from datetime import datetime
from pydantic import BaseModel, Field


class ElderBasicInfo(BaseModel):
    """어르신 기본 정보"""
    id: int
    name: str
    relation: str
    service_days: int
    
    class Config:
        from_attributes = True


class TodayHighlight(BaseModel):
    """오늘의 하이라이트"""
    message: str
    call_time: str
    emotion: str
    tags: list[str]
    
    class Config:
        from_attributes = True


class CallAttemptsStats(BaseModel):
    """통화 시도 통계"""
    count: int


class CallSuccessStats(BaseModel):
    """통화 성공 통계"""
    count: int


class AvgDurationStats(BaseModel):
    """평균 통화 시간 통계"""
    minutes: int


class WeeklyStats(BaseModel):
    """주간 통계"""
    call_attempts: CallAttemptsStats
    call_success_count: CallSuccessStats
    avg_duration: AvgDurationStats
    
    class Config:
        from_attributes = True


class RecentCallItem(BaseModel):
    """최근 통화 항목"""
    id: int
    date: str  # "2025.01.19" 형식
    time: str  # "10:30" 형식
    duration_minutes: int
    summary: str
    tags: list[str]
    emotion: str | None
    status: str  # completed, missed, failed
    
    class Config:
        from_attributes = True


class NextScheduledCall(BaseModel):
    """다음 예정 통화"""
    datetime: datetime
    date_display: str  # "2025년 1월 20일"
    time_display: str  # "10:00"
    is_today: bool
    
    class Config:
        from_attributes = True


class WeeklyScheduleItem(BaseModel):
    """주간 일정 항목"""
    day_of_week: str  # "월요일", "화요일" 등
    date: str  # "2025-01-20"
    date_display: str  # "1월 20일"
    scheduled_times: list[str]  # ["14:00"] 또는 []
    
    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    """대시보드 최종 응답"""
    elder: ElderBasicInfo
    today_highlight: TodayHighlight | None
    weekly_stats: WeeklyStats
    recent_calls: list[RecentCallItem]
    next_scheduled_call: NextScheduledCall | None
    this_week_schedule: list[WeeklyScheduleItem]
    
    class Config:
        from_attributes = True


class CallListResponse(BaseModel):
    """통화 목록 페이지네이션 응답"""
    items: list[RecentCallItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True


class CallMessageItem(BaseModel):
    """대화 메시지 항목"""
    role: str  # user, assistant
    message: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class CallDetailResponse(BaseModel):
    """통화 상세 응답"""
    id: int
    elder_name: str
    date: str  # "2023년 10월 27일"
    time: str  # "10:30 AM"
    duration: str  # "5분 32초"
    status: str  # completed, failed, no_answer
    emotion: str | None  # 좋음, 보통, 나쁨
    summary: str | None
    tags: list[str]
    messages: list[CallMessageItem]
    
    class Config:
        from_attributes = True

