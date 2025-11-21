# APNs Push Server

FastAPI 기반 iOS APNs 푸시 알림 서버 + Vapi 웹훅 + SQLite/PostgreSQL 지원

## 📁 프로젝트 구조

```
server/
├── .env                    # 환경변수 (gitignore)
├── .env.example            # 환경변수 예시
├── requirements.txt        # Python 패키지
├── AuthKey_*.p8           # APNs 인증 키
│
├── alembic/               # DB 마이그레이션
│   ├── env.py             # Alembic async 설정
│   └── versions/          # 마이그레이션 히스토리
├── alembic.ini            # Alembic 설정
│
├── data/                  # SQLite DB 파일 (gitignore)
│   └── app.db
│
└── app/
    ├── main.py            # FastAPI 앱 엔트리포인트
    │
    ├── core/              # 핵심 설정
    │   ├── config.py      # 환경변수 관리 (DATABASE_URL 포함)
    │   └── security.py    # JWT 생성
    │
    ├── db/                # 데이터베이스
    │   ├── base.py        # SQLAlchemy Base 클래스
    │   ├── session.py     # Async Engine, SessionLocal, get_db
    │   └── models/        # SQLAlchemy 모델 (DB 테이블)
    │       └── user.py    # User 모델
    │
    ├── schemas/           # Pydantic 모델 (API 요청/응답)
    │   └── push.py        # 푸시 관련 스키마
    │
    ├── services/          # 비즈니스 로직
    │   └── apns.py        # APNs 푸시 전송
    │
    └── routers/           # API 엔드포인트
        ├── push.py        # /push, /push/voip
        ├── webhook.py     # /vapi/webhook
        └── health.py      # /, /health
```

## 🚀 시작하기

### 1. 패키지 설치

```bash
# venv,Conda등 가성환경 활성화 (예: fastapi 또는 push)

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env.example`을 복사해서 `.env` 파일을 만들고, 실제 값을 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 예시:

```env
# Apple APNs
TEAM_ID=U77SWC9NZT
KEY_ID=5XFZZ6ZD2H
BUNDLE_ID=com.stevenkim.CallClient
P8_PRIVATE_KEY_PATH=AuthKey_5XFZZ6ZD2H.p8

# 디바이스 토큰 (개발용)
DEVICE_TOKEN=your_actual_device_token
VOIP_DEVICE_TOKEN=your_actual_voip_token

# APNs 환경
APNS_ENV=sandbox  # sandbox 또는 production

# 데이터베이스
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
# PostgreSQL로 전환 시:
# DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# 서버 설정
DEBUG=True
```

### 3. 데이터베이스 마이그레이션

```bash
# 초기 마이그레이션 생성 (첫 실행 시)
alembic revision --autogenerate -m "initial user table"

# DB에 적용
alembic upgrade head
```

### 4. 서버 실행

```bash
uvicorn app.main:app --reload
```

또는 포트를 지정하려면:

```bash
uvicorn app.main:app --reload --port 8000
```

## 📡 API 엔드포인트

### 헬스체크

```bash
# 기본 헬스체크
GET http://localhost:8000/

# 상세 헬스체크
GET http://localhost:8000/health
```

### 일반 알림 푸시

```bash
POST http://localhost:8000/push/
Content-Type: application/json

{
  "title": "테스트 푸시",
  "body": "안녕하세요!"
}
```

### VoIP 푸시

```bash
POST http://localhost:8000/push/voip
Content-Type: application/json

{
  "ai_call_id": "call_123"
}
```

### Vapi 웹훅

```bash
POST http://localhost:8000/vapi/webhook
Content-Type: application/json

{
  "message": {
    "type": "end-of-call-report",
    "transcript": "통화 내용..."
  }
}
```

## 📚 API 문서

서버 실행 후 자동 생성되는 문서:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🗄️ 데이터베이스

### 현재 구조

- **SQLite** (개발용): `data/app.db`
- **SQLAlchemy 2.0** (async)
- **Alembic** (마이그레이션)

### 모델

#### User

- `id`: Integer (Primary Key)
- `email`: String (Unique, Indexed)
- `created_at`: DateTime
- `updated_at`: DateTime

### DB 사용 예시

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models.user import User

@app.post("/users")
async def create_user(email: str, db: AsyncSession = Depends(get_db)):
    user = User(email=email)
    db.add(user)
    await db.flush()
    return {"id": user.id, "email": user.email}

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
```

### PostgreSQL로 전환

1. **패키지 설치**:

   ```bash
   pip install asyncpg
   ```

2. **환경변수 변경** (`.env`):

   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
   ```

3. **코드 변경 없음!** SQLAlchemy가 자동 처리합니다.

### Alembic 명령어

```bash
# 새 마이그레이션 생성 (모델 변경 후)
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 되돌리기
alembic downgrade -1

# 마이그레이션 히스토리 확인
alembic history

# 현재 버전 확인
alembic current
```

## 🔧 개발

### 새 라우터 추가

1. `app/routers/`에 새 파일 생성
2. `APIRouter` 정의
3. `app/main.py`에서 `include_router()` 호출

### 새 서비스 추가

1. `app/services/`에 새 파일 생성
2. 비즈니스 로직 구현
3. 라우터에서 `Depends()`로 주입

### 새 DB 모델 추가

1. `app/db/models/`에 새 파일 생성 (예: `device.py`)
2. SQLAlchemy 모델 정의:

   ```python
   from sqlalchemy.orm import Mapped, mapped_column
   from app.db.base import Base

   class Device(Base):
       __tablename__ = "devices"
       id: Mapped[int] = mapped_column(primary_key=True)
       # ...
   ```

3. `app/db/models/__init__.py`에 import 추가:
   ```python
   from app.db.models.device import Device
   __all__ = ["User", "Device"]
   ```
4. 마이그레이션 생성 및 적용:
   ```bash
   alembic revision --autogenerate -m "add device table"
   alembic upgrade head
   ```

### API 스키마 추가

1. `app/schemas/`에 새 파일 생성
2. Pydantic 모델 정의
3. 라우터에서 사용

## 📝 참고사항

- **APNs 환경**:
  - `sandbox`: Xcode로 빌드한 개발용 앱
  - `production`: TestFlight, App Store 배포용
- **디바이스 토큰**: iOS 앱에서 출력된 토큰을 `.env`에 입력
- **JWT 갱신**: APNs JWT는 자동으로 매 요청마다 새로 생성됨 (1시간 유효)
- **DB 자동 생성**: 서버 시작 시 테이블 자동 생성 (개발 편의용)
- **schemas vs models**:
  - `app/schemas/`: API 요청/응답용 Pydantic 모델
  - `app/db/models/`: DB 테이블용 SQLAlchemy 모델
- SQlite Viewer for VScode 설치: https://marketplace.cursorapi.com/items/?itemName=qwtel.sqlite-viewer

## 🔐 보안

- `.env` 파일은 절대 Git에 커밋하지 마세요
- `AuthKey_*.p8` 파일도 안전하게 관리하세요
- `data/` 디렉토리는 `.gitignore`에 포함됨 (SQLite DB)
- 프로덕션에서는 디바이스 토큰을 DB에 저장하세요
- 프로덕션에서는 PostgreSQL 사용을 권장합니다

## 🐛 트러블슈팅

### 마이그레이션 충돌

```bash
# 마이그레이션 초기화 (개발 단계에서만)
rm -rf alembic/versions/*
rm data/app.db
alembic revision --autogenerate -m "initial"
alembic upgrade head
```
