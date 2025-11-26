#!/usr/bin/env python3
"""
VoIP 푸시 테스트 스크립트

사용법:
    python test_voip_push.py

이 스크립트는:
1. 서버가 실행 중인지 확인
2. VoIP 푸시 전송
3. APNs 응답 분석
4. 문제 진단
"""

import asyncio
import httpx
from datetime import datetime


BASE_URL = "http://localhost:8000"
ELDER_ID = 1  # 테스트할 어르신 ID


def print_section(title: str):
    """섹션 제목 출력"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


async def check_server():
    """서버 상태 확인"""
    print_section("1️⃣  서버 상태 확인")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ 서버가 정상 실행 중입니다.")
                return True
            else:
                print(f"⚠️  서버 응답: {response.status_code}")
                return False
    except httpx.ConnectError:
        print("❌ 서버에 연결할 수 없습니다.")
        print("   서버를 먼저 실행하세요: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


async def send_voip_push():
    """VoIP 푸시 전송"""
    print_section("2️⃣  VoIP 푸시 전송")
    
    print(f"📞 Elder ID {ELDER_ID}에게 VoIP 푸시 전송 중...")
    print(f"⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/push/voip",
                json={"elder_id": ELDER_ID},
                timeout=10.0
            )
            
            print(f"📬 서버 응답: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"❌ 오류 응답:")
                print(response.text)
                return None
                
    except Exception as e:
        print(f"❌ 오류: {e}")
        return None


def analyze_response(data: dict):
    """APNs 응답 분석"""
    print_section("3️⃣  APNs 응답 분석")
    
    status_code = data.get("status_code")
    apns_id = data.get("apns_id")
    body = data.get("body", "")
    
    print(f"Status Code: {status_code}")
    print(f"APNs ID: {apns_id}")
    print(f"Body: {body if body else '(empty)'}\n")
    
    # 상태 코드별 분석
    if status_code == 200:
        print("✅ 성공! APNs로 푸시가 전송되었습니다.")
        print("\n📱 이제 iOS 기기를 확인하세요:")
        print("   - CallKit 전화 UI가 떠야 합니다")
        print("   - 안 뜬다면 아래 원인을 확인하세요\n")
        
    elif status_code == 400:
        print("❌ 400 Bad Request - 잘못된 요청")
        print("\n원인:")
        print("  - apns-topic이 잘못되었을 수 있음")
        print("  - apns-push-type이 'voip'가 아닐 수 있음")
        print("  - 페이로드 형식이 잘못되었을 수 있음")
        print("\n해결:")
        print("  - server/app/core/config.py의 BUNDLE_ID 확인")
        print("  - server/app/services/apns.py의 headers 확인\n")
        
    elif status_code == 403:
        print("❌ 403 Forbidden - 인증 오류")
        print("\n원인:")
        print("  - JWT 토큰이 잘못되었음")
        print("  - P8 키가 잘못되었음")
        print("  - TEAM_ID, KEY_ID가 잘못되었음")
        print("\n해결:")
        print("  - .env 파일의 TEAM_ID, KEY_ID 재확인")
        print("  - P8_PRIVATE_KEY_PATH 파일 확인")
        print("  - Apple Developer에서 키 상태 확인\n")
        
    elif status_code == 410:
        print("❌ 410 Gone - 토큰 무효")
        print("\n원인:")
        print("  - iOS가 VoIP 토큰을 무효화했음")
        print("  - 앱이 삭제되었거나 재설치되었음")
        print("  - 시스템이 앱의 VoIP 푸시를 차단했음")
        print("\n해결:")
        print("  ⚠️  이것이 가장 흔한 원인입니다!")
        print("  1. 기기에서 앱 완전 삭제")
        print("  2. 기기 재부팅 (필수!)")
        print("  3. 앱 재설치")
        print("  4. Xcode 콘솔에서 새 VoIP 토큰 확인")
        print("  5. DB에 새 토큰 업데이트:")
        print("     python")
        print("     >>> import sqlite3")
        print("     >>> conn = sqlite3.connect('data/app.db')")
        print(f"     >>> conn.execute('UPDATE elders SET voip_device_token = ? WHERE id = ?', ('새토큰', {ELDER_ID}))")
        print("     >>> conn.commit()\n")
        
    else:
        print(f"❌ 알 수 없는 상태 코드: {status_code}")
        print(f"Body: {body}\n")


def print_troubleshooting():
    """문제 해결 가이드"""
    print_section("4️⃣  앱 종료 시 푸시가 안 올 때")
    
    print("📋 체크리스트:\n")
    
    print("□ 1. 서버 응답이 200인가?")
    print("     → YES: APNs로는 전송됨. iOS 측 문제")
    print("     → NO: 서버/APNs 설정 문제\n")
    
    print("□ 2. 백그라운드에서는 오는가?")
    print("     → YES: 코드는 정상. iOS 정책 문제")
    print("     → NO: 코드/설정 문제\n")
    
    print("□ 3. 앱을 어떻게 종료했는가?")
    print("     → 위로 스와이프: iOS가 VoIP 차단할 수 있음")
    print("     → 홈 버튼 후 자연스럽게: 정상 방법\n")
    
    print("□ 4. 이전에 앱이 강제종료된 적이 있는가?")
    print("     → YES: iOS가 앱을 신뢰하지 않음. 완전 초기화 필요")
    print("     → NO: 다른 원인\n")
    
    print("\n🔧 해결 방법 (순서대로):\n")
    
    print("1️⃣  올바른 테스트 방법:")
    print("   - 앱 실행")
    print("   - 홈 버튼으로 백그라운드 (위로 스와이프 NO!)")
    print("   - 30초~1분 기다림 (iOS가 자연스럽게 종료)")
    print("   - 푸시 전송")
    print("   - CallKit UI 확인\n")
    
    print("2️⃣  완전 초기화 (APNs 410 에러 또는 계속 안 될 때):")
    print("   - 앱 완전 삭제 (데이터까지)")
    print("   - 기기 완전 재부팅 (필수!)")
    print("   - Xcode Clean Build (Cmd+Shift+K)")
    print("   - 앱 재설치")
    print("   - 새 VoIP 토큰 DB 업데이트")
    print("   - 위의 올바른 테스트 방법으로 재시도\n")
    
    print("3️⃣  개발 빌드의 한계:")
    print("   - Debug 빌드는 VoIP가 불안정할 수 있음")
    print("   - Release/AdHoc 빌드가 더 안정적")
    print("   - TestFlight 배포가 가장 안정적\n")
    
    print("\n💡 자세한 가이드:")
    print("   ios/VOIP_RESET_GUIDE.md 참고\n")


async def main():
    """메인 함수"""
    print("\n🚀 VoIP 푸시 테스트 시작")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 서버 확인
    if not await check_server():
        return
    
    # VoIP 푸시 전송
    data = await send_voip_push()
    
    if data:
        # 응답 분석
        analyze_response(data)
    
    # 문제 해결 가이드
    print_troubleshooting()
    
    print("\n" + "="*70)
    print("✅ 테스트 완료")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

