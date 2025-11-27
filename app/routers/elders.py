"""Elder 관련 API 라우터"""
import traceback
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.elder import ElderCreate, ElderResponse
from app.services.elder import ElderService

router = APIRouter(prefix="/users", tags=["elders"])


@router.post("/{user_id}/elders", response_model=ElderResponse, status_code=status.HTTP_201_CREATED)
async def create_elder(
    user_id: int,
    elder_data: ElderCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    새로운 어르신 등록
    
    - **user_id**: 사용자 ID
    - **elder_data**: 어르신 정보 및 통화 스케줄
    
    Returns:
        생성된 어르신 정보
    """
    try:
        print("=" * 80)
        print("🔍 [DEBUG] 어르신 등록 시작")
        print(f"   user_id: {user_id}")
        print(f"   elder_data: {elder_data.model_dump()}")
        print("=" * 80)
        
        elder = await ElderService.create_elder(
            db=db,
            user_id=user_id,
            elder_data=elder_data
        )
        
        print("✅ [SUCCESS] 어르신 등록 완료")
        print(f"   elder_id: {elder.id}")
        print("=" * 80)
        
        return elder
    except ValueError as e:
        # 보호자가 존재하지 않는 경우
        print(f"❌ [ERROR] ValueError 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # 상세한 에러 정보 출력
        print("=" * 80)
        print("❌ [ERROR] 어르신 등록 중 예외 발생")
        print(f"   에러 타입: {type(e).__name__}")
        print(f"   에러 메시지: {str(e)}")
        print("\n📋 상세 Traceback:")
        traceback.print_exc()
        print("=" * 80)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"어르신 등록 중 오류가 발생했습니다: {type(e).__name__}: {str(e)}"
        )


@router.get("/{user_id}/elders", response_model=list[ElderResponse])
async def get_user_elders(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    특정 사용자의 모든 어르신 목록 조회
    
    - **user_id**: 사용자 ID
    
    Returns:
        어르신 목록
    """
    elders = await ElderService.get_elders_by_user(db=db, user_id=user_id)
    return elders


@router.get("/{user_id}/elders/{elder_id}", response_model=ElderResponse)
async def get_elder(
    user_id: int,
    elder_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    특정 어르신 정보 조회
    
    - **user_id**: 사용자 ID
    - **elder_id**: 어르신 ID
    
    Returns:
        어르신 정보
    """
    elder = await ElderService.get_elder_by_id(db=db, elder_id=elder_id)
    
    if not elder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 어르신을 찾을 수 없습니다"
        )
    
    # 해당 어르신이 요청한 user_id의 소유인지 확인
    if elder.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다"
        )
    
    return elder


@router.post("/{user_id}/elders/{elder_id}/regenerate-invite-code", response_model=ElderResponse)
async def regenerate_invite_code(
    user_id: int,
    elder_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    초대 코드 재생성
    
    - **user_id**: 사용자 ID
    - **elder_id**: 어르신 ID
    
    Returns:
        업데이트된 어르신 정보 (새로운 초대 코드 포함)
    """
    try:
        elder = await ElderService.regenerate_invite_code(
            db=db,
            elder_id=elder_id,
            user_id=user_id
        )
        return elder
    except ValueError as e:
        error_msg = str(e)
        if "찾을 수 없습니다" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg
            )
