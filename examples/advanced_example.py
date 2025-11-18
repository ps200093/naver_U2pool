"""
고급 사용 예제
- Headless 모드
- 스크린샷 저장
- 쿠키 관리
- 프록시 사용 (준비)
"""
import sys
import time
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawler import NaverCrawler
from src.utils import save_to_json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def headless_crawling():
    """Headless 모드로 크롤링"""
    print("\n👻 Headless 모드 크롤링 시작...")
    
    with NaverCrawler(
        headless=True,  # Headless 모드
        use_mobile=True,
        device="galaxy_s24"
    ) as crawler:
        print("1️⃣ 네이버 접속 중...")
        crawler.get_page("https://m.naver.com")
        
        # 타이틀 확인
        title = crawler.driver.title
        print(f"2️⃣ 페이지 타이틀: {title}")
        
        # User Agent 확인
        user_agent = crawler.driver.execute_script("return navigator.userAgent")
        print(f"3️⃣ User Agent: {user_agent[:80]}...")
        
        # 모바일 감지 확인
        is_mobile = crawler.driver.execute_script(
            "return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)"
        )
        print(f"4️⃣ 모바일 감지: {is_mobile}")
        
        print("\n✅ Headless 크롤링 완료!")


def take_screenshots():
    """여러 페이지 스크린샷 저장"""
    print("\n📸 스크린샷 저장 예제...")
    
    # 스크린샷 저장 폴더
    screenshot_dir = Path(__file__).parent.parent / "data" / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    pages = {
        "naver_main": "https://m.naver.com",
        "naver_news": "https://m.news.naver.com",
        "naver_shopping": "https://mshopping.naver.com"
    }
    
    with NaverCrawler(
        headless=False,
        use_mobile=True,
        device="galaxy_s24"
    ) as crawler:
        for name, url in pages.items():
            print(f"\n📍 {name} 접속 중...")
            crawler.get_page(url, wait_time=2)
            
            # 스크린샷 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = screenshot_dir / f"{name}_{timestamp}.png"
            crawler.driver.save_screenshot(str(filename))
            
            print(f"   ✅ 스크린샷 저장: {filename}")
            time.sleep(1)
    
    print(f"\n✅ 모든 스크린샷 저장 완료!")
    print(f"   저장 위치: {screenshot_dir}")


def cookie_management():
    """쿠키 관리 예제"""
    print("\n🍪 쿠키 관리 예제...")
    
    with NaverCrawler(
        headless=False,
        use_mobile=True,
        device="galaxy_s24"
    ) as crawler:
        # 네이버 접속
        print("1️⃣ 네이버 접속 중...")
        crawler.get_page("https://m.naver.com")
        
        # 쿠키 가져오기
        cookies = crawler.driver.get_cookies()
        print(f"2️⃣ 쿠키 개수: {len(cookies)}")
        
        # 쿠키 정보 출력
        print("\n쿠키 목록:")
        for cookie in cookies[:5]:  # 처음 5개만
            print(f"   - {cookie['name']}: {cookie['value'][:30]}...")
        
        # 쿠키 저장
        cookie_data = {
            "url": crawler.driver.current_url,
            "timestamp": datetime.now().isoformat(),
            "cookies": cookies
        }
        
        data_dir = Path(__file__).parent.parent / "data"
        save_to_json(cookie_data, "cookies.json")
        
        print("\n✅ 쿠키 저장 완료!")
        
        # 특정 쿠키 추가
        print("\n3️⃣ 커스텀 쿠키 추가...")
        crawler.driver.add_cookie({
            'name': 'test_cookie',
            'value': 'test_value',
            'domain': '.naver.com'
        })
        print("   ✅ 쿠키 추가 완료!")


