"""
여러 사이트 크롤링 예제
URL을 파라미터로 저장하고 필요할 때 접속
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.crawler import NaverCrawler
from selenium.webdriver.common.by import By
import time


def example1_multiple_sites():
    """예제 1: 여러 사이트 순회 크롤링"""
    print("\n" + "="*60)
    print("예제 1: 여러 사이트 순회")
    print("="*60)
    
    # URL 리스트
    urls = [
        "https://m.naver.com",
        "https://m.daum.net",
        "https://www.google.com",
    ]
    
    # 크롤러 생성 (URL은 나중에 지정)
    with NaverCrawler(use_mobile=True, headless=False) as crawler:
        for url in urls:
            print(f"\n📍 접속: {url}")
            crawler.get_page(url)
            time.sleep(2)
            
            # 간단한 크롤링
            crawler.scroll_down(300)
            time.sleep(1)
            
            print(f"✅ {url} 크롤링 완료")


def example2_initial_url():
    """예제 2: 초기 URL 설정 후 다른 페이지로 이동"""
    print("\n" + "="*60)
    print("예제 2: 초기 URL 설정")
    print("="*60)
    
    # 초기 URL을 파라미터로 전달
    with NaverCrawler(url="https://m.naver.com", use_mobile=True, headless=False) as crawler:
        # 초기 URL 접속
        print(f"📍 초기 URL: {crawler.url}")
        crawler.get_page(crawler.url)
        time.sleep(2)
        
        # 다른 페이지로 이동
        print("📍 다음 페이지로 이동")
        crawler.get_page("https://m.daum.net")
        time.sleep(2)
        
        # 또 다른 페이지
        print("📍 또 다른 페이지로 이동")
        crawler.get_page("https://www.google.com")
        time.sleep(2)


def example3_blog_crawling():
    """예제 3: 여러 블로그 글 크롤링"""
    print("\n" + "="*60)
    print("예제 3: 여러 블로그 글 크롤링")
    print("="*60)
    
    # 블로그 URL 리스트 (예시)
    blog_urls = [
        "https://m.blog.naver.com",
        "https://m.blog.naver.com",
        "https://m.blog.naver.com",
    ]
    
    with NaverCrawler(use_mobile=True, device="galaxy_s24", headless=False) as crawler:
        for i, url in enumerate(blog_urls, 1):
            print(f"\n📖 블로그 {i}/{len(blog_urls)} 접속: {url}")
            crawler.get_page(url)
            time.sleep(3)
            
            # 자연스럽게 읽기 (10~20초)
            print(f"   읽는 중...")
            crawler.simulate_natural_reading(min_read_time=10, max_read_time=20)
            
            print(f"✅ 블로그 {i} 완료")


def example4_search_multiple_keywords():
    """예제 4: 여러 키워드 검색"""
    print("\n" + "="*60)
    print("예제 4: 여러 키워드 검색")
    print("="*60)
    
    keywords = ["파이썬", "크롤링", "셀레니움"]
    
    with NaverCrawler(url="https://m.naver.com", use_mobile=True, headless=False) as crawler:
        for keyword in keywords:
            print(f"\n🔍 검색: {keyword}")
            
            # 네이버 메인으로 이동
            crawler.get_page(crawler.url)
            time.sleep(2)
            
            # 검색창 찾아서 입력
            if crawler.is_element_present(By.CSS_SELECTOR, "input.search_input"):
                search_box = crawler.find_element(By.CSS_SELECTOR, "input.search_input")
                search_box.clear()
                crawler.slow_typing(search_box, keyword)
                time.sleep(1)
                
                # 검색 버튼 클릭 (실제로는 엔터키나 버튼 클릭)
                # crawler.touch_element(By.CLASS_NAME, "search_btn")
                
                print(f"✅ '{keyword}' 검색 완료")
            
            time.sleep(2)


def example5_category_pages():
    """예제 5: 카테고리별 페이지 크롤링"""
    print("\n" + "="*60)
    print("예제 5: 카테고리별 페이지 크롤링")
    print("="*60)
    
    # 카테고리별 URL
    categories = {
        "뉴스": "https://m.news.naver.com",
        "쇼핑": "https://shopping.naver.com",
        "블로그": "https://section.blog.naver.com",
    }
    
    with NaverCrawler(use_mobile=True, headless=False) as crawler:
        for category_name, url in categories.items():
            print(f"\n📂 {category_name} 카테고리 크롤링")
            print(f"   URL: {url}")
            
            crawler.get_page(url)
            time.sleep(3)
            
            # 스크롤하며 데이터 수집
            print(f"   스크롤 중...")
            crawler.dynamic_scroll(distance=800)
            time.sleep(1)
            
            # 여기서 실제 데이터 수집 로직 추가
            # items = crawler.find_elements(By.CLASS_NAME, "item")
            
            print(f"✅ {category_name} 완료")


def example6_url_list_from_file():
    """예제 6: 파일에서 URL 목록 읽어서 크롤링"""
    print("\n" + "="*60)
    print("예제 6: URL 목록 파일 크롤링")
    print("="*60)
    
    # 실제로는 파일에서 읽어오기
    # with open('urls.txt', 'r', encoding='utf-8') as f:
    #     urls = [line.strip() for line in f if line.strip()]
    
    # 예시 URL 목록
    urls = [
        "https://m.naver.com",
        "https://m.daum.net",
        "https://www.google.com",
    ]
    
    print(f"총 {len(urls)}개의 URL 크롤링 예정")
    
    with NaverCrawler(use_mobile=True, headless=False) as crawler:
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] {url}")
            
            try:
                crawler.get_page(url)
                time.sleep(2)
                
                # 타이틀 가져오기
                title = crawler.driver.title
                print(f"   제목: {title}")
                
                # 스크롤
                crawler.scroll_down(300)
                time.sleep(1)
                
                results.append({
                    "url": url,
                    "title": title,
                    "status": "success"
                })
                
            except Exception as e:
                print(f"   ❌ 오류: {e}")
                results.append({
                    "url": url,
                    "status": "failed",
                    "error": str(e)
                })
        
        # 결과 출력
        print("\n" + "="*60)
        print("크롤링 결과 요약")
        print("="*60)
        success = sum(1 for r in results if r['status'] == 'success')
        print(f"성공: {success}/{len(urls)}")
        print(f"실패: {len(urls) - success}/{len(urls)}")


def example7_conditional_crawling():
    """예제 7: 조건부 페이지 이동"""
    print("\n" + "="*60)
    print("예제 7: 조건부 페이지 이동")
    print("="*60)
    
    with NaverCrawler(url="https://m.naver.com", use_mobile=True, headless=False) as crawler:
        # 메인 페이지 접속
        print("📍 네이버 메인 접속")
        crawler.get_page(crawler.url)
        time.sleep(2)
        
        # 특정 요소가 있는지 확인
        if crawler.is_element_present(By.CLASS_NAME, "news_area"):
            print("✅ 뉴스 영역 발견! 뉴스 페이지로 이동")
            crawler.get_page("https://m.news.naver.com")
            time.sleep(2)
            
            # 뉴스 스크롤
            crawler.dynamic_scroll(distance=1000)
        else:
            print("ℹ️ 뉴스 영역 없음. 블로그로 이동")
            crawler.get_page("https://section.blog.naver.com")
            time.sleep(2)


def main():
    """메인 함수"""
    print("\n" + "="*80)
    print("여러 사이트 크롤링 예제")
    print("="*80)
    
    examples = {
        '1': ('여러 사이트 순회', example1_multiple_sites),
        '2': ('초기 URL 설정', example2_initial_url),
        '3': ('여러 블로그 글 크롤링', example3_blog_crawling),
        '4': ('여러 키워드 검색', example4_search_multiple_keywords),
        '5': ('카테고리별 페이지', example5_category_pages),
        '6': ('URL 목록 파일 크롤링', example6_url_list_from_file),
        '7': ('조건부 페이지 이동', example7_conditional_crawling),
    }
    
    print("\n실행할 예제를 선택하세요:")
    for key, (name, _) in examples.items():
        print(f"{key}. {name}")
    print("0. 종료")
    
    choice = input("\n선택 (0-7): ").strip()
    
    if choice == '0':
        print("종료합니다.")
        return
    elif choice in examples:
        name, func = examples[choice]
        try:
            func()
        except KeyboardInterrupt:
            print("\n\n⚠️ 사용자가 중단했습니다.")
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ 잘못된 선택입니다.")
    
    print("\n" + "="*80)
    print("예제 실행 완료")
    print("="*80)


if __name__ == "__main__":
    main()

