"""인증 코드 관리 서비스 (MVP - 딕셔너리 기반)"""
import random
from datetime import datetime, timedelta
from typing import Dict, Optional

# 인메모리 저장소: {email: {code: str, expires_at: datetime}}
auth_codes: Dict[str, Dict] = {}

# 코드 유효 시간 (초)
CODE_EXPIRE_SECONDS = 300  # 5분


def generate_code(email: str) -> str:
    """
    6자리 랜덤 숫자 코드 생성 및 저장
    
    같은 이메일로 재요청 시 기존 코드를 덮어씁니다.
    
    Args:
        email: 사용자 이메일
        
    Returns:
        str: 6자리 숫자 코드
    """
    # 6자리 랜덤 숫자 생성 (000000 ~ 999999)
    code = str(random.randint(0, 999999)).zfill(6)
    
    # 만료 시간 계산
    expires_at = datetime.now() + timedelta(seconds=CODE_EXPIRE_SECONDS)
    
    # 저장 (기존 코드가 있으면 덮어쓰기)
    auth_codes[email] = {
        "code": code,
        "expires_at": expires_at,
    }
    
    print(f"🔐 Generated code for {email}: {code} (expires at {expires_at})")
    return code


def verify_code(email: str, code: str) -> tuple[bool, Optional[str]]:
    """
    인증 코드 검증
    
    Args:
        email: 사용자 이메일
        code: 검증할 6자리 코드
        
    Returns:
        tuple[bool, Optional[str]]: (성공 여부, 에러 메시지)
            - (True, None): 인증 성공
            - (False, "message"): 인증 실패 (이유 포함)
    """
    # 입력값 검증
    if not email or not code:
        return False, "이메일과 인증 코드를 모두 입력해주세요"
    
    # 코드 형식 검증 (6자리 숫자)
    if not code.isdigit() or len(code) != 6:
        return False, "인증 코드는 6자리 숫자여야 합니다"
    
    # 해당 이메일로 발급된 코드가 없는 경우
    if email not in auth_codes:
        return False, "인증 코드가 발급되지 않았습니다"
    
    stored_data = auth_codes[email]
    stored_code = stored_data["code"]
    expires_at = stored_data["expires_at"]
    
    # 만료 시간 체크
    if datetime.now() > expires_at:
        # 만료된 코드는 삭제
        del auth_codes[email]
        return False, "인증 코드가 만료되었습니다 (5분)"
    
    # 코드 일치 여부 확인
    if stored_code != code:
        return False, "인증 코드가 일치하지 않습니다"
    
    # 인증 성공 시 사용된 코드 삭제 (재사용 방지)
    del auth_codes[email]
    print(f"✅ Code verified successfully for {email}")
    
    return True, None

