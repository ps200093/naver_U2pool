import time
import logging
import json
import os
from pathlib import Path
from selenium.webdriver.common.by import By
from src.chrome_driver import ChromeDriver
from src.naver_shopping import OptimizedNaverCrawler


def load_config(config_path="config/config.json"):
    """config.json 파일 로드"""
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"⚠️ 설정 파일을 찾을 수 없습니다: {config_path}")
            print("기본 설정을 사용합니다.")
            return {
                "headless": False,
                "wait_time": 3,
                "timeout": 10,
                "use_debug_mode": True,
                "debug_port": 9222,
                "profile_path": None
            }
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"✅ 설정 파일 로드 완료: {config_path}")
            return config
    except Exception as e:
        print(f"❌ 설정 파일 로드 실패: {e}")
        print("기본 설정을 사용합니다.")
        return {
            "headless": False,
            "wait_time": 3,
            "timeout": 10,
            "use_debug_mode": True,
            "debug_port": 9222,
            "profile_path": None
        }


def test_crawler(url_list: dict = {}, config=None):
    """
    크롤러 테스트 (naver_shopping.py 사용)
    
    Args:
        url_list: 테스트할 URL 딕셔너리 (키워드: URL)
        config: 설정 딕셔너리 (None이면 자동 로드)
    """
    # 설정 로드
    if config is None:
        config = load_config()
    
    print(f"\n{'='*60}")
    print(f"🔍 크롤러 테스트 시작")
    print(f"🔍 키워드 개수: {len(url_list)}")
    print(f"{'='*60}")
    print(f"\n📋 현재 설정:")
    print(f"  - 헤드리스 모드: {config.get('headless', False)}")
    print(f"  - 디버깅 모드: {config.get('use_debug_mode', True)} (VBA 원본 방식)")
    if config.get('use_debug_mode', True):
        print(f"  - 디버깅 포트: {config.get('debug_port', 9222)}")
        profile_path = config.get('profile_path') or os.path.expanduser("~/ChromeTEMP")
        print(f"  - 프로필 경로: {profile_path}")
    print(f"  - 대기 시간: {config.get('wait_time', 3)}초")
    print(f"  - 타임아웃: {config.get('timeout', 10)}초")
    print(f"{'='*60}\n")
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 🆕 모든 키워드에 대해 반복 처리
    if not url_list:
        print("⚠️  처리할 URL이 없습니다.")
        return
    
    keywords = list(url_list.keys())
    total_keywords = len(keywords)
    
    for idx, keyword in enumerate(keywords, 1):
        print(f"\n{'='*60}")
        print(f"🔄 키워드 {idx}/{total_keywords}: '{keyword}'")
        print(f"{'='*60}")
        
        url = url_list[keyword]
        
        # 각 키워드마다 새로운 드라이버 생성
        chrome = ChromeDriver(
            headless=config.get("headless", False),
            use_debug_mode=config.get("use_debug_mode", True),
            debug_port=config.get("debug_port", 9222),
            profile_path=config.get("profile_path")  # None이면 자동으로 ~/ChromeTEMP
        )

        driver = chrome.create_driver()
        
        # ChromeDriver 객체에 driver 속성 추가 (OptimizedNaverCrawler에서 사용)
        chrome.driver = driver
        
        # OptimizedNaverCrawler 생성 (naver_shopping.py)
        crawler = OptimizedNaverCrawler(chrome_controller=chrome)

        try:
            # 첫 번째 키워드일 때만 로그인 안내
            if idx == 1:
                print("\n1️⃣ 네이버 로그인 (선택사항)")
                print("  - 로그인이 필요한 경우 브라우저에서 수동으로 로그인해주세요.")
                # input("  - 로그인을 건너뛰려면 엔터를 누르세요...")
            
            print(f"\n2️⃣ 검색 테스트: '{keyword}'")
            
            # naver_shopping.py의 _natural_search 사용
            # 자동으로 네이버 메인 → 통합검색 → 쇼핑 탭 클릭
            crawler._natural_search(keyword=keyword, domestic=True)
            
            # 상품 목록 로딩
            crawler._fast_lazy_load()

            # URL에서 UID 추출
            target_uid = crawler.extract_uid_from_url(url)
            
            if target_uid:
                print(f"\n3️⃣ 목표 상품 찾기")
                print(f"  - URL: {url}")
                print(f"  - UID (nv_mid): {target_uid}")
                
                # nv_mid로 상품 찾아서 클릭
                success = crawler.find_and_click_product_by_uid(target_uid)
                
                if success:
                    print(f"\n✅ 상품 페이지로 이동 성공!")
                    print(f"  🔗 현재 URL: {driver.current_url}")
                    
                    # 잠시 대기 (사용자가 결과 확인 가능)
                    time.sleep(2)
                else:
                    print(f"\n⚠️  상품을 찾지 못했습니다.")
            else:
                print(f"\n⚠️  URL에서 UID를 추출할 수 없습니다: {url}")
                
                # UID 추출 실패 시 기존 방식으로 진행
                print("\n3️⃣ 가격비교 상품 데이터 추출")
                data = crawler._extract_store_data(page=1)
                
                if data:
                    print(f"\n✅ {len(data)}개 스토어 추출 완료!")
                    print(f"\n📊 추출된 데이터 샘플 (처음 3개):")
                    for i, item in enumerate(data[:3], 1):
                        print(f"\n[{i}]")
                        print(f"  상품명: {item.get('상품명', 'N/A')[:50]}")
                        print(f"  스토어: {item.get('이름', 'N/A')}")
                        print(f"  순위: {item.get('ranking', 'N/A')}")
                        print(f"  광고: {item.get('광고', 'N/A')}")
                        print(f"  리뷰수: {item.get('리뷰수', 'N/A')}")
                        print(f"  찜수: {item.get('찜수', 'N/A')}")
                else:
                    print("\n⚠️  데이터 추출 실패")
            
            print(f"\n✅ 키워드 '{keyword}' 처리 완료!")
            
        except Exception as e:
            print(f"\n❌ 키워드 '{keyword}' 처리 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            print(f"\n드라이버 종료 중... ({idx}/{total_keywords})")
            # Chrome 프로세스까지 완전히 종료 (다음 키워드 처리를 위해)
            chrome.quit_driver(driver, kill_chrome=True)
            print("✅ 드라이버 종료 완료!")
            
            # 다음 키워드가 있으면 잠시 대기 (Chrome 프로세스 정리 시간)
            if idx < total_keywords:
                print("\n⏳ 다음 키워드 준비 중...")
                time.sleep(3)  # Chrome 프로세스가 완전히 종료될 시간 확보
    
    print(f"\n{'='*60}")
    print(f"🎉 모든 키워드 처리 완료! (총 {total_keywords}개)")
    print(f"{'='*60}")
    # input("\n엔터를 누르면 종료합니다...")



if __name__ == "__main__":
    # config.json 설정 로드
    config = load_config()
    
    url_list = {
        # "한우선물세트": "https://brand.naver.com/gorgeouscowofficial/products/9687826363",
        "한우선물세트": "https://smartstore.naver.com/the_homme/products/11629672050",
        "다이어리": "https://search.shopping.naver.com/catalog/57407585768",
        "바디스크럽": "https://smartstore.naver.com/braziliansecret/products/636183671",
    }
    
    # 크롤러 테스트 실행
    test_crawler(url_list=url_list, config=config)
