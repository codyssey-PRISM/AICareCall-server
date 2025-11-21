"""인증 관련 Pydantic 스키마"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class CodeRequest(BaseModel):
    """인증 코드 요청"""
    email: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class CodeResponse(BaseModel):
    """인증 코드 응답"""
    success: bool
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "인증 코드가 이메일로 전송되었습니다"
            }
        }


class VerifyRequest(BaseModel):
    """인증 코드 검증 요청"""
    email: str
    code: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "code": "123456"
            }
        }


class UserInfo(BaseModel):
    """사용자 정보"""
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "created_at": "2024-01-01T00:00:00"
            }
        }


class VerifyResponse(BaseModel):
    """인증 코드 검증 응답"""
    success: bool
    message: str
    user: Optional[UserInfo] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "인증 성공",
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "created_at": "2024-01-01T00:00:00"
                }
            }
        }

