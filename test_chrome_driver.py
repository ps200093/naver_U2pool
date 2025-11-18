"""
크롬 드라이버 동작 확인 스크립트
"""
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_chromedriver_basic():
    """기본 크롬 드라이버 테스트"""
    print("\n" + "="*60)
    print("🔍 크롬 드라이버 기본 테스트")
    print("="*60 + "\n")
    
    try:
        # 1. 드라이버 경로 확인
        driver_path = Path(__file__).parent / "drivers" / "chromedriver.exe"
        
        if driver_path.exists():
            print(f"✅ ChromeDriver 발견: {driver_path}")
        else:
            print(f"⚠️  ChromeDriver가 {driver_path}에 없습니다.")
            print("   시스템 PATH에서 찾습니다...")
            driver_path = "chromedriver"
        
        # 2. Chrome 옵션 설정
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # 3. 드라이버 생성 시도
        print("\n🚀 드라이버 생성 중...")
        service = Service(str(driver_path))
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ 드라이버 생성 성공!")
        
        # 4. Chrome 버전 확인
        user_agent = driver.execute_script("return navigator.userAgent")
        print(f"\n📱 User Agent: {user_agent}")
        
        # 5. 간단한 페이지 접속 테스트
        print("\n🌐 Google 접속 테스트 중...")
        driver.get("https://www.google.com")
        print(f"✅ 페이지 제목: {driver.title}")
        
        # 6. JavaScript 실행 테스트
        print("\n🔧 JavaScript 실행 테스트...")
        result = driver.execute_script("return 'JavaScript 실행 성공!'")
        print(f"✅ {result}")
        
        print("\n" + "="*60)
        print("🎉 모든 테스트 통과! 크롬 드라이버가 정상 작동합니다.")
        print("="*60)
        
        return True
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ 테스트 실패!")
        print("="*60)
        print(f"\n오류 메시지: {e}")
        print("\n해결 방법:")
        print("1. ChromeDriver가 올바르게 설치되었는지 확인")
        print("2. Chrome 브라우저와 ChromeDriver 버전이 호환되는지 확인")
        print("3. PATH 환경변수가 올바르게 설정되었는지 확인")
        return False
        
    finally:
        try:
            if 'driver' in locals():
                driver.quit()
                print("\n✅ 드라이버 종료 완료")
        except:
            pass


def test_mobile_driver():
    """모바일 드라이버 테스트 (MobileDriver 클래스 사용)"""
    print("\n" + "="*60)
    print("📱 모바일 드라이버 테스트")
    print("="*60 + "\n")
    
    try:
        from src.mobile_driver import MobileDriver
        
        # 드라이버 생성
        print("🚀 모바일 드라이버 생성 중...")
        mobile = MobileDriver(headless=True, device="galaxy_s24")
        driver = mobile.create_driver()
        
        print("\n✅ 모바일 드라이버 생성 성공!")
        
        # 네이버 모바일 접속 테스트
        print("\n🌐 네이버 모바일 접속 테스트...")
        driver.get("https://m.naver.com")
        print(f"✅ 페이지 제목: {driver.title}")
        
        print("\n" + "="*60)
        print("🎉 모바일 드라이버 테스트 통과!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ 모바일 드라이버 테스트 실패!")
        print("="*60)
        print(f"\n오류 메시지: {e}")
        return False
        
    finally:
        try:
            if 'mobile' in locals() and 'driver' in locals():
                mobile.quit_driver(driver)
                print("\n✅ 드라이버 종료 완료")
        except:
            pass


def main():
    """메인 실행 함수"""
    print("\n" + "🔍"*30)
    print(" "*10 + "크롬 드라이버 검증 스크립트")
    print("🔍"*30 + "\n")
    
    # 1. 기본 드라이버 테스트
    basic_result = test_chromedriver_basic()
    
    # 2. 모바일 드라이버 테스트 (기본 테스트 성공 시에만)
    if basic_result:
        print("\n")
        mobile_result = test_mobile_driver()
    else:
        mobile_result = False
        print("\n⚠️  기본 테스트 실패로 모바일 드라이버 테스트를 건너뜁니다.")
    
    # 최종 결과
    print("\n\n" + "="*60)
    print(" "*15 + "📊 최종 결과")
    print("="*60)
    print(f"기본 드라이버 테스트: {'✅ 통과' if basic_result else '❌ 실패'}")
    print(f"모바일 드라이버 테스트: {'✅ 통과' if mobile_result else '❌ 실패'}")
    print("="*60 + "\n")
    
    return basic_result and mobile_result


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

