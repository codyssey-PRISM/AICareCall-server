"""인증 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.auth import CodeRequest, CodeResponse, VerifyRequest, VerifyResponse, UserInfo
from app.services.auth import generate_code, verify_code
from app.services.email import send_auth_code_email
from app.db.session import get_db
from app.db.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/code", response_model=CodeResponse)
async def request_auth_code(req: CodeRequest, db: AsyncSession = Depends(get_db)):
    """
    인증 코드 요청
    
    - 이메일을 입력하면 6자리 숫자 코드를 생성하여 이메일로 전송합니다
    - 코드는 5분간 유효합니다
    - 같은 이메일로 재요청 시 기존 코드는 무효화되고 새 코드가 발급됩니다
    """
    # 0. 이미 가입된 이메일인지 확인
    stmt = select(User).where(User.email == req.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="이미 가입된 이메일입니다"
        )
    
    # 1. 인증 코드 생성
    code = generate_code(req.email)
    
    # 2. 이메일로 코드 전송
    email_sent = await send_auth_code_email(req.email, code)
    
    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="이메일 전송에 실패했습니다. 잠시 후 다시 시도해주세요."
        )
    
    return CodeResponse(
        success=True,
        message="인증 코드가 이메일로 전송되었습니다"
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_auth_code(
    req: VerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    인증 코드 검증
    
    - 이메일과 코드를 입력하여 검증합니다
    - 성공 시:
      - User 테이블에 저장 (신규 유저인 경우)
      - User 정보를 반환합니다
    - 실패 시:
      - 코드 불일치 또는 만료 사유를 반환합니다
    """
    # 1. 코드 검증
    is_valid, error_message = verify_code(req.email, req.code)
    
    if not is_valid:
        return VerifyResponse(
            success=False,
            message=error_message,
            user=None
        )
    
    # 2. DB에서 사용자 조회 또는 생성
    stmt = select(User).where(User.email == req.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        # 신규 사용자 생성
        user = User(email=req.email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"👤 New user created: {user.email} (id={user.id})")
    else:
        print(f"👤 Existing user authenticated: {user.email} (id={user.id})")
    
    # 3. 성공 응답
    return VerifyResponse(
        success=True,
        message="인증 성공",
        user=UserInfo.model_validate(user)
    )

