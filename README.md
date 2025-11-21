# APNs Push Server

FastAPI 기반 iOS APNs 푸시 알림 서버 + Vapi 웹훅

## 📁 프로젝트 구조

```
server/
├── .env                    # 환경변수 (gitignore)
├── .env.example            # 환경변수 예시
├── requirements.txt        # Python 패키지
├── AuthKey_*.p8           # APNs 인증 키
│
├── app/
│   ├── main.py            # FastAPI 앱 엔트리포인트
│   │
│   ├── core/              # 핵심 설정
│   │   ├── config.py      # 환경변수 관리
│   │   └── security.py    # JWT 생성
│   │
│   ├── models/            # Pydantic 모델
│   │   └── push.py
│   │
│   ├── services/          # 비즈니스 로직
│   │   └── apns.py        # APNs 푸시 전송
│   │
│   └── routers/           # API 엔드포인트
│       ├── push.py        # /push, /push/voip
│       ├── webhook.py     # /vapi/webhook
│       └── health.py      # /, /health
```

## 🚀 시작하기

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env.example`을 복사해서 `.env` 파일을 만들고, 실제 값을 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 예시:

```env
TEAM_ID=U77SWC9NZT
KEY_ID=5XFZZ6ZD2H
BUNDLE_ID=com.stevenkim.CallClient
P8_PRIVATE_KEY_PATH=AuthKey_5XFZZ6ZD2H.p8

DEVICE_TOKEN=your_actual_device_token
VOIP_DEVICE_TOKEN=your_actual_voip_token

APNS_ENV=sandbox  # sandbox 또는 production
DEBUG=True
```

### 3. 서버 실행

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

## 🔧 개발

### 새 라우터 추가

1. `app/routers/`에 새 파일 생성
2. `APIRouter` 정의
3. `app/main.py`에서 `include_router()` 호출

### 새 서비스 추가

1. `app/services/`에 새 파일 생성
2. 비즈니스 로직 구현
3. 라우터에서 `Depends()`로 주입

## 📝 참고사항

- **APNs 환경**:
  - `sandbox`: Xcode로 빌드한 개발용 앱
  - `production`: TestFlight, App Store 배포용
- **디바이스 토큰**: iOS 앱에서 출력된 토큰을 `.env`에 입력
- **JWT 갱신**: APNs JWT는 자동으로 매 요청마다 새로 생성됨 (1시간 유효)

## 🔐 보안

- `.env` 파일은 절대 Git에 커밋하지 마세요
- `AuthKey_*.p8` 파일도 안전하게 관리하세요
- 프로덕션에서는 디바이스 토큰을 DB에 저장하세요
