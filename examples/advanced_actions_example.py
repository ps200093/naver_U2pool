"""
고급 크롤링 동작 예제
자연스러운 스크롤, 터치, 텍스트 입력 등의 사용법
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.crawler import NaverCrawler
from selenium.webdriver.common.by import By
import time


def example_natural_scrolling():
    """자연스러운 스크롤 예제"""
    print("\n=== 자연스러운 스크롤 예제 ===")
    
    with NaverCrawler(use_mobile=True, device="galaxy_s24", headless=False) as crawler:
        # 네이버 모바일 접속
        crawler.get_page("https://m.naver.com")
        
        # 1. 동적 스크롤 (사람처럼 자연스럽게)
        print("동적 스크롤 실행...")
        crawler.dynamic_scroll(distance=800)
        
        # 2. 부드러운 스크롤 (easing 적용)
        print("부드러운 스크롤 실행...")
        crawler.smooth_scroll_by(500)
        time.sleep(1)
        
        # 3. 자연스러운 읽기 시뮬레이션 (20~30초)
        print("자연스러운 읽기 시뮬레이션 (20~30초)...")
        crawler.simulate_natural_reading(min_read_time=20, max_read_time=30)


def example_touch_interactions():
    """터치 인터랙션 예제"""
    print("\n=== 터치 인터랙션 예제 ===")
    
    with NaverCrawler(use_mobile=True, device="galaxy_s24", headless=False) as crawler:
        crawler.get_page("https://m.naver.com")
        
        # 1. 일반 터치 (재시도 및 랜덤 오프셋 포함)
        print("검색창 터치...")
        crawler.touch_element(By.CSS_SELECTOR, "input.search_input")
        time.sleep(1)
        
        # 2. JavaScript를 통한 터치 (가려진 요소도 가능)
        # crawler.touch_element_by_js(By.ID, "some_element")
        
        # 3. 특정 좌표 터치
        # crawler.touch_at_coordinates(200, 300)
        
        # 4. 무작위 구석 클릭 (팝업 닫기 등)
        print("무작위 구석 클릭...")
        crawler.random_corner_click()


def example_text_input():
    """텍스트 입력 예제"""
    print("\n=== 텍스트 입력 예제 ===")
    
    with NaverCrawler(use_mobile=True, device="galaxy_s24", headless=False) as crawler:
        crawler.get_page("https://m.naver.com")
        
        # 검색창 찾기
        search_input = crawler.wait_for_element(By.CSS_SELECTOR, "input.search_input")
        
        if search_input:
            # 천천히 사람처럼 타이핑
            print("검색어 입력 중...")
            crawler.slow_typing(search_input, "네이버 뉴스", min_delay=0.1, max_delay=0.3)
            time.sleep(2)


def example_swipe_gesture():
    """스와이프 제스처 예제"""
    print("\n=== 스와이프 제스처 예제 ===")
    
    with NaverCrawler(use_mobile=True, device="galaxy_s24", headless=False) as crawler:
        crawler.get_page("https://m.naver.com")
        
        # 화면 높이 가져오기
        viewport_height = crawler.driver.execute_script("return window.innerHeight;")
        
        # 아래로 스와이프 (위에서 아래로)
        print("아래로 스와이프...")
        start_y = int(viewport_height * 0.8)
        end_y = int(viewport_height * 0.2)
        crawler.swipe(start_y, end_y, duration=0.4)
        time.sleep(1)
        
        # 위로 스와이프 (아래에서 위로)
        print("위로 스와이프...")
        crawler.swipe(end_y, start_y, duration=0.4)


def example_element_search():
    """요소 탐색 예제"""
    print("\n=== 요소 탐색 예제 ===")
    
    with NaverCrawler(use_mobile=True, device="galaxy_s24", headless=False) as crawler:
        crawler.get_page("https://m.naver.com")
        
        # 1. 단일 요소 찾기
        search_box = crawler.find_element(By.CSS_SELECTOR, "input.search_input")
        if search_box:
            print(f"검색창 발견: {search_box.tag_name}")
        
        # 2. 여러 요소 찾기
        links = crawler.find_elements(By.TAG_NAME, "a")
        print(f"링크 개수: {len(links)}")
        
        # 3. 클릭 가능할 때까지 대기
        element = crawler.wait_for_element_clickable(By.CSS_SELECTOR, "button.search_btn", timeout=5)
        if element:
            print("클릭 가능한 버튼 발견")
        
        # 4. 요소 존재 여부 확인 (대기 없음)
        exists = crawler.is_element_present(By.ID, "some_element")
        print(f"요소 존재 여부: {exists}")


def example_scroll_variations():
    """다양한 스크롤 예제"""
    print("\n=== 다양한 스크롤 예제 ===")
    
    with NaverCrawler(use_mobile=True, device="galaxy_s24", headless=False) as crawler:
        crawler.get_page("https://m.naver.com")
        
        # 1. 기본 스크롤
        print("아래로 스크롤...")
        crawler.scroll_down(300)
        time.sleep(1)
        
        # 2. 최하단으로
        print("최하단으로 스크롤...")
        crawler.scroll_to_bottom()
        time.sleep(1)
        
        # 3. 최상단으로
        print("최상단으로 스크롤...")
        crawler.scroll_to_top()
        time.sleep(1)
        
        # 4. 무한 스크롤 (더 이상 콘텐츠가 없을 때까지)
        print("무한 스크롤 시작...")
        scroll_count = crawler.infinite_scroll(max_scrolls=5, scroll_pause=1.0)
        print(f"총 {scroll_count}회 스크롤 완료")
        
        # 5. 현재 스크롤 위치 확인
        position = crawler.get_scroll_position()
        print(f"현재 스크롤 위치: x={position['x']}, y={position['y']}")


def example_cid_extraction():
    """CID 추출 예제"""
    print("\n=== CID 추출 예제 ===")
    
    crawler = NaverCrawler()
    
    # 다양한 URL 형식에서 CID 추출
    urls = [
        "https://blog.naver.com/user/123456789",
        "https://blog.naver.com/user/123456789?param=value",
        "https://m.blog.naver.com/PostView.naver?blogId=user&logNo=987654321",
    ]
    
    for url in urls:
        cid = crawler.extract_cid(url)
        print(f"URL: {url}")
        print(f"CID: {cid}\n")


def main():
    """메인 함수"""
    print("=" * 60)
    print("고급 크롤링 동작 예제")
    print("=" * 60)
    
    # 실행할 예제 선택
    examples = {
        '1': ('자연스러운 스크롤', example_natural_scrolling),
        '2': ('터치 인터랙션', example_touch_interactions),
        '3': ('텍스트 입력', example_text_input),
        '4': ('스와이프 제스처', example_swipe_gesture),
        '5': ('요소 탐색', example_element_search),
        '6': ('다양한 스크롤', example_scroll_variations),
        '7': ('CID 추출', example_cid_extraction),
    }
    
    print("\n실행할 예제를 선택하세요:")
    for key, (name, _) in examples.items():
        print(f"{key}. {name}")
    print("0. 전체 실행")
    
    choice = input("\n선택 (0-7): ").strip()
    
    if choice == '0':
        # 전체 실행
        for key, (name, func) in examples.items():
            try:
                func()
            except Exception as e:
                print(f"\n오류 발생 ({name}): {e}")
            time.sleep(2)
    elif choice in examples:
        # 선택한 예제 실행
        name, func = examples[choice]
        try:
            func()
        except Exception as e:
            print(f"\n오류 발생: {e}")
    else:
        print("잘못된 선택입니다.")
    
    print("\n" + "=" * 60)
    print("예제 실행 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()

