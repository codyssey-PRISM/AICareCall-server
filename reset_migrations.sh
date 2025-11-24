#!/bin/bash

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Alembic 마이그레이션 초기화 스크립트${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# 현재 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}⚠️  경고: 이 스크립트는 다음을 삭제합니다:${NC}"
echo "  - data/app.db (데이터베이스)"
echo "  - alembic/versions/*.py (모든 마이그레이션 파일)"
echo ""
echo -e "${YELLOW}계속하시겠습니까? (y/N)${NC}"
read -r response

if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${RED}❌ 취소되었습니다.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🔄 초기화를 시작합니다...${NC}"
echo ""

# 1. 백업 생성 (선택사항)
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
echo -e "${YELLOW}📦 백업 생성 중: ../${BACKUP_DIR}${NC}"
mkdir -p "../${BACKUP_DIR}"
if [ -f "data/app.db" ]; then
    cp data/app.db "../${BACKUP_DIR}/app.db" 2>/dev/null && echo -e "${GREEN}   ✓ DB 백업 완료${NC}" || echo -e "${YELLOW}   - DB 없음${NC}"
fi
if ls alembic/versions/*.py 1> /dev/null 2>&1; then
    cp alembic/versions/*.py "../${BACKUP_DIR}/" 2>/dev/null && echo -e "${GREEN}   ✓ 마이그레이션 파일 백업 완료${NC}" || echo -e "${YELLOW}   - 마이그레이션 파일 없음${NC}"
fi
echo ""

# 2. DB 삭제
echo -e "${YELLOW}🗑️  기존 DB 삭제 중...${NC}"
if [ -f "data/app.db" ]; then
    rm -f data/app.db
    echo -e "${GREEN}   ✓ data/app.db 삭제 완료${NC}"
else
    echo -e "${YELLOW}   - data/app.db 파일이 없습니다${NC}"
fi
echo ""

# 3. 마이그레이션 파일 삭제
echo -e "${YELLOW}🗑️  기존 마이그레이션 파일 삭제 중...${NC}"
if ls alembic/versions/*.py 1> /dev/null 2>&1; then
    rm -f alembic/versions/*.py
    echo -e "${GREEN}   ✓ 마이그레이션 파일 삭제 완료${NC}"
else
    echo -e "${YELLOW}   - 마이그레이션 파일이 없습니다${NC}"
fi

if [ -d "alembic/versions/__pycache__" ]; then
    rm -rf alembic/versions/__pycache__
    echo -e "${GREEN}   ✓ __pycache__ 정리 완료${NC}"
fi
echo ""

# 4. 새 마이그레이션 생성
echo -e "${YELLOW}📝 새로운 초기 마이그레이션 생성 중...${NC}"
alembic revision --autogenerate -m "initial schema"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✓ 마이그레이션 생성 완료${NC}"
else
    echo -e "${RED}   ✗ 마이그레이션 생성 실패${NC}"
    exit 1
fi
echo ""

# 5. 마이그레이션 적용
echo -e "${YELLOW}⬆️  마이그레이션 적용 중...${NC}"
alembic upgrade head
if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✓ 마이그레이션 적용 완료${NC}"
else
    echo -e "${RED}   ✗ 마이그레이션 적용 실패${NC}"
    exit 1
fi
echo ""

# 6. 결과 확인
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  초기화 완료!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${GREEN}📊 현재 버전:${NC}"
alembic current
echo ""
echo -e "${GREEN}📜 마이그레이션 히스토리:${NC}"
alembic history
echo ""
echo -e "${GREEN}💾 백업 위치: ../${BACKUP_DIR}${NC}"
echo ""
echo -e "${GREEN}✅ 모든 작업이 완료되었습니다!${NC}"

