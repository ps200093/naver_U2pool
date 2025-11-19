"""
최적화된 네이버 쇼핑 크롤러
"""

from selenium.webdriver.common.by import By
import json
import pandas as pd
import time
import random
from urllib.parse import urlparse, parse_qs


class OptimizedNaverCrawler:
    """속도 최적화된 네이버 쇼핑 크롤러"""
    
    def __init__(self, chrome_controller):
        self.chrome = chrome_controller
        self.driver = chrome_controller.driver
    
    @staticmethod
    def extract_uid_from_url(url):
        """
        네이버 쇼핑 URL에서 상품 UID(nv_mid) 추출
        
        지원하는 URL 형식:
            1. 스마트스토어: https://smartstore.naver.com/oroda_mall/products/7197769400
            2. 쇼핑 카탈로그: https://search.shopping.naver.com/catalog/57407585768
            3. 쿼리 파라미터: ?n_media_id=12345 또는 ?nvMid=12345
        
        Args:
            url: 네이버 쇼핑 상품 URL
        
        Returns:
            str: 상품 UID (nv_mid)
        """
        try:
            # URL 파싱
            parsed = urlparse(url)
            
            # 1. /products/{uid} 형태에서 추출 (스마트스토어)
            if '/products/' in parsed.path:
                uid = parsed.path.split('/products/')[-1].split('/')[0].split('?')[0]
                return uid
            
            # 2. /catalog/{uid} 또는 /cattalog/{uid} 형태에서 추출 (쇼핑 카탈로그)
            if '/catalog/' in parsed.path or '/cattalog/' in parsed.path:
                # catalog 또는 cattalog 이후의 숫자 추출
                parts = parsed.path.split('/')
                for i, part in enumerate(parts):
                    if part in ['catalog', 'cattalog'] and i + 1 < len(parts):
                        uid = parts[i + 1].split('?')[0]
                        if uid.isdigit():
                            return uid
            
            # 3. 쿼리 파라미터에서 추출 시도
            query_params = parse_qs(parsed.query)
            if 'n_media_id' in query_params:
                return query_params['n_media_id'][0]
            if 'nvMid' in query_params:
                return query_params['nvMid'][0]
            
            return None
        except Exception as e:
            print(f"    ⚠️  UID 추출 실패: {e}")
            return None
    
    def crawl_page(self, keyword, page=1, domestic=True, first_search=False):
        """
        단일 페이지 크롤링
        
        Args:
            keyword: 검색 키워드
            page: 페이지 번호
            domestic: True=국내, False=해외
            first_search: 첫 검색인지 여부
        
        Returns:
            list: 스토어 데이터 리스트
        """
        from urllib.parse import quote
        
        print(f"  📄 {page}페이지 로딩 중...")
        
        if first_search and page == 1:
            # 첫 검색: 네이버 통합검색 → 쇼핑 탭 클릭 (자연스러운 방식)
            self._natural_search(keyword, domestic)
        else:
            # VBA: 버튼 클릭으로 페이지 이동
            self._click_page_button(page)
        
        # Lazy loading 처리 (VBA: 스크롤하며 상품 로딩)
        self._fast_lazy_load()
        
        # 데이터 추출 (VBA: For Each 스토어 In 스토어들)
        data = self._extract_store_data(page)
        
        print(f"  ✅ {len(data)}개 스토어 추출 완료")
        
        return data
    
    
    def _natural_search(self, keyword, domestic=True):
        """
        자연스러운 검색 (VBA 원본처럼 단순하게!)
        VBA 원본 로직:
        1. 쇼핑 검색창 있으면 → 직접 입력
        2. 없으면 → 통합검색 (VBA URL 파라미터) → 쇼핑 탭 클릭
        """
        from urllib.parse import quote
        from selenium.webdriver.common.keys import Keys
        
        print("=" * 70)
        print("🔍 검색 시작 (VBA 원본 방식)")
        print("=" * 70)
        
        # VBA 원본: 먼저 쇼핑 검색창이 있는지 확인
        print(f"  🔍 쇼핑 검색창 확인 중...")
        shopping_search_box = None
        
        # 쇼핑 페이지에 있는 경우에만 검색창 사용
        current_url = self.driver.current_url
        if "search.shopping.naver.com" in current_url:
            try:
                # VBA: SEL.FindElementByCss("._searchInput_search_text_83jy9", 0)
                shopping_search_box = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "._searchInput_search_text_83jy9"
                )
                if not shopping_search_box.is_displayed():
                    shopping_search_box = None
            except:
                shopping_search_box = None
        
        # 쇼핑 검색창이 있으면 직접 입력 (VBA 원본)
        if shopping_search_box:
            print(f"  ✅ 쇼핑 검색창 발견! 직접 입력...")
            try:
                shopping_search_box.clear()
                time.sleep(random.uniform(0.3, 0.5))
                
                # 키워드 입력
                for char in keyword:
                    shopping_search_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                time.sleep(random.uniform(0.5, 1))
                
                # 엔터
                shopping_search_box.send_keys(Keys.RETURN)
                time.sleep(random.uniform(1, 2))
                
                print(f"  ✅ 검색 완료!")
                return
            except Exception as e:
                print(f"  ⚠️  직접 검색 실패: {e}, 통합검색으로 전환...")
        
        # 쇼핑 검색창이 없으면 통합검색에서 시작 (VBA 원본)
        print(f"  🔍 통합검색으로 이동...")
        
        # 먼저 현재 페이지 확인
        current_url = self.driver.current_url
        print(f"  DEBUG: 현재 URL: {current_url}")
        
        # 네이버 메인이 아니면 메인으로 이동 (더 자연스럽게)
        if "naver.com" not in current_url or "search.shopping.naver.com" in current_url:
            print(f"  🏠 네이버 메인으로 먼저 이동...")
            self.driver.get("https://www.naver.com")
            time.sleep(random.uniform(1, 2))
        
        encoded = quote(keyword)
        # 🔥 VBA 원본과 동일한 URL 파라미터!
        search_url = f"https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&ssc=tab.nx.all&query={encoded}"
        
        print(f"  DEBUG: 검색 URL: {search_url}")
        self.driver.get(search_url)
        time.sleep(random.uniform(2, 3))
        
        print(f"  DEBUG: 이동 후 URL: {self.driver.current_url}")
        print(f"  DEBUG: 페이지 제목: {self.driver.title}")
        
        # 오류 페이지 체크
        if "오류" in self.driver.title or "error" in self.driver.title.lower():
            print(f"  ⚠️  오류 페이지 감지!")
            print(f"  💡 해결 방법:")
            print(f"     1. 로그인 상태 확인")
            print(f"     2. 브라우저를 닫고 다시 시작")
            print(f"     3. 잠시 후 다시 시도")
            return
        
        # VBA 원본: 10번 시도하면서 쇼핑 탭 찾기
        print(f"  🛒 쇼핑 탭 찾는 중...")
        
        # 현재 창 수 기록 (쇼핑 탭 클릭으로 새 창이 열렸는지 확인용)
        initial_window_count = len(self.driver.window_handles)
        print(f"  DEBUG: 시작 시 창 개수: {initial_window_count}")
        
        for attempt in range(10):
            # VBA: d.wait 1000 (1초 대기)
            time.sleep(1)
            
            current_window_count = len(self.driver.window_handles)
            print(f"  DEBUG: 시도 {attempt + 1}/10, 현재 창 개수: {current_window_count}")
            
            # VBA: If SEL.Windows.Count = 1 Then
            # 수정: 새 창이 열렸는지 확인 (초기 창 개수와 비교)
            if current_window_count == initial_window_count:
                # 쇼핑 탭 찾기 (여러 선택자 시도)
                shopping_tab = None
                
                # 선택자 목록 (우선순위 순)
                selectors = [
                    # 1. role="tab" + class="tab" (최신 네이버)
                    'a[role="tab"].tab',
                    # 2. role="tab" 속성만
                    'a[role="tab"]',
                    # 3. 구버전 선택자
                    '.flick_bx a',
                    # 4. XPath로 텍스트 검색 (최후의 수단)
                    None  # XPath는 별도 처리
                ]
                
                try:
                    for selector in selectors:
                        if selector:
                            # CSS 선택자
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            print(f"  DEBUG: '{selector}' 선택자로 {len(elements)}개 요소 발견")
                            
                            for elem in elements:
                                try:
                                    elem_text = elem.text.strip()
                                    if elem_text:
                                        print(f"  DEBUG: 요소 텍스트: '{elem_text}'")
                                    if elem_text == '쇼핑':
                                        shopping_tab = elem
                                        print(f"  ✅ 쇼핑 탭 발견! (선택자: {selector}, 시도 {attempt + 1}/10)")
                                        break
                                except:
                                    continue
                            
                            if shopping_tab:
                                break
                    
                    # CSS 선택자로 못 찾으면 XPath 시도
                    if not shopping_tab:
                        print(f"  DEBUG: XPath로 쇼핑 탭 검색 중...")
                        xpath_selectors = [
                            "//a[@role='tab' and contains(text(), '쇼핑')]",
                            "//a[contains(@class, 'tab') and contains(text(), '쇼핑')]",
                            "//a[contains(text(), '쇼핑')]"
                        ]
                        
                        for xpath in xpath_selectors:
                            try:
                                elements = self.driver.find_elements(By.XPATH, xpath)
                                print(f"  DEBUG: XPath로 {len(elements)}개 요소 발견")
                                if elements:
                                    shopping_tab = elements[0]
                                    print(f"  ✅ 쇼핑 탭 발견! (XPath, 시도 {attempt + 1}/10)")
                                    break
                            except:
                                continue
                
                except Exception as e:
                    print(f"  DEBUG: 쇼핑 탭 찾기 오류: {e}")
                
                if shopping_tab:
                    # 원래 창 저장
                    original_windows = self.driver.window_handles
                    
                    # VBA: 쇼핑탭.Click: d.wait 1000
                    try:
                        shopping_tab.click()
                        print(f"  🖱️  쇼핑 탭 클릭!")
                        time.sleep(2)  # 1초 → 2초 (새 창 열릴 시간)
                        
                        # VBA: SEL.SwitchToNextWindow
                        new_windows = self.driver.window_handles
                        if len(new_windows) > len(original_windows):
                            for window in new_windows:
                                if window not in original_windows:
                                    self.driver.switch_to.window(window)
                                    print(f"  ✅ 쇼핑 페이지로 전환 완료!")
                                    print(f"  DEBUG: 새 창 URL: {self.driver.current_url}")
                                    break
                        
                        break  # 성공하면 루프 종료
                    except Exception as e:
                        print(f"  ⚠️  클릭 오류: {e}")
                        import traceback
                        traceback.print_exc()
            else:
                # 새 창이 열렸음 (쇼핑 탭 클릭 성공)
                print(f"  ✅ 새 창 감지! (창 {initial_window_count}개 → {current_window_count}개)")
                break
        
        print("=" * 70)
        print("🔍 검색 완료")
        print("=" * 70)
        
        # VBA: If SEL.Windows.Count = 1 Then GoTo passKeyword
        # 수정: 초기 창 개수와 비교
        final_window_count = len(self.driver.window_handles)
        if final_window_count == initial_window_count:
            print(f"  ⚠️  쇼핑 탭 클릭 실패! (창 개수 변화 없음: {initial_window_count}개)")
            print(f"  ℹ️  직접 쇼핑 URL로 이동 시도...")
            
            # 최후의 수단: 직접 쇼핑 검색 URL로 이동
            from urllib.parse import quote
            encoded = quote(keyword)
            shopping_url = f"https://search.shopping.naver.com/search/all?where=all&frm=NVSCTAB&query={encoded}"
            print(f"  DEBUG: 직접 이동 URL: {shopping_url}")
            self.driver.get(shopping_url)
            time.sleep(2)
            return
        
        # VBA: d.wait 1000
        time.sleep(2)  # 1초 → 2초 (페이지 로딩 대기)
        
        # 🆕 쇼핑 페이지 로딩 후 오류 체크
        print(f"  🔍 쇼핑 페이지 상태 확인...")
        print(f"  DEBUG: 현재 URL: {self.driver.current_url}")
        print(f"  DEBUG: 페이지 제목: {self.driver.title}")
        
        # 오류 페이지 감지
        if "오류" in self.driver.title or "error" in self.driver.title.lower():
            print(f"  ⚠️  ⚠️  ⚠️  오류 페이지 감지! ⚠️  ⚠️  ⚠️")
            print(f"  ")
            print(f"  🚨 네이버가 자동화를 감지했습니다!")
            print(f"  ")
            print(f"  💡 해결 방법:")
            print(f"     1. 브라우저를 수동으로 조작해서 정상 페이지로 이동")
            print(f"     2. 또는 엔터를 눌러 다음 키워드로 건너뛰기")
            print(f"  ")
            input("  ⏸️  계속하려면 엔터를 누르세요...")
            return
    
    
    def _click_page_button(self, target_page):
        """
        VBA: Sub 다음페이지넘김(SEL As ChromeDriver, 페이지 As Long)
        페이지네이션 - Selenium 클릭 방식으로 페이지 이동
        
        Args:
            target_page: 이동할 페이지 번호
        """
        print(f"  🔘 {target_page}페이지로 이동 중...")
        
        try:
            # 페이지 버튼을 찾기 위한 여러 셀렉터 시도
            selectors = [
                # data-shp-contents-id 속성 사용 (가장 명확)
                f"a.pagination_btn_page__utqBz[data-shp-contents-id='{target_page}']",
                # 텍스트가 target_page인 페이지네이션 버튼
                f"a.pagination_btn_page__utqBz",
                # 백업: 일반 페이지네이션 링크
                ".pagination_num__qsa2U a"
            ]
            
            page_button = None
            used_selector = None
            
            # 첫 번째 셀렉터로 시도 (가장 정확한 방법)
            try:
                page_button = self.driver.find_element(By.CSS_SELECTOR, selectors[0])
                used_selector = selectors[0]
                print(f"  ✅ data-shp-contents-id로 버튼 찾음")
            except:
                # 두 번째 방법: 모든 버튼 찾아서 텍스트로 매칭
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selectors[1])
                    for btn in buttons:
                        if btn.text.strip() == str(target_page):
                            page_button = btn
                            used_selector = selectors[1]
                            print(f"  ✅ 텍스트 매칭으로 버튼 찾음")
                            break
                except:
                    pass
            
            if not page_button:
                print(f"  ❌ {target_page}페이지 버튼을 찾을 수 없습니다.")
                return False
            
            # 버튼이 보일 때까지 스크롤
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", page_button)
            time.sleep(0.5)
            
            # 클릭 시도 (여러 방법)
            click_success = False
            
            # 방법 1: 일반 클릭
            try:
                page_button.click()
                click_success = True
                print(f"  ✅ 일반 클릭 성공")
            except Exception as e1:
                print(f"  ⚠️  일반 클릭 실패: {e1}")
                
                # 방법 2: JavaScript 클릭
                try:
                    self.driver.execute_script("arguments[0].click();", page_button)
                    click_success = True
                    print(f"  ✅ JavaScript 클릭 성공")
                except Exception as e2:
                    print(f"  ⚠️  JavaScript 클릭 실패: {e2}")
                    
                    # 방법 3: ActionChains 클릭
                    try:
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(self.driver)
                        actions.move_to_element(page_button).click().perform()
                        click_success = True
                        print(f"  ✅ ActionChains 클릭 성공")
                    except Exception as e3:
                        print(f"  ❌ ActionChains 클릭 실패: {e3}")
            
            if not click_success:
                print(f"  ❌ 모든 클릭 방법 실패")
                return False
            
            # 페이지 로딩 대기
            time.sleep(2)
            
            # 🆕 최상단으로 스크롤
            print(f"  ⬆️  페이지 최상단으로 이동...")
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # 기본 페이지 로딩 대기
            self._wait_for_page_load()
            
            # 페이지 전환 확인
            try:
                # 활성화된 페이지 버튼 찾기
                active_button = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    ".pagination_num__qsa2U a.pagination_on__hQbxh, .pagination_on__hQbxh"
                )
                active_page_num = active_button.text.strip()
                
                if active_page_num == str(target_page):
                    print(f"  ✅ {target_page}페이지 전환 확인!")
                else:
                    print(f"  ⚠️  페이지 불일치: 요청={target_page}, 실제={active_page_num}")
                    return False
            except Exception as e:
                print(f"  ⚠️  페이지 확인 실패: {e}")
                # 활성 버튼을 못 찾아도 상품 확인으로 넘어감
            
            # 🆕 Lazy load로 40개 상품 모두 로드
            print(f"  📜 페이지 {target_page}의 상품 로딩 중 (목표: 40개)...")
            self._fast_lazy_load(max_attempts=20)
            
            # 최종 확인: 상품 개수 체크
            products = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".product_item__KQayS, .adProduct_item__T7utB"
            )
            
            if len(products) > 0:
                print(f"  ✅ 상품 {len(products)}개 로드 완료")
                
                # 40개 미만이면 경고
                if len(products) < 40:
                    print(f"  ⚠️  예상보다 적은 상품 (목표: 40개, 실제: {len(products)}개)")
                    print(f"      → 마지막 페이지이거나 일부 상품만 있을 수 있습니다.")
                
                return True
            else:
                print(f"  ⚠️  상품이 감지되지 않음!")
                return False
            
        except Exception as e:
            print(f"  ❌ 페이지 이동 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
    def _wait_for_page_load(self):
        """
        VBA: Sub 랜딩기다리기(SEL As ChromeDriver)
        페이지 로딩 대기
        """
        # VBA: SEL.ExecuteScript ("window.scrollBy(0, 20000)"): d.wait 1000
        try:
            self.driver.execute_script("window.scrollBy(0, 20000)")
            time.sleep(1)
        except:
            pass
        
        # VBA: Set 랜딩오브젝트 = SEL.FindElementByClass("basicList_list_basis__uNBZx", 0)
        max_wait = 10
        for i in range(max_wait):
            try:
                list_element = self.driver.find_element(By.CLASS_NAME, "basicList_list_basis__uNBZx")
                if list_element:
                    return  # 로딩 완료
            except:
                pass
            
            # VBA: 검색결과 없음 체커
            try:
                no_result = self.driver.find_element(By.CSS_SELECTOR, ".noResultWithBestResults_svg_noresult__uF7vF")
                if no_result:
                    print(f"  ⚠️  검색 결과 없음")
                    return
            except:
                pass
            
            time.sleep(0.5)
        
        # 페이지가 제대로 로딩되었는지 확인
        try:
            # 쇼핑 검색 결과가 있는지 확인
            time.sleep(1)
            products = self.driver.find_elements(By.CSS_SELECTOR, ".product_item__KQayS")
            print(f"  ✅ 쇼핑 페이지 정상! (상품 {len(products)}개 감지)")
        except Exception as e:
            print(f"  ⚠️  페이지 로딩 확인 실패: {e}")
        
        time.sleep(1)
        
        # 책 검색으로 빠진 경우 처리 (VBA 원본)
        try:
            # VBA: SEL.FindElementByCss(".bookSearchNotice_show_all__unpDH", 0).Click
            book_notice = self.driver.find_element(
                By.CSS_SELECTOR,
                ".bookSearchNotice_show_all__unpDH"
            )
            book_notice.click()
            print(f"  📚 책 검색 감지! 가격비교로 전환...")
            time.sleep(1)
        except:
            pass
    
    def _fast_lazy_load(self, max_attempts=20):
        """빠른 Lazy loading 처리 (자연스러운 스크롤)"""
        print("=" * 70)
        print("📜 DEBUG: _fast_lazy_load() 시작")
        print(f"  DEBUG: 현재 URL: {self.driver.current_url}")
        print(f"  DEBUG: 시작 스크롤 위치: {self.driver.execute_script('return window.pageYOffset')}")
        print("=" * 70)
        
        # 🆕 페이지 로딩 완료 대기 (확장 프로그램: search-content.js 323줄)
        print(f"  ⏳ 페이지 초기 로딩 대기 (3초)...")
        time.sleep(3)  # 2초 → 3초로 증가
        
        # 🆕 Next.js 데이터 로딩 확인 (최대 10초)
        print(f"  🔍 Next.js 데이터 로딩 확인 중...")
        data_loaded = False
        for i in range(20):  # 최대 20번 시도 (10초)
            try:
                has_data = self.driver.execute_script("""
                    return window.__NEXT_DATA__ 
                        && window.__NEXT_DATA__.props 
                        && window.__NEXT_DATA__.props.pageProps;
                """)
                if has_data:
                    data_loaded = True
                    print(f"  ✅ Next.js 데이터 로딩 완료! (시도 {i+1}/20)")
                    break
            except Exception as e:
                if i == 0:  # 첫 시도에서만 에러 출력
                    print(f"  DEBUG: Next.js 체크 오류: {e}")
            time.sleep(0.5)
        
        if not data_loaded:
            # 실패 원인 상세 분석
            print(f"  ⚠️  Next.js 데이터 로딩 실패!")
            try:
                # 현재 URL 확인
                current_url = self.driver.current_url
                print(f"  DEBUG: 현재 URL: {current_url}")
                
                # window.__NEXT_DATA__ 존재 여부
                has_next_data = self.driver.execute_script("return typeof window.__NEXT_DATA__ !== 'undefined';")
                print(f"  DEBUG: window.__NEXT_DATA__ 존재: {has_next_data}")
                
                if has_next_data:
                    # __NEXT_DATA__의 구조 확인
                    has_props = self.driver.execute_script("return window.__NEXT_DATA__ && window.__NEXT_DATA__.props !== undefined;")
                    print(f"  DEBUG: __NEXT_DATA__.props 존재: {has_props}")
                    
                    if has_props:
                        has_pageProps = self.driver.execute_script("return window.__NEXT_DATA__.props.pageProps !== undefined;")
                        print(f"  DEBUG: __NEXT_DATA__.props.pageProps 존재: {has_pageProps}")
                        
                        # pageProps의 키 확인
                        pageProps_keys = self.driver.execute_script("""
                            if (window.__NEXT_DATA__ && window.__NEXT_DATA__.props && window.__NEXT_DATA__.props.pageProps) {
                                return Object.keys(window.__NEXT_DATA__.props.pageProps);
                            }
                            return [];
                        """)
                        print(f"  DEBUG: pageProps 키들: {pageProps_keys}")
                
                # 쇼핑 페이지인지 확인
                if 'search.shopping.naver.com' not in current_url:
                    print(f"  ⚠️  쇼핑 페이지가 아닙니다! (통합검색 또는 다른 페이지)")
                    print(f"  💡 쇼핑 탭을 클릭했는지 확인하세요.")
                
            except Exception as debug_error:
                print(f"  DEBUG: 디버깅 중 오류: {debug_error}")
            
            print(f"  ℹ️  계속 진행... (상품 목록이 있으면 정상 동작)")
        
        target_count = 40  # 한 페이지 목표 개수
        no_change_count = 0  # 변화 없는 횟수 카운터
        prev_item_count = 0  # 이전 아이템 수
        
        for attempt in range(max_attempts):
            # 🔧 요소를 찾기 전에 잠시 대기 (DOM 업데이트 시간 확보)
            time.sleep(0.3)
            
            # 현재 아이템 수 확인
            items = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".product_item__KQayS, .adProduct_item__T7utB"
            )
            current_item_count = len(items)
            
            print(f"  DEBUG: Lazy load 시도 {attempt + 1}/{max_attempts} - 아이템 수: {current_item_count}/{target_count}")
            
            # 🔧 추가 디버깅: CSS 선택자별로 확인
            if attempt == 0 and current_item_count == 0:
                product_items = self.driver.find_elements(By.CSS_SELECTOR, ".product_item__KQayS")
                ad_items = self.driver.find_elements(By.CSS_SELECTOR, ".adProduct_item__T7utB")
                print(f"  DEBUG: 일반 상품: {len(product_items)}개, 광고 상품: {len(ad_items)}개")
                
                # 대체 선택자 시도
                alt_items = self.driver.find_elements(By.CSS_SELECTOR, "[class*='product_item'], [class*='adProduct_item']")
                print(f"  DEBUG: 대체 선택자로 찾은 상품: {len(alt_items)}개")
            
            # 목표 달성 확인
            if current_item_count >= target_count:
                print(f"  ✅ 목표 아이템 수 달성!")
                break
            
            # 🔧 변화 없음 감지 (3번 연속 변화가 없으면 종료)
            if current_item_count == prev_item_count:
                no_change_count += 1
                print(f"  ⚠️  상품 수 변화 없음 ({no_change_count}/3)")
                
                if no_change_count >= 3:
                    print(f"  ⚠️  3번 연속 변화 없음 - 더 이상 로드할 상품이 없는 것으로 판단")
                    print(f"  ℹ️  현재 {current_item_count}개 상품으로 진행합니다.")
                    break
            else:
                no_change_count = 0  # 변화가 있으면 카운터 리셋
            
            prev_item_count = current_item_count
            
            # 🆕 자연스러운 스크롤 (smooth behavior - 확장 프로그램 방식)
            scroll_before = self.driver.execute_script('return window.pageYOffset')
            page_height = self.driver.execute_script('return document.body.scrollHeight')
            
            # smooth 스크롤 사용
            self.driver.execute_script("""
                window.scrollTo({
                    top: window.pageYOffset + 800,
                    behavior: 'smooth'
                });
            """)
            
            # 🔧 스크롤이 실제로 적용될 시간 확보 (smooth 스크롤은 애니메이션)
            time.sleep(0.5)
            
            scroll_after = self.driver.execute_script('return window.pageYOffset')
            print(f"  DEBUG: 스크롤 {scroll_before} → {scroll_after} (페이지 높이: {page_height})")
            
            # 🔧 스크롤이 더 이상 진행되지 않는 경우 (페이지 끝)
            if scroll_before == scroll_after:
                print(f"  ⚠️  스크롤이 더 이상 진행되지 않음 (페이지 끝)")
                # 마지막으로 한 번 더 대기 후 요소 확인
                time.sleep(1.5)
                final_items = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    ".product_item__KQayS, .adProduct_item__T7utB"
                )
                print(f"  ℹ️  최종 {len(final_items)}개 상품으로 진행합니다.")
                break
            
            # 🆕 랜덤 대기 시간 (1초 ~ 1.8초 - 더 여유 있게)
            random_delay = 1.0 + random.random() * 0.8
            time.sleep(random_delay)
            
            # 5번마다 조금 더 대기 (읽는 척)
            if attempt % 5 == 0 and attempt > 0:
                time.sleep(random.uniform(1.0, 2.0))
    
    def find_and_click_product_by_uid(self, target_uid, max_pages=5, max_scroll_attempts=20):
        """
        상품 UID를 기준으로 상품을 찾아서 클릭 (최대 5페이지까지 검색)
        
        다양한 ID 타입을 지원합니다:
        - nv_mid: 카탈로그 상품 ID
        - catalog_nv_mid: 카탈로그 상품 ID (대체)
        - chnl_prod_no: 스마트스토어 채널 상품 번호
        
        Args:
            target_uid: 찾을 상품의 UID (nv_mid 또는 chnl_prod_no)
            max_pages: 최대 검색할 페이지 수 (기본값: 5)
            max_scroll_attempts: 페이지당 최대 스크롤 시도 횟수
        
        Returns:
            bool: 성공 여부
        """
        print(f"\n{'='*70}")
        print(f"🎯 상품 찾기: target_uid={target_uid} (최대 {max_pages}페이지)")
        print(f"   (nv_mid, catalog_nv_mid, chnl_prod_no 모두 확인)")
        print(f"{'='*70}")
        
        # 여러 페이지 검색
        for page in range(1, max_pages + 1):
            print(f"\n📄 {page}페이지 검색 중...")
            
            # 2페이지부터는 페이지 이동 필요 (Lazy load 포함)
            if page > 1:
                success = self._click_page_button(page)
                if not success:
                    print(f"  ⚠️  {page}페이지 이동 실패, 검색 종료")
                    break
            else:
                # 1페이지는 Lazy loading으로 상품 로딩
                print(f"  📜 1페이지 상품 로딩 중 (목표: 40개)...")
                self._fast_lazy_load(max_attempts=max_scroll_attempts)
            
            try:
                # 모든 상품 요소 가져오기
                store_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    ".product_item__KQayS, .adProduct_item__T7utB"
                )
                
                print(f"  📦 {page}페이지에서 {len(store_elements)}개 상품 확인 (목표: 40개)")
                
                # 40개 미만이면 경고
                if len(store_elements) < 40:
                    print(f"  ⚠️  예상보다 적은 상품! 마지막 페이지이거나 로딩 문제일 수 있습니다.")
                
                # 각 상품의 ID 확인
                for idx, store in enumerate(store_elements):
                    try:
                        # 상품명 링크 찾기
                        product_link = store.find_element(
                            By.CSS_SELECTOR, 
                            ".product_link__aFnaq, .adProduct_link__hNwpz"
                        )
                        
                        # data-shp-contents-dtl에서 여러 ID 추출
                        contents_dtl = product_link.get_attribute('data-shp-contents-dtl')
                        
                        if contents_dtl:
                            try:
                                dtl_array = json.loads(contents_dtl)
                                
                                # 🆕 여러 ID 타입 추출
                                id_fields = {
                                    'nv_mid': None,
                                    'catalog_nv_mid': None,
                                    'chnl_prod_no': None
                                }
                                
                                for obj in dtl_array:
                                    key = obj.get('key')
                                    if key in id_fields and obj.get('value'):
                                        id_fields[key] = str(obj['value'])
                                
                                # 디버깅: 모든 상품의 ID 정보 출력
                                id_info = ", ".join([f"{k}={v}" for k, v in id_fields.items() if v])
                                print(f"    [{idx+1}] {id_info}")
                                
                                # 🆕 target_uid와 모든 ID 비교
                                matched = False
                                matched_field = None
                                
                                for field_name, field_value in id_fields.items():
                                    if field_value and field_value == str(target_uid):
                                        matched = True
                                        matched_field = field_name
                                        break
                                
                                if matched:
                                    print(f"\n  ✅ 일치하는 상품 발견! ({matched_field}={target_uid})")
                                    print(f"     페이지: {page}, 인덱스: {idx+1}")
                                    
                                    # 상품 정보 출력
                                    try:
                                        product_name = product_link.text.strip()
                                        print(f"  📦 상품명: {product_name[:50]}...")
                                    except:
                                        pass
                                    
                                    # 상품으로 스크롤
                                    self.driver.execute_script(
                                        "arguments[0].scrollIntoView({block: 'center'});", 
                                        store
                                    )
                                    time.sleep(0.5)
                                    
                                    # 클릭
                                    print(f"  🖱️  상품 클릭...")
                                    product_link.click()
                                    time.sleep(2)
                                    
                                    print(f"  ✅ 상품 페이지로 이동 완료!")
                                    print(f"  🔗 현재 URL: {self.driver.current_url}")
                                    return True
                            
                            except json.JSONDecodeError:
                                continue
                    
                    except Exception as e:
                        continue
                
                print(f"  ⏭️  {page}페이지에서 상품을 찾지 못했습니다.")
            
            except Exception as e:
                print(f"  ⚠️  {page}페이지 검색 중 오류: {e}")
                continue
        
        print(f"\n  ❌ {max_pages}페이지까지 검색했지만 target_uid={target_uid}인 상품을 찾지 못했습니다.")
        return False
    
    def _extract_store_data(self, page=1):
        """
        화면의 각 상품 요소를 순회하며 스토어 정보 추출 (VBA 원본 방식)
        VBA: For Each 스토어 In 스토어들
        
        Args:
            page: 현재 페이지 번호 (ranking offset 계산용)
        """
        try:
            print(f"  🔍 1단계: 상품 요소 추출 시작...")
            
            # === 1단계: 톡톡 ID를 JSON에서 추출 (VBA: 631-662줄) ===
            talk_id_dict = {}
            try:
                script = self.driver.find_element(By.ID, "__NEXT_DATA__")
                data = json.loads(script.get_attribute('innerText'))
                products = data.get('props', {}).get('pageProps', {}).get('initialState', {}).get('products', {}).get('list', [])
                
                # VBA: For Each 제이슨스토어 In JSON(...)
                for product in products:
                    item = product.get('item', {})
                    product_name = item.get('productName', '')
                    talk_id = item.get('mallInfoCache', {}).get('talkAccountId', '')
                    
                    # VBA: If 스토어아디 <> "" And 톡스토어 <> "" Then
                    if product_name and talk_id:
                        talk_id_dict[product_name] = talk_id
                
                print(f"  ✅ 톡톡 ID {len(talk_id_dict)}개 추출")
            except Exception as e:
                print(f"  ⚠️  톡톡 ID 추출 실패: {e}")
            
            # === 2단계: 화면 요소에서 스토어 정보 추출 ===
            # VBA: Set 스토어들 = SEL.FindElementsByCss(".product_item__KQayS, .adProduct_item__T7utB", 0)
            store_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".product_item__KQayS, .adProduct_item__T7utB"
            )
            
            print(f"  ✅ 총 상품 요소: {len(store_elements)}개")
            
            results = []
            success_count = 0  # 성공적으로 처리된 상품 카운터
            
            # 🔍 디버깅: 첫 번째 상품의 ranking 정보 출력
            if len(store_elements) > 0:
                try:
                    first_store = store_elements[0]
                    first_link = first_store.find_element(By.CSS_SELECTOR, "a[data-shp-contents-id]")
                    print(f"  🔍 [디버깅] 첫 번째 상품 링크 속성:")
                    print(f"    - data-shp-contents-id: {first_link.get_attribute('data-shp-contents-id')}")
                    print(f"    - data-shp-contents-grp: {first_link.get_attribute('data-shp-contents-grp')}")
                    print(f"    - data-shp-contents-rank: {first_link.get_attribute('data-shp-contents-rank')}")
                    dtl = first_link.get_attribute('data-shp-contents-dtl')
                    if dtl:
                        print(f"    - data-shp-contents-dtl (전체):")
                        try:
                            dtl_parsed = json.loads(dtl)
                            for item in dtl_parsed:
                                print(f"      * {item.get('key')}: {item.get('value')}")
                        except:
                            print(f"      (파싱 실패) {dtl}")
                    else:
                        print(f"    - data-shp-contents-dtl: None")
                except Exception as e:
                    print(f"  ⚠️  [디버깅] 첫 번째 상품 링크 확인 실패: {e}")
            
            # VBA: For Each 스토어 In 스토어들
            for idx, store in enumerate(store_elements):
                try:
                    # VBA: 스토어.ScrollIntoView
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", store)
                    time.sleep(0.05)  # 짧은 대기
                    
                    # VBA: 스토어주소 = 스토어.FindElementByCss(".product_mall_title__sJPEp a", 0).Attribute("href")
                    try:
                        mall_link = store.find_element(By.CSS_SELECTOR, ".product_mall_title__sJPEp a, .adProduct_mall__grJaU")
                        store_url = mall_link.get_attribute('href')
                    except:
                        continue  # 스토어 링크 없으면 패스
                    
                    # VBA: If InStr(스토어주소, "naver") = 0 Then GoTo pass
                    if 'naver' not in store_url:
                        continue
                    
                    # 스마트스토어만 필터링
                    if 'smartstore.naver.com' not in store_url and 'brand.naver.com' not in store_url:
                        continue
                    
                    # VBA: 스토어이름 = 스토어.FindElementByCss(".product_mall__0cRyd", 0).Text
                    try:
                        mall_name_elem = store.find_element(By.CSS_SELECTOR, ".product_mall__0cRyd, .adProduct_mall__grJaU, .product_catalog__FbLL3")
                        mall_name = mall_name_elem.text.strip()
                        
                        # VBA: If 스토어이름 = "쇼핑몰별 최저가" Then GoTo pass
                        if mall_name in ["쇼핑몰별 최저가", "브랜드 카탈로그"]:
                            continue
                    except:
                        mall_name = ""
                    
                    # VBA: 상품명 = 스토어.FindElementByCss(".product_link__aFnaq", 0).Text
                    try:
                        product_link = store.find_element(By.CSS_SELECTOR, ".product_link__aFnaq, .adProduct_link__hNwpz")
                        product_name = product_link.text.strip()
                        product_url = product_link.get_attribute('href')
                    except:
                        continue
                    
                    # 스토어 ID 추출 (VBA 로직)
                    store_id = ''
                    if 'smartstore.naver.com%2F' in store_url:
                        # URL 인코딩된 경우
                        store_id = store_url.split('smartstore.naver.com%2F')[1].split('&')[0]
                    elif 'smartstore.naver.com/' in store_url:
                        # 일반 경우
                        store_id = store_url.split('smartstore.naver.com/')[1].split('/')[0].split('?')[0]
                    elif 'brand.naver.com/' in store_url:
                        store_id = store_url.split('brand.naver.com/')[1].split('/')[0].split('?')[0]
                    
                    if not store_id:
                        continue
                    
                    # 브랜드스토어인지 확인
                    is_brand = 'brand.naver.com' in store_url
                    
                    # 톡톡 ID 매칭
                    talk_id = talk_id_dict.get(product_name, '')
                    
                    # Extension: Ranking 정보 추출 (search-content.js 471-596줄)
                    ranking = None
                    is_ad = False
                    price = 0  # 🆕 가격 초기화
                    nv_mid = None  # 🆕 nv_mid 초기화
                    
                    try:
                        # 상품명 링크에서 ranking 속성 찾기 (VBA: 상품명 링크 = product_link)
                        # product_link는 이미 위에서 찾았으므로 그것을 사용
                        product_link_elem = product_link  # 이미 찾은 상품명 링크 재사용
                        contents_grp = product_link_elem.get_attribute('data-shp-contents-grp')
                        contents_rank = product_link_elem.get_attribute('data-shp-contents-rank')
                        contents_dtl = product_link_elem.get_attribute('data-shp-contents-dtl')
                        
                        # 광고 여부
                        is_ad = (contents_grp == 'ad')
                        
                        if success_count < 3:
                            print(f"    🔍 성공 {success_count}: contents_grp={contents_grp}, is_ad={is_ad}")
                        
                        # Extension 방식: contentsDtl JSON 파싱으로 정확한 순위 추출
                        rank_offset = (page - 1) * 40
                        
                        if contents_dtl:
                            try:
                                dtl_array = json.loads(contents_dtl)
                                
                                # 🆕 nv_mid 추출 (이미 위에서 선언했으므로 재선언 금지!)
                                # 'nv_mid' 또는 'catalog_nv_mid' 둘 다 시도
                                nv_mid_obj = next((obj for obj in dtl_array if obj.get('key') in ['nv_mid', 'catalog_nv_mid']), None)
                                if nv_mid_obj and nv_mid_obj.get('value'):
                                    nv_mid = str(nv_mid_obj['value'])
                                    if success_count < 3:
                                        print(f"    ✅ 성공 {success_count}: nv_mid 추출 성공 ({nv_mid_obj.get('key')}) - {nv_mid}")
                                elif success_count < 3:
                                    print(f"    ⚠️  성공 {success_count}: nv_mid 추출 실패 - nv_mid_obj={nv_mid_obj}")
                                    # dtl_array의 모든 키 출력
                                    all_keys = [obj.get('key') for obj in dtl_array]
                                    print(f"    📋 성공 {success_count}: dtl_array에 있는 키들: {all_keys}")
                                
                                # 🆕 가격 추출
                                price_obj = next((obj for obj in dtl_array if obj.get('key') == 'price'), None)
                                if price_obj and price_obj.get('value'):
                                    try:
                                        price = int(price_obj['value'])
                                    except:
                                        price = 0
                                
                                if is_ad:
                                    # 광고의 경우: ad_expose_order
                                    ad_order_obj = next((obj for obj in dtl_array if obj.get('key') == 'ad_expose_order'), None)
                                    if ad_order_obj and ad_order_obj.get('value'):
                                        ranking = int(ad_order_obj['value']) + rank_offset
                                        if success_count < 3:
                                            print(f"    ✅ 성공 {success_count}: 광고 순위 추출 - ad_expose_order={ad_order_obj.get('value')}, offset={rank_offset}, final={ranking}")
                                else:
                                    # 일반 상품: organic_expose_order
                                    organic_order_obj = next((obj for obj in dtl_array if obj.get('key') == 'organic_expose_order'), None)
                                    if organic_order_obj and organic_order_obj.get('value'):
                                        ranking = int(organic_order_obj['value']) + rank_offset
                                        if success_count < 3:
                                            print(f"    ✅ 성공 {success_count}: 일반 순위 추출 - organic_expose_order={organic_order_obj.get('value')}, offset={rank_offset}, final={ranking}")
                                    elif success_count < 3:
                                        print(f"    ⚠️  성공 {success_count}: organic_expose_order를 찾을 수 없음")
                                
                                if ranking is None and success_count < 3:
                                    print(f"    ⚠️  성공 {success_count}: JSON 파싱 성공했지만 ranking이 None (is_ad={is_ad})")
                                    
                            except Exception as json_err:
                                # JSON 파싱 실패 시 contents_rank 사용 (fallback)
                                if success_count < 3:
                                    print(f"    ⚠️  성공 {success_count}: JSON 파싱 실패 - {json_err}")
                                if contents_rank:
                                    ranking = int(contents_rank) + rank_offset
                                    if success_count < 3:
                                        print(f"    ℹ️  성공 {success_count}: Fallback으로 contents_rank 사용 - {ranking}")
                        elif contents_rank:
                            # contentsDtl이 없으면 contents_rank 사용
                            ranking = int(contents_rank) + rank_offset
                            if success_count < 3:
                                print(f"    ℹ️  성공 {success_count}: contentsDtl 없음, contents_rank 사용 - {ranking}")
                        else:
                            if success_count < 3:
                                print(f"    ⚠️  성공 {success_count}: contents_dtl과 contents_rank 모두 없음")
                            
                    except Exception as e:
                        # 디버깅용
                        if success_count < 3:
                            print(f"    ❌ 성공 {success_count}: Ranking 추출 완전 실패 - {e}")
                            import traceback
                            traceback.print_exc()
                    
                    # 디버깅: 처음 3개 상품의 최종 ranking 정보 출력
                    if success_count < 3:
                        print(f"    📊 성공 {success_count} 최종: ranking={ranking}, is_ad={is_ad}, store_id={store_id}")
                    
                    # VBA: 스토어리뷰수 (832-868줄)
                    review_count = 0
                    
                    # 여러 선택자 시도
                    review_selectors = [
                        ".adProduct_count__J5x57",
                        ".product_num__WuH26",
                        ".product_etc__Z7jnS em",  # 리뷰수가 em 태그 안에 있을 수 있음
                        "[class*='product'][class*='num']",  # 클래스명에 product와 num이 포함된 것
                    ]
                    
                    review_found = False
                    for selector in review_selectors:
                        try:
                            review_elem = store.find_element(By.CSS_SELECTOR, selector)
                            review_text = review_elem.text.strip()
                            if success_count < 3:
                                print(f"    🔍 성공 {success_count}: 리뷰 요소 발견 ({selector}) - text='{review_text}'")
                            if review_text:
                                review_count = self._parse_review_count(review_text)
                                if success_count < 3:
                                    print(f"    ✅ 성공 {success_count}: 리뷰수 파싱 완료 - {review_count}")
                                review_found = True
                                break
                        except:
                            continue
                    
                    if not review_found:
                        # VBA: 리뷰수가 없으면 스팬들에서 찾기
                        if success_count < 3:
                            print(f"    ⚠️  성공 {success_count}: 직접 선택자 실패, 스팬에서 검색...")
                        try:
                            spans = store.find_elements(By.CSS_SELECTOR, ".product_etc__Z7jnS, .adProduct_review__DQla5, .adProduct_etc__AM_WB")
                            if success_count < 3:
                                print(f"    🔍 성공 {success_count}: 스팬 {len(spans)}개 발견")
                            for span in spans:
                                span_text = span.text.strip()
                                if success_count < 3:
                                    print(f"       - 스팬 텍스트: '{span_text}'")
                                if '리뷰' in span_text:
                                    if '(' in span_text:  # 광고의 경우: 별점 5 리뷰(1)
                                        review_count = self._parse_review_count(span_text.split('(')[1].split(')')[0])
                                    else:
                                        review_count = self._parse_review_count(span_text)
                                    if success_count < 3:
                                        print(f"    ✅ 성공 {success_count}: 스팬에서 리뷰수 추출 - {review_count}")
                                    break
                        except Exception as e2:
                            if success_count < 3:
                                print(f"    ❌ 성공 {success_count}: 스팬 검색도 실패 - {e2}")
                    
                    # VBA: 스토어찜수 (839-873줄)
                    like_count = 0
                    try:
                        spans = store.find_elements(By.CSS_SELECTOR, ".product_etc__Z7jnS, .adProduct_review__DQla5, .adProduct_etc__AM_WB")
                        for span in spans:
                            span_text = span.text.strip()
                            if '찜' in span_text:
                                like_count = self._parse_review_count(span_text.replace('찜', ''))
                                break
                    except:
                        pass
                    
                    # VBA: 스토어등급, 스토어서비스등급 (875-903줄)
                    store_grade = ""
                    service_grade = ""
                    try:
                        grade_container = store.find_element(By.CSS_SELECTOR, ".product_mall_area__32KR3, .adProduct_mall_area__XKm_G")
                        grade_elems = grade_container.find_elements(By.CSS_SELECTOR, ".product_grade__O_5f5, .adProduct_grade__wZiUX")
                        
                        for i, grade_elem in enumerate(grade_elems):
                            grade_text = grade_elem.text.strip()
                            if grade_text:
                                if grade_text == "굿서비스":
                                    service_grade = grade_text
                                elif not store_grade:
                                    store_grade = grade_text
                                elif not service_grade:
                                    service_grade = grade_text
                    except:
                        pass
                    
                    # 디버깅: nv_mid 저장 전 최종 확인
                    if success_count < 3:
                        print(f"    💾 성공 {success_count}: 저장 전 nv_mid={nv_mid}, price={price}")
                    
                    # 결과 저장 (VBA 컬럼명 + Extension ranking) - 비활성화됨
                    # results.append({
                    #     '상품명': product_name,        # VBA: 상품명
                    #     '이름': mall_name,             # VBA: 이름 (스토어이름)
                    #     '스토어아이디': store_id,       # VBA: 스토어아이디
                    #     'url': f'https://brand.naver.com/{store_id}' if is_brand else f'https://smartstore.naver.com/{store_id}',  # VBA: url
                    #     '상품url': product_url,        # 상품 링크
                    #     'nv_mid': nv_mid,             # 🆕 상품 고유 ID
                    #     '가격': price,                 # 🆕 상품 가격
                    #     '스토어': '브랜드' if is_brand else '',  # VBA: 스토어 (브랜드 여부)
                    #     '리뷰수': review_count,         # VBA: 리뷰수
                    #     '찜수': like_count,             # VBA: 찜수
                    #     '등급': store_grade,           # VBA: 등급
                    #     '서비스': service_grade,        # VBA: 서비스
                    #     'ranking': ranking,            # Extension: 검색 순위
                    #     '광고': '광고' if is_ad else '',  # Extension: 광고 여부
                    #     '톡톡아이디': talk_id,          # 톡톡 ID
                    #     '톡톡주소': f'https://talk.naver.com/ct/{talk_id}' if talk_id else '',  # VBA: 톡톡주소
                    # })
                    
                    success_count += 1  # 성공 카운터 증가
                    
                    if (idx + 1) % 10 == 0:
                        print(f"  📊 진행 중: {idx + 1}/{len(store_elements)}개 처리, {len(results)}개 추출")
                
                except Exception as e:
                    # 개별 상품 처리 실패는 무시하고 계속
                    continue
            
            print(f"  ✅ 1단계 완료: {len(results)}개 스마트스토어")
            return results
        
        except Exception as e:
            print(f"  ⚠️  데이터 추출 오류: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_review_count(self, text):
        """
        VBA 함수: 스스리뷰만처리 (1600-1614줄)
        리뷰/찜 수를 파싱 ("1,234" → 1234, "1.2만" → 12000)
        """
        if not text:
            return 0
        
        # VBA: 현재리뷰수 = Replace(현재리뷰수, " ", "")
        text = text.replace(' ', '')
        text = text.replace('리뷰', '')
        text = text.replace('(', '')
        text = text.replace(')', '')
        text = text.replace(',', '')
        
        if not text:
            return 0
        
        # VBA: If InStr(현재리뷰수, "만") <> 0 Then
        if '만' in text:
            try:
                number = text.replace('만', '')
                return int(float(number) * 10000)
            except:
                return 0
        else:
            try:
                return int(text)
            except:
                return 0
    
    def _get_store_info_from_api(self, store_id):
        """
        API(DB)에서 스토어 정보 조회 (VBA: getDataDB 함수)
        VBA: 2277-2307줄
        
        Returns:
            dict or None: 성공 시 스토어 정보, 실패 시 None
        """
        try:
            import requests
            
            url = f"https://api.mgunexcel.com/getssseller?id={store_id}"
            response = requests.get(url, timeout=5)
            
            # VBA: If InStr(res, "|") = 0 Then Exit Sub
            if "Internal Server Error" in response.text or "|" not in response.text:
                return None
            
            # VBA: resArr = Split(res, "|||")
            data = response.text.strip('"').split("|||")
            
            # VBA 컬럼 순서 (2289-2290줄: Resize(1, 18))
            # 스토어아이디(1) + 상호명(2) + 스토어설명(3) + ... 총 18개
            # API 응답: 0=키워드, 1=스토어ID, 2=상호명, 3=빈칸, 4=대표자, ...
            
            # VBA: If 값 = "None" Then 값 = ""
            def get_value(idx):
                if idx < len(data):
                    val = data[idx].strip()
                    return "" if val in ["None", ""] else val
                return ""
            
            # 연락처 처리 (VBA: 핸드폰번호 + 연락처)
            # 인덱스 5: 핸드폰번호 (010-xxxx-xxxx)
            # 인덱스 6: 일반전화 (064-xxxx-xxxx)
            cell_phone = get_value(5)  # 핸드폰번호
            just_phone = get_value(6)  # 연락처 (일반전화)
            
            # 둘 중 하나라도 있으면 사용 (VBA: 핸드폰 우선)
            contact = cell_phone if cell_phone else just_phone
            
            # VBA 컬럼명으로 반환
            return {
                '상호명': get_value(2),              # VBA: 상호명
                '대표자': get_value(4),              # VBA: 대표자
                '연락처': contact,                   # VBA: 연락처 (핸드폰 or 일반전화)
                '이메일': get_value(7),              # VBA: 이메일
                '사업자등록번호': get_value(8),       # VBA: 사업자등록번호
                '사업장소재지': get_value(9),         # VBA: 사업장소재지
                '통신판매업번호': get_value(10),      # VBA: 통신판매업번호
            }
        
        except Exception as e:
            print(f"    ⚠️  API 조회 실패: {e}")
            return None
    
    def _extract_detailed_info_by_crawling(self, store_id, is_brand=False):
        """
        스토어 프로필 페이지에서 상세 정보 크롤링 (VBA: 1268-1329줄 주석 코드)
        ⚠️ VBA에서는 실제로 사용되지 않음 (모두 주석 처리)
        """
        try:
            # VBA: If list.ListColumns("스토어").DataBodyRange(row) = "브랜드" Then
            if is_brand:
                profile_url = f"https://brand.naver.com/{store_id}/profile?cp=1"
            else:
                profile_url = f"https://smartstore.naver.com/{store_id}/profile?cp=1"
            
            print(f"    🔍 {store_id} 크롤링으로 상세 정보 추출 중...")
            self.driver.get(profile_url)
            time.sleep(random.uniform(1.0, 1.5))
            
            # ⚠️ 중요: "상세 정보 확인" 버튼 클릭 → 팝업 창 열림
            # 프로필 페이지에서 버튼을 눌러야 판매자 정보가 표시됨
            # 팝업: https://shopping.naver.com/popup/seller-info/{hash}/profile?...
            original_window = self.driver.current_window_handle
            
            try:
                # 다양한 셀렉터로 버튼 찾기 시도
                detail_button = None
                button_selectors = [
                    "//button[contains(text(), '상세 정보 확인')]",
                    "//button[contains(text(), '상세정보')]",
                    "//a[contains(text(), '상세 정보 확인')]",
                    "//a[contains(text(), '상세정보')]",
                    "//div[contains(@class, 'detail')]//button",
                    "//button[contains(@class, 'detail')]"
                ]
                
                for selector in button_selectors:
                    try:
                        detail_button = self.driver.find_element(By.XPATH, selector)
                        if detail_button:
                            print(f"    🔘 '상세 정보 확인' 버튼 클릭 중...")
                            detail_button.click()
                            time.sleep(2.0)  # 팝업 열릴 때까지 대기
                            break
                    except:
                        continue
                
                # 팝업 창으로 전환
                all_windows = self.driver.window_handles
                if len(all_windows) > 1:
                    # 새 팝업 창으로 전환
                    for window in all_windows:
                        if window != original_window:
                            self.driver.switch_to.window(window)
                            print(f"    🪟 팝업 창으로 전환됨")
                            break
                    
                    # 단순히 3초 대기 (사용자가 캡챠 풀 시간 + 페이지 로딩 시간)
                    print(f"    ⏳ 페이지 로딩 대기 중 (3초)...")
                    time.sleep(3)
                    
                    time.sleep(1.0)  # 추가 안정화 대기
                else:
                    print(f"    ⚠️  팝업이 열리지 않음, 현재 페이지에서 정보 추출 시도")
            
            except Exception as e:
                print(f"    ⚠️  버튼 클릭 실패: {e}")
            
            # VBA: Set 정보개체 = SEL.FindElementsByClass("_1kgEGGOBTi")
            # 팝업 창에서 정보 추출
            
            # 디버그: 페이지 소스 일부 출력
            try:
                page_source = self.driver.page_source
                if "상호명" in page_source:
                    print(f"    ✅ 페이지에 '상호명' 텍스트 존재 확인")
                    # 상호명 주변 HTML 추출
                    idx = page_source.find("상호명")
                    snippet = page_source[max(0, idx-200):min(len(page_source), idx+200)]
                    print(f"    📄 HTML 스니펫: {snippet[:100]}...")
                else:
                    print(f"    ⚠️  페이지에 '상호명' 텍스트가 없음")
            except Exception as e:
                print(f"    ⚠️  페이지 소스 확인 실패: {e}")
            
            info_elements = self.driver.find_elements(By.CLASS_NAME, "_1kgEGGOBTi")
            print(f"    📝 추출 가능한 정보 항목: {len(info_elements)}개")
            
            # 추출할 정보 초기화
            business_name = ""  # 상호명
            ceo_name = ""       # 대표자
            contact = ""        # 연락처
            business_number = "" # 사업자등록번호
            address = ""        # 사업장소재지
            ecommerce_number = "" # 통신판매업번호
            email = ""          # 이메일
            
            # VBA: For Each 개체 In 정보개체
            for i, element in enumerate(info_elements):
                try:
                    # VBA: Select Case 개체.FindElementsByClass("_2E256BP8nc")(1).Text
                    label_elem = element.find_elements(By.CLASS_NAME, "_2E256BP8nc")
                    value_elem = element.find_elements(By.CLASS_NAME, "_2PXb_kpdRh")
                    
                    if not label_elem or not value_elem:
                        continue
                    
                    label = label_elem[0].text.strip()
                    value = value_elem[0].text.strip()
                    
                    # 디버그: 추출된 정보 출력
                    print(f"      [{i+1}] {label}: {value[:30]}..." if len(value) > 30 else f"      [{i+1}] {label}: {value}")
                    
                    # VBA의 Select Case 로직
                    if label == "상호명":
                        business_name = value
                    elif label == "대표자":
                        # VBA: 대표자 = Split(대표자, ",")(0)
                        ceo_name = value.split(',')[0].split('(')[0].strip()
                    elif label == "고객센터":
                        # VBA: 연락처 = Replace(연락처, "인증", "")
                        contact = value.replace("인증", "").replace("잘못된 번호 신고", "").strip()
                    elif label == "사업자등록번호":
                        business_number = value
                    elif label == "사업장 소재지":
                        address = value
                    elif label == "통신판매업번호":
                        ecommerce_number = value
                    elif label == "e-mail":
                        email = value
                
                except Exception as e:
                    print(f"      ⚠️  [{i+1}] 추출 오류: {e}")
                    continue
            
            # 추출 결과 요약
            print(f"    ✅ 추출 완료: 상호명={business_name}, 대표자={ceo_name}, 연락처={contact}")
            
            # VBA 컬럼명으로 반환
            result = {
                '상호명': business_name,
                '대표자': ceo_name,
                '연락처': contact,
                '사업자등록번호': business_number,
                '사업장소재지': address,
                '통신판매업번호': ecommerce_number,
                '이메일': email,
            }
            
            # 팝업 창 닫고 원래 창으로 돌아가기
            try:
                all_windows = self.driver.window_handles
                if len(all_windows) > 1:
                    # 현재 팝업 창 닫기
                    self.driver.close()
                    # 원래 창으로 전환
                    self.driver.switch_to.window(original_window)
                    print(f"    🔙 원래 창으로 복귀")
            except:
                pass
            
            return result
        
        except Exception as e:
            print(f"    ⚠️  크롤링 실패: {e}")
            
            # 오류 발생 시에도 원래 창으로 복귀 시도
            try:
                all_windows = self.driver.window_handles
                if len(all_windows) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
            except:
                pass
            
            return {}
    
    def crawl_multiple_keywords(self, keywords, pages_per_keyword=5, domestic=True, extract_detailed=False):
        """
        여러 키워드 크롤링 (VBA 방식: 각 스토어 추출 후 즉시 상세 정보 추출)
        
        Args:
            keywords: 키워드 리스트
            pages_per_keyword: 키워드당 크롤링할 페이지 수
            domestic: True=국내, False=해외
            extract_detailed: True면 각 스토어의 상세 정보(사업자정보) 추출 (VBA: 스토어정보채워넣기)
        
        Returns:
            DataFrame: 크롤링 결과
        """
        all_data = []
        total = len(keywords) * pages_per_keyword
        current = 0
        
        # 이미 처리한 스토어 ID 추적 (VBA: 이미 불러온 스토어 체크)
        processed_stores = set()
        
        for keyword_idx, keyword in enumerate(keywords):
            if not keyword.strip():
                continue
                
            print(f"\n{'='*60}")
            print(f"📦 키워드: {keyword}")
            print(f"{'='*60}")
            
            for page in range(1, pages_per_keyword + 1):
                current += 1
                print(f"[{current}/{total}] 크롤링 중...")
                
                try:
                    # 각 키워드의 첫 페이지는 자연스러운 검색 사용
                    first_search = (page == 1)
                    
                    data = self.crawl_page(
                        keyword=keyword, 
                        page=page,
                        domestic=domestic,
                        first_search=first_search
                    )
                    
                    # VBA 방식: 각 스토어를 추출하자마자 상세 정보 추출
                    for item in data:
                        store_id = item['스토어아이디']
                        
                        # VBA: If 아이디딕.Exists(스토어아이디) = False Then
                        if store_id in processed_stores:
                            print(f"  ⏭️  이미 처리한 스토어: {store_id}")
                            continue
                        
                        # 키워드 정보 추가 (VBA 컬럼명)
                        item['키워드'] = keyword  # VBA: 키워드
                        item['페이지'] = page      # VBA: 페이지
                        
                        # VBA: Call 스토어정보채워넣기실무(list.ListRows.Count)
                        # VBA에서도 API(getDataDB)만 사용
                        if extract_detailed:
                            print(f"  🔍 {store_id} 상세 정보 추출 중...")
                            
                            # API로 상세 정보 조회 (VBA: Call getDataDB)
                            detailed_info = self._get_store_info_from_api(store_id)
                            if detailed_info and detailed_info.get('상호명'):
                                print(f"    ✅ API에서 조회 성공!")
                                item.update(detailed_info)
                            else:
                                print(f"    ⚠️  API에 정보 없음")
                            
                            # VBA: d.start 1000 * formSearch.inputDelay (지연시간)
                            time.sleep(random.uniform(1.0, 1.5))
                        
                        all_data.append(item)
                        processed_stores.add(store_id)
                    
                    print(f"  📊 누적: {len(all_data)}개 (중복 제외)")
                    
                except Exception as e:
                    print(f"  ❌ 오류: {e}")
                    continue
        
        # DataFrame 생성
        if all_data:
            df = pd.DataFrame(all_data)
            print(f"\n✅ 총 {len(df)}개 스토어 수집 완료!")
            return df
        else:
            return pd.DataFrame()
    
    def wait_for_login(self, timeout=300):
        """
        사용자가 수동으로 로그인할 때까지 대기
        VBA 원본처럼 자연스러운 방식
        
        Args:
            timeout: 최대 대기 시간 (초)
        
        Returns:
            bool: 로그인 성공 여부
        """
        print("\n" + "="*60)
        print("🔐 네이버 로그인")
        print("="*60)
        print("📌 브라우저에서 네이버 로그인을 완료해주세요.")
        print(f"⏱️  최대 {timeout}초 대기합니다...")
        print("="*60)
        
        # 1. 네이버 메인 페이지로 이동 (자연스럽게)
        print("\n🏠 네이버 메인 페이지로 이동...")
        self.driver.get("https://www.naver.com")
        self.chrome.human_delay(2, 3)  # 1~2초 → 2~3초 (페이지 로딩 대기)
        
        # 2. 로그인 버튼 찾아서 클릭
        try:
            print("🔍 로그인 버튼 찾는 중...")
            
            # 🆕 페이지 로딩 완료 대기
            time.sleep(1)
            
            # 로그인 버튼 선택자들
            login_selectors = [
                ".link_login",
                "a[href*='nid.naver.com']",
                ".area_links a.link_login"
            ]
            
            login_btn = None
            # 🆕 최대 5번 시도 (5초)
            for attempt in range(5):
                for selector in login_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            # 🆕 요소가 화면에 보이는지 확인
                            if elem.is_displayed():
                                text = elem.text.strip()
                                href = elem.get_attribute('href') or ''
                                if '로그인' in text or 'login' in href.lower():
                                    login_btn = elem
                                    break
                        if login_btn:
                            break
                    except:
                        continue
                
                if login_btn:
                    break
                    
                # 찾지 못하면 1초 대기 후 재시도
                if attempt < 4:
                    print(f"  ⏳ 로그인 버튼 찾는 중... (시도 {attempt + 1}/5)")
                    time.sleep(1)
            
            if login_btn:
                print("✅ 로그인 버튼 발견! 클릭...")
                
                # VBA처럼 단순 클릭
                try:
                    login_btn.click()
                    self.chrome.human_delay(2, 3)
                except Exception as e:
                    # 클릭 실패 시 직접 이동
                    print(f"⚠️  로그인 버튼 클릭 실패: {e}, 직접 이동...")
                    self.driver.get("https://nid.naver.com/nidlogin.login")
                    self.chrome.human_delay(2, 3)
            else:
                # 로그인 버튼 못 찾으면 직접 이동
                print("⚠️  로그인 버튼 못 찾음, 직접 이동...")
                self.driver.get("https://nid.naver.com/nidlogin.login")
                self.chrome.human_delay(1, 2)
        
        except Exception as e:
            print(f"⚠️  로그인 버튼 클릭 실패: {e}")
            self.driver.get("https://nid.naver.com/nidlogin.login")
            self.chrome.human_delay(1, 2)
        
        # 3. 로그인 완료 대기
        print("\n⏳ 로그인을 완료해주세요...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 로그인 완료 확인
            current_url = self.driver.current_url
            
            # nid.naver.com을 벗어났는지 확인
            if "nid.naver.com" not in current_url:
                # 🆕 로그인 버튼이 없으면 로그인 완료 (새로고침 제거!)
                try:
                    login_elements = self.driver.find_elements(By.CSS_SELECTOR, ".link_login")
                    if not login_elements:
                        print("\n✅ 로그인 완료!")
                        # 🆕 불필요한 메인 페이지 이동 제거
                        self.chrome.human_delay(1, 2)
                        return True
                except:
                    # 로그인 버튼 찾기 실패해도 nid 벗어났으면 성공
                    print("\n✅ 로그인 완료!")
                    self.chrome.human_delay(1, 2)
                    return True
            
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            print(f"\r⏳ 로그인 대기 중... ({elapsed}초 경과 / {remaining}초 남음)", end="", flush=True)
            
            time.sleep(2)
        
        print("\n❌ 로그인 시간 초과")
        return False

