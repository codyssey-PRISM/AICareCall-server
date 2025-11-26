# Seed Data 사용 가이드

## 파일 설명

### 1. `user-elder-no-token-seed.py`
- 기본 User와 Elder 데이터만 생성
- VoIP 토큰 없이 간단한 테스트용

### 2. `dashboard_test_seed.py` ⭐️ 추천
- 대시보드 API 테스트용 종합 더미 데이터
- 포함 데이터:
  - Users (보호자 3명)
  - Elders (어르신 5명)
  - CallSchedules (매일 아침 9시, 저녁 8시)
  - Calls (최근 14일간의 통화 기록)
  - CallMessages (실제 대화 내용)

## 사용 방법

### 1. 데이터베이스 초기화 (선택사항)

기존 데이터를 모두 삭제하고 새로 시작하려면:

```bash
cd /Users/seungwookim/Code/Test/vapi/server
rm data/app.db
alembic upgrade head
```

### 2. 시드 데이터 생성

#### 종합 테스트 데이터 생성 (추천)
```bash
python -m seed.dashboard_test_seed
```

#### 간단한 테스트 데이터만 생성
```bash
python -m seed.user-elder-no-token-seed
```

## 생성되는 데이터

### Users (보호자)
- guardian1@example.com
- guardian2@example.com
- guardian3@example.com

### Elders (각 보호자별로 연결)
1. 김영희 (75세, 여, 어머니) - guardian1
2. 김철수 (78세, 남, 아버지) - guardian1
3. 박순자 (82세, 여, 할머니) - guardian2
4. 이만수 (80세, 남, 할아버지) - guardian2
5. 최영란 (73세, 여, 어머니) - guardian3

### CallSchedules
- 각 어르신별로 주중 아침 9시, 매일 저녁 8시 스케줄

### Calls & CallMessages
- 최근 14일간 하루 1-2회 통화
- 각 통화마다 실제 대화 내용 포함
- 요약, 감정 분석, 태그 데이터 포함

## API 테스트 예시

시드 데이터 생성 후 다음과 같이 테스트할 수 있습니다:

```bash
# 서버 시작
uvicorn app.main:app --reload

# 다른 터미널에서 API 테스트
# 1. 특정 보호자의 어르신 목록 조회
curl http://localhost:8000/api/elders?user_id=1

# 2. 특정 어르신의 통화 기록 조회
curl http://localhost:8000/api/calls?elder_id=1

# 3. 특정 통화의 상세 정보 조회
curl http://localhost:8000/api/calls/1
```

## 트러블슈팅

### 에러: `ModuleNotFoundError: No module named 'app'`
- 현재 디렉토리가 `/server`인지 확인
- `python -m seed.dashboard_test_seed` 형식으로 실행

### 에러: `database is locked`
- 다른 프로세스에서 DB를 사용 중인지 확인
- API 서버를 중지하고 다시 시도

### 에러: `UNIQUE constraint failed`
- 이미 데이터가 존재함
- 데이터베이스를 초기화하고 다시 시도