def extract_page_info():
    """페이지 정보 추출"""
    print("\n📊 페이지 정보 추출 예제...")
    
    with NaverCrawler(
        headless=True,
        use_mobile=True,
        device="galaxy_s24"
    ) as crawler:
        crawler.get_page("https://m.naver.com")
        
        # JavaScript로 다양한 정보 추출
        info = crawler.driver.execute_script("""
            return {
                // 페이지 정보
                title: document.title,
                url: window.location.href,
                
                // Navigator 정보
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                languages: navigator.languages,
                onLine: navigator.onLine,
                cookieEnabled: navigator.cookieEnabled,
                
                // 모바일 관련
                maxTouchPoints: navigator.maxTouchPoints,
                
                // 화면 정보
                screenWidth: window.screen.width,
                screenHeight: window.screen.height,
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                devicePixelRatio: window.devicePixelRatio,
                
                // Connection API
                connectionType: navigator.connection ? navigator.connection.effectiveType : 'unknown',
                
                // 기타
                hardwareConcurrency: navigator.hardwareConcurrency,
                deviceMemory: navigator.deviceMemory
            };
        """)
        
        print("\n=== 페이지 정보 ===")
        print(f"제목: {info['title']}")
        print(f"URL: {info['url']}")
        print()
        
        print("=== Navigator 정보 ===")
        print(f"User Agent: {info['userAgent'][:80]}...")
        print(f"플랫폼: {info['platform']}")
        print(f"언어: {info['language']}")
        print(f"온라인: {info['onLine']}")
        print(f"쿠키 활성화: {info['cookieEnabled']}")
        print()
        
        print("=== 모바일 정보 ===")
        print(f"터치 포인트: {info['maxTouchPoints']}")
        print(f"연결 타입: {info['connectionType']}")
        print()
        
        print("=== 화면 정보 ===")
        print(f"스크린: {info['screenWidth']}x{info['screenHeight']}")
        print(f"뷰포트: {info['innerWidth']}x{info['innerHeight']}")
        print(f"Pixel Ratio: {info['devicePixelRatio']}")
        print()
        
        print("=== 하드웨어 정보 ===")
        print(f"CPU 코어: {info['hardwareConcurrency']}")
        print(f"메모리: {info['deviceMemory']}GB")
        
        # JSON으로 저장
        data_dir = Path(__file__).parent.parent / "data"
        save_to_json(info, "page_info.json")
        
        print("\n✅ 페이지 정보 추출 및 저장 완료!")


def compare_mobile_desktop():
    """모바일과 데스크톱 모드 비교"""
    print("\n🔄 모바일 vs 데스크톱 비교...")
    
    results = {}
    
    # 모바일 모드
    print("\n1️⃣ 모바일 모드로 접속...")
    with NaverCrawler(
        headless=True,
        use_mobile=True,
        device="galaxy_s24"
    ) as crawler:
        crawler.get_page("https://www.naver.com")
        
        results['mobile'] = {
            'url': crawler.driver.current_url,
            'title': crawler.driver.title,
            'user_agent': crawler.driver.execute_script("return navigator.userAgent"),
            'platform': crawler.driver.execute_script("return navigator.platform"),
            'mobile_detected': crawler.driver.execute_script(
                "return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)"
            )
        }
    
    # 데스크톱 모드
    print("2️⃣ 데스크톱 모드로 접속...")
    with NaverCrawler(
        headless=True,
        use_mobile=False
    ) as crawler:
        crawler.get_page("https://www.naver.com")
        
        results['desktop'] = {
            'url': crawler.driver.current_url,
            'title': crawler.driver.title,
            'user_agent': crawler.driver.execute_script("return navigator.userAgent"),
            'platform': crawler.driver.execute_script("return navigator.platform"),
            'mobile_detected': crawler.driver.execute_script(
                "return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)"
            )
        }
    
    # 결과 비교
    print("\n" + "="*60)
    print("비교 결과")
    print("="*60)
    
    print("\n📱 모바일 모드:")
    print(f"  URL: {results['mobile']['url']}")
    print(f"  플랫폼: {results['mobile']['platform']}")
    print(f"  모바일 감지: {results['mobile']['mobile_detected']}")
    print(f"  User Agent: {results['mobile']['user_agent'][:60]}...")
    
    print("\n💻 데스크톱 모드:")
    print(f"  URL: {results['desktop']['url']}")
    print(f"  플랫폼: {results['desktop']['platform']}")
    print(f"  모바일 감지: {results['desktop']['mobile_detected']}")
    print(f"  User Agent: {results['desktop']['user_agent'][:60]}...")
    
    # 저장
    data_dir = Path(__file__).parent.parent / "data"
    save_to_json(results, "mobile_vs_desktop.json")
    
    print("\n✅ 비교 완료!")


def main():
    """메인 메뉴"""
    print("\n" + "="*60)
    print("🚀 고급 사용 예제")
    print("="*60 + "\n")
    
    examples = {
        "1": ("Headless 모드 크롤링", headless_crawling),
        "2": ("스크린샷 저장", take_screenshots),
        "3": ("쿠키 관리", cookie_management),
        "4": ("페이지 정보 추출", extract_page_info),
        "5": ("모바일 vs 데스크톱 비교", compare_mobile_desktop),
    }
    
    print("예제 선택:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\n선택하세요 (1-5): ").strip()
    
    if choice in examples:
        name, func = examples[choice]
        print(f"\n{'='*60}")
        print(f"▶️ {name}")
        print(f"{'='*60}")
        func()
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()

