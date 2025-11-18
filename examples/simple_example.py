"""
간단한 사용 예제
네이버 모바일 검색 크롤링
"""
import sys
import time
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawler import NaverCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def search_naver_mobile(keyword):
    """네이버 모바일에서 검색"""
    print(f"\n🔍 '{keyword}' 검색 시작...")
    
    with NaverCrawler(
        headless=False,
        use_mobile=True,
        device="galaxy_s24"
    ) as crawler:
        # 네이버 모바일 접속
        print("\n1️⃣ 네이버 모바일 접속...")
        crawler.get_page("https://m.naver.com")
        
        try:
            # 검색창 찾기
            print("2️⃣ 검색창 찾는 중...")
            search_box = WebDriverWait(crawler.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.search_input"))
            )
            
            # 검색어 입력
            print(f"3️⃣ '{keyword}' 입력...")
            search_box.clear()
            search_box.send_keys(keyword)
            time.sleep(1)
            
            # 검색 버튼 클릭
            print("4️⃣ 검색 실행...")
            search_btn = crawler.driver.find_element(By.CSS_SELECTOR, "button.btn_search")
            search_btn.click()
            time.sleep(3)
            
            print("✅ 검색 완료!")
            print("\n결과를 확인하세요. 엔터를 누르면 종료합니다...")
            input()
            
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            print("\n셀렉터가 변경되었을 수 있습니다.")
            print("개발자 도구(F12)로 확인하세요.")
            input()


def browse_naver_shopping():
    """네이버 쇼핑 모바일 둘러보기"""
    print("\n🛒 네이버 쇼핑 모바일 접속...")
    
    with NaverCrawler(
        headless=False,
        use_mobile=True,
        device="galaxy_s24"
    ) as crawler:
        # 네이버 쇼핑 접속
        crawler.get_page("https://mshopping.naver.com/")
        
        print("\n✅ 네이버 쇼핑 접속 완료!")
        print("모바일 뷰로 보이는지 확인하세요.")
        print("\n엔터를 누르면 종료합니다...")
        input()


def compare_devices():
    """여러 기기로 같은 페이지 비교"""
    devices = ["galaxy_s24", "iphone_15_pro"]
    
    for device in devices:
        print(f"\n{'='*60}")
        print(f"📱 {device}로 접속 중...")
        print(f"{'='*60}")
        
        with NaverCrawler(
            headless=False,
            use_mobile=True,
            device=device
        ) as crawler:
            crawler.get_page("https://m.naver.com")
            
            # 화면 정보 출력
            info = crawler.driver.execute_script("""
                return {
                    platform: navigator.platform,
                    width: window.screen.width,
                    height: window.screen.height
                };
            """)
            
            print(f"\n플랫폼: {info['platform']}")
            print(f"화면 크기: {info['width']}x{info['height']}")
            print(f"\n{device} 확인 - 3초 대기...")
            time.sleep(3)


def main():
    """메인 메뉴"""
    print("\n" + "="*60)
    print("🎯 네이버 모바일 크롤링 예제")
    print("="*60 + "\n")
    
    print("예제 선택:")
    print("  1. 네이버 검색")
    print("  2. 네이버 쇼핑 둘러보기")
    print("  3. 여러 기기로 비교")
    
    choice = input("\n선택하세요 (1-3): ").strip()
    
    if choice == "1":
        keyword = input("검색어를 입력하세요: ").strip()
        if keyword:
            search_naver_mobile(keyword)
        else:
            print("검색어를 입력해주세요.")
    elif choice == "2":
        browse_naver_shopping()
    elif choice == "3":
        compare_devices()
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()

