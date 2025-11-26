"""대시보드 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from math import ceil

from app.db.session import get_db
from app.db.models.elder import Elder
from app.db.models.call_schedule import CallSchedule
from app.schemas.dashboard import DashboardResponse, CallListResponse, CallDetailResponse, CallMessageItem
from app.services.dashboard import (
    build_elder_basic_info,
    get_weekly_stats,
    get_recent_calls,
    get_today_highlight,
    find_next_scheduled_call,
    build_weekly_schedule,
    get_week_range,
    get_call_list_paginated,
    get_call_detail_by_id,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{elder_id}", response_model=DashboardResponse)
async def get_dashboard(
    elder_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    보호자 웹 대시보드용 종합 데이터 반환 (MVP)
    
    - **elder_id**: 어르신 ID
    
    Returns:
        대시보드 종합 데이터:
        - elder: 어르신 기본 정보 및 서비스 경과일
        - today_highlight: 오늘의 하이라이트 (오늘 통화가 있는 경우)
        - weekly_stats: 이번 주 통화 통계
        - recent_calls: 최근 통화 기록 10개
        - next_scheduled_call: 다음 예정 통화
        - this_week_schedule: 이번 주 월~일 일정
    
    TODO: 추후 이메일 검증을 통한 사용자 인증 추가 예정
    """
    # 1. 어르신 정보 조회
    result = await db.execute(
        select(Elder).where(Elder.id == elder_id)
    )
    elder = result.scalar_one_or_none()
    
    if not elder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 어르신을 찾을 수 없습니다"
        )
    
    # 2. 어르신 기본 정보 구성
    elder_info = await build_elder_basic_info(elder)
    
    # 3. 이번 주 범위 계산 (월요일 00:00 ~ 다음 주 월요일 00:00)
    week_start, week_end = get_week_range()
    
    # 4. 주간 통화 통계
    weekly_stats = await get_weekly_stats(
        db=db,
        elder_id=elder_id,
        week_start=week_start,
        week_end=week_end
    )
    
    # 5. 최근 통화 기록 (최근 10개)
    recent_calls = await get_recent_calls(
        db=db,
        elder_id=elder_id,
        limit=10
    )
    
    # 6. 오늘의 하이라이트 추출
    today_highlight = get_today_highlight(recent_calls)
    
    # 7. CallSchedule 조회
    schedule_result = await db.execute(
        select(CallSchedule).where(CallSchedule.elder_id == elder_id)
    )
    call_schedules = schedule_result.scalars().all()
    
    # 8. 다음 예정 통화 찾기
    next_scheduled_call = find_next_scheduled_call(call_schedules)
    
    # 9. 이번 주 일정 구성 (월~일)
    this_week_schedule = build_weekly_schedule(call_schedules, week_start)
    
    # 10. 최종 응답 구성
    return DashboardResponse(
        elder=elder_info,
        today_highlight=today_highlight,
        weekly_stats=weekly_stats,
        recent_calls=recent_calls,
        next_scheduled_call=next_scheduled_call,
        this_week_schedule=this_week_schedule
    )


@router.get("/{elder_id}/call-list", response_model=CallListResponse)
async def get_call_list(
    elder_id: int,
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    db: AsyncSession = Depends(get_db)
):
    """
    통화 목록 페이지네이션 조회 (MVP)
    
    - **elder_id**: 어르신 ID
    - **page**: 페이지 번호 (기본값: 1, 최소값: 1)
    
    Returns:
        통화 목록 페이지네이션 응답:
        - items: 통화 항목 리스트 (5개씩)
        - total: 전체 통화 개수
        - page: 현재 페이지 번호
        - page_size: 페이지당 항목 수 (5개 고정)
        - total_pages: 전체 페이지 수
    """
    # 1. 어르신 존재 여부 확인
    result = await db.execute(
        select(Elder).where(Elder.id == elder_id)
    )
    elder = result.scalar_one_or_none()
    
    if not elder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 어르신을 찾을 수 없습니다"
        )
    
    # 2. 페이지네이션 데이터 조회
    page_size = 5
    items, total = await get_call_list_paginated(
        db=db,
        elder_id=elder_id,
        page=page,
        page_size=page_size
    )
    
    # 3. 전체 페이지 수 계산
    total_pages = ceil(total / page_size) if total > 0 else 1
    
    # 4. 응답 반환
    return CallListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/call-detail/{call_id}", response_model=CallDetailResponse)
async def get_call_detail(
    call_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    통화 상세 정보 조회 (MVP)
    
    - **call_id**: 통화 ID
    
    Returns:
        통화 상세 정보:
        - 통화 기본 정보 (일시, 시간, 대상, 상태)
        - 상태 분석 (emotion)
        - AI 요약 (summary)
        - 키워드 태그 (tags)
        - 대화 전체 로그 (messages)
    """
    # 1. Call과 관련 데이터 조회
    call, elder_name = await get_call_detail_by_id(db, call_id)
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 통화를 찾을 수 없습니다"
        )
    
    # 2. 날짜/시간 포맷팅
    # 날짜: "2023년 10월 27일"
    date_str = call.started_at.strftime("%Y년 %m월 %d일")
    # 시간: "10:30 AM"
    time_str = call.started_at.strftime("%I:%M %p")
    
    # 3. 통화 시간 계산 (분:초)
    if call.ended_at:
        duration_seconds = int((call.ended_at - call.started_at).total_seconds())
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        duration_str = f"{minutes}분 {seconds}초"
    else:
        duration_str = "0분 0초"
    
    # 4. tags가 None이면 빈 리스트
    tags = call.tags if call.tags else []
    
    # 5. CallMessage를 CallMessageItem으로 변환
    message_items = [
        CallMessageItem(
            role=msg.role,
            message=msg.message,
            timestamp=msg.timestamp
        )
        for msg in sorted(call.messages, key=lambda m: m.timestamp)
    ]
    
    # 6. 응답 반환
    return CallDetailResponse(
        id=call.id,
        elder_name=elder_name,
        date=date_str,
        time=time_str,
        duration=duration_str,
        status=call.status,
        emotion=call.emotion,
        summary=call.summary,
        tags=tags,
        messages=message_items
    )

