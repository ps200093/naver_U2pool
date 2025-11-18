"""
모바일 에뮬레이션 테스트 스크립트
간단하게 모바일 드라이버를 테스트할 수 있습니다.
"""
import time
import logging
from src.mobile_driver import MobileDriver


def test_single_device(device_name="galaxy_s24"):
    """단일 기기 테스트"""
    print(f"\n{'='*60}")
    print(f"🔍 {device_name} 테스트 시작")
    print(f"{'='*60}\n")
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 드라이버 생성
    mobile = MobileDriver(
        headless=False,  # 브라우저를 보려면 False
        device=device_name
    )
    
    driver = mobile.create_driver()
    
    try:
        print("\n1️⃣ 네이버 모바일 접속 중...")
        driver.get("https://m.naver.com")
        time.sleep(3)
        print("✅ 네이버 모바일 접속 성공!\n")

        input("엔터를 누르면 다음 테스트로 이동합니다...")

        
        print("2️⃣ User Agent 확인 페이지 접속 중...")
        time.sleep(2)
        driver.get("https://www.whatismybrowser.com/detect/what-is-my-user-agent")
        time.sleep(5)
        print("✅ User Agent 확인 페이지 로드 완료!\n")
        
        print("3️⃣ 모바일 감지 테스트 페이지 접속 중...")
        time.sleep(2)
        driver.get("https://whatismyviewport.com/")
        time.sleep(5)
        print("✅ 뷰포트 확인 완료!\n")
        
        # JavaScript로 정보 확인
        print("\n" + "="*60)
        print("📱 브라우저 정보 확인")
        print("="*60)
        
        info = driver.execute_script("""
            return {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                mobile: /Android|iPhone|iPad|iPod/i.test(navigator.userAgent),
                touchPoints: navigator.maxTouchPoints,
                width: window.screen.width,
                height: window.screen.height,
                vendor: navigator.vendor,
                language: navigator.language
            };
        """)
        
        print(f"User Agent: {info['userAgent'][:80]}...")
        print(f"플랫폼: {info['platform']}")
        print(f"모바일 감지: {info['mobile']}")
        print(f"터치 포인트: {info['touchPoints']}")
        print(f"화면 크기: {info['width']}x{info['height']}")
        print(f"Vendor: {info['vendor']}")
        print(f"언어: {info['language']}")
        print("="*60 + "\n")
        
        print("✅ 모든 테스트 완료!")
        print("\n브라우저를 확인하세요.")
        print("종료하려면 엔터를 누르세요...")
        input()
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n드라이버 종료 중...")
        mobile.quit_driver(driver)
        print("✅ 종료 완료!")


def test_all_devices():
    """모든 기기 순차 테스트"""
    devices = ["galaxy_s24", "galaxy_s23", "iphone_15_pro", "iphone_14"]
    
    print("\n" + "="*60)
    print("🔄 모든 기기 테스트 시작")
    print("="*60 + "\n")
    
    for device in devices:
        print(f"\n▶️ {device} 테스트 중...")
        
        mobile = MobileDriver(headless=False, device=device)
        driver = mobile.create_driver()
        
        try:
            driver.get("https://m.naver.com")
            time.sleep(3)
            
            # 간단한 정보 출력
            platform = driver.execute_script("return navigator.platform")
            mobile_detected = driver.execute_script(
                "return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)"
            )
            
            print(f"   플랫폼: {platform}")
            print(f"   모바일 감지: {mobile_detected}")
            print(f"   ✅ {device} 테스트 완료!\n")
            

            time.sleep(2)
            
        except Exception as e:
            print(f"   ❌ {device} 테스트 실패: {e}\n")
            
        finally:
            mobile.quit_driver(driver)
    
    print("\n" + "="*60)
    print("✅ 모든 기기 테스트 완료!")
    print("="*60 + "\n")


def interactive_test():
    """대화형 테스트"""
    print("\n" + "="*60)
    print("🎯 모바일 에뮬레이션 대화형 테스트")
    print("="*60 + "\n")
    
    print("사용 가능한 기기:")
    print("  1. galaxy_s24    (Galaxy S24 Ultra)")
    print("  2. galaxy_s23    (Galaxy S23)")
    print("  3. iphone_15_pro (iPhone 15 Pro)")
    print("  4. iphone_14     (iPhone 14)")
    print("  5. 모든 기기 테스트")
    
    choice = input("\n선택하세요 (1-5): ").strip()
    
    device_map = {
        "1": "galaxy_s24",
        "2": "galaxy_s23",
        "3": "iphone_15_pro",
        "4": "iphone_14"
    }
    
    if choice in device_map:
        test_single_device(device_map[choice])
    elif choice == "5":
        test_all_devices()
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    # 단일 기기 테스트
    test_single_device("galaxy_s24")
    
    # 또는 대화형 테스트
    # interactive_test()
    
    # 또는 모든 기기 테스트
    # test_all_devices()

