"""Elder 앱 관련 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.elder import VerifyInviteCodeRequest, VerifyInviteCodeResponse
from app.services.elder import ElderService
from app.services.call import CallService

router = APIRouter(prefix="/elder-app", tags=["elder-app"])


@router.post("/invitation-code", response_model=VerifyInviteCodeResponse, status_code=status.HTTP_200_OK)
async def register_invitation_code(
    request: VerifyInviteCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    초대 코드를 검증하고 VoIP 디바이스 토큰을 등록
    
    - **invite_code**: 초대 코드 (6자리)
    - **voip_device_token**: VoIP 디바이스 토큰
    
    Returns:
        성공 시 어르신 정보와 함께 성공 메시지 반환
    
    Raises:
        404: 초대 코드가 유효하지 않음
        409: 이미 등록된 초대 코드
    """
    try:
        elder = await ElderService.verify_and_register_device(
            db=db,
            invite_code=request.invite_code,
            voip_device_token=request.voip_device_token
        )
        
        return VerifyInviteCodeResponse(
            success=True,
            elder_id=elder.id,
            elder_name=elder.name,
            message="디바이스가 성공적으로 등록되었습니다."
        )
    except ValueError as e:
        error_msg = str(e)
        
        # 초대 코드가 유효하지 않은 경우
        if "유효하지 않습니다" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        # 이미 등록된 경우
        elif "이미 등록된" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg
            )
        # 기타 에러
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"디바이스 등록 중 오류가 발생했습니다: {str(e)}"
            )


@router.get("/assistant-config/{elder_id}")
async def get_assistant_config(
    elder_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    특정 어르신의 Vapi Assistant 설정 조회
    
    VoIP push를 받은 iOS 앱이 이 API를 호출하여 
    통화에 필요한 전체 assistant configuration을 가져갑니다.
    
    - **elder_id**: 어르신 ID
    
    Returns:
        Vapi Assistant 설정 딕셔너리
    
    Raises:
        404: 어르신을 찾을 수 없음
    """
    try:
        elder = await ElderService.get_elder_by_id(db=db, elder_id=elder_id)
        
        if not elder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="어르신을 찾을 수 없습니다."
            )
        
        # CallService를 통해 assistant config 생성
        assistant_config = await CallService.get_assistant_config(elder)
        
        return assistant_config
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assistant 설정 조회 중 오류가 발생했습니다: {str(e)}"
        )

