"""
네이버 크롤링을 위한 메인 크롤러 클래스
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.remote.webelement import WebElement
import logging
import time
import random
import re
from pathlib import Path
from typing import Optional, Callable


class NaverCrawler:
    # 기본 설정 상수
    DEFAULT_TIMEOUT = 10
    SCROLL_CONFIG = {
        'min_offset': -500,
        'max_offset': -200,
        'min_step': 30,
        'max_step': 70,
        'base_pause': 0.05
    }
    
    def __init__(self, driver=None, url=None, config=None):
        """
        크롤러 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            url: 접속할 URL (선택사항, get_page()로 나중에 접속 가능)
            config: 설정 딕셔너리 (timeout, wait_time 등)
        """
        self.driver = driver
        self.url = url
        self.config = config or {}
        
        # config에서 timeout 가져오기 (없으면 기본값 사용)
        self.DEFAULT_TIMEOUT = self.config.get("timeout", 10)
        
        self._setup_logger()
        self.logger.info("NaverCrawler 초기화 완료")
        
    def _setup_logger(self):
        """로거 설정"""
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'crawler.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self):
        """
        크롬 드라이버 설정
        
        Note: 일반적으로 main.py에서 driver를 생성하여 전달하므로 이 메서드는 선택적입니다.
        """
        if self.driver is not None:
            self.logger.info("기존 드라이버 사용")
            return self.driver
        
        self.logger.warning("드라이버가 없습니다. chrome_driver.py를 사용하여 드라이버를 생성하세요.")
        return None
    
    def get_page(self, url, wait_time=None):
        """
        페이지 접속
        
        Args:
            url: 접속할 URL
            wait_time: 페이지 로드 대기 시간(초) - None이면 config의 wait_time 사용
        """
        try:
            self.driver.get(url)
            if wait_time is None:
                wait_time = self.config.get("wait_time", 3)
            time.sleep(wait_time)
            self.logger.info(f"페이지 접속 완료: {url}")
        except Exception as e:
            self.logger.error(f"페이지 접속 실패: {e}")
            raise
    
    def wait_for_element(self, by: By, value: str, timeout: int = None, 
                         condition: Callable = EC.presence_of_element_located) -> Optional[WebElement]:
        """
        특정 요소가 나타날 때까지 대기 (고급 버전)
        
        Args:
            by: 검색 방법 (By.ID, By.CLASS_NAME 등)
            value: 검색 값
            timeout: 최대 대기 시간(초) - None이면 DEFAULT_TIMEOUT 사용
            condition: 대기 조건 (기본값: presence_of_element_located)
        
        Returns:
            WebElement: 찾은 요소, 실패 시 None
        """
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT
            
        try:
            element = WebDriverWait(self.driver, timeout).until(condition((by, value)))
            self.logger.info(f"요소 대기 완료: {by}={value}")
            return element
        except TimeoutException:
            self.logger.error(f"요소 찾기 타임아웃: {by}={value}")
            return None
        except Exception as e:
            self.logger.error(f"요소 대기 중 예상치 못한 오류: {str(e)}")
            return None
    
    # ==================== Element 탐색 메서드 ====================
    
    def find_element(self, by, value):
        """
        단일 요소 찾기
        
        Args:
            by: 검색 방법 (By.ID, By.CLASS_NAME, By.CSS_SELECTOR 등)
            value: 검색 값
            
        Returns:
            WebElement: 찾은 요소
        """
        try:
            element = self.driver.find_element(by, value)
            self.logger.info(f"요소 찾기 성공: {by}={value}")
            return element
        except Exception as e:
            self.logger.error(f"요소 찾기 실패: {by}={value}, {e}")
            raise
    
    def find_elements(self, by, value):
        """
        여러 요소 찾기
        
        Args:
            by: 검색 방법 (By.ID, By.CLASS_NAME, By.CSS_SELECTOR 등)
            value: 검색 값
            
        Returns:
            list: 찾은 요소들의 리스트
        """
        try:
            elements = self.driver.find_elements(by, value)
            self.logger.info(f"요소 {len(elements)}개 찾기 성공: {by}={value}")
            return elements
        except Exception as e:
            self.logger.error(f"요소들 찾기 실패: {by}={value}, {e}")
            return []
    
    def wait_for_element_clickable(self, by, value, timeout=10):
        """
        요소가 클릭 가능할 때까지 대기
        
        Args:
            by: 검색 방법
            value: 검색 값
            timeout: 최대 대기 시간(초)
            
        Returns:
            WebElement: 클릭 가능한 요소
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            self.logger.info(f"클릭 가능한 요소 대기 완료: {by}={value}")
            return element
        except Exception as e:
            self.logger.error(f"클릭 가능한 요소 대기 실패: {by}={value}, {e}")
            raise
    
    def wait_for_elements(self, by, value, timeout=10, min_count=1):
        """
        여러 요소가 나타날 때까지 대기
        
        Args:
            by: 검색 방법
            value: 검색 값
            timeout: 최대 대기 시간(초)
            min_count: 최소 요소 개수
            
        Returns:
            list: 찾은 요소들의 리스트
        """
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
            if len(elements) >= min_count:
                self.logger.info(f"요소 {len(elements)}개 대기 완료: {by}={value}")
                return elements
            else:
                raise Exception(f"요소 개수 부족: {len(elements)} < {min_count}")
        except Exception as e:
            self.logger.error(f"요소들 대기 실패: {by}={value}, {e}")
            raise
    
    def is_element_present(self, by, value):
        """
        요소 존재 여부 확인 (대기 없음)
        
        Args:
            by: 검색 방법
            value: 검색 값
            
        Returns:
            bool: 요소 존재 여부
        """
        try:
            self.driver.find_element(by, value)
            return True
        except:
            return False
    
    # ==================== 터치 동작 메서드 ====================
    
    def touch_element(self, by, value, wait_time=0.5, max_attempts=3):
        """
        요소 터치 (모바일 클릭) - 재시도 및 랜덤성 추가
        
        Args:
            by: 검색 방법
            value: 검색 값
            wait_time: 터치 후 대기 시간(초)
            max_attempts: 최대 시도 횟수
        """
        for attempt in range(max_attempts):
            try:
                element = self.wait_for_element_clickable(by, value)
                if element:
                    # 모바일 터치 인터랙션 (랜덤 오프셋 포함)
                    action = ActionChains(self.driver)
                    offset_x = random.randint(-5, 5)
                    offset_y = random.randint(-5, 5)
                    
                    action.move_to_element_with_offset(element, offset_x, offset_y)
                    action.click()
                    action.perform()
                    
                    self.logger.info(f"요소 터치 완료: {by}={value}")
                    time.sleep(random.uniform(wait_time * 0.8, wait_time * 1.2))
                    return True
            except ElementClickInterceptedException:
                self.logger.warning(f"클릭 차단됨 (시도 {attempt + 1}/{max_attempts}), 구석 클릭 시도")
                self.random_corner_click()
                time.sleep(random.uniform(0.5, 1.0))
                if attempt < max_attempts - 1:
                    continue
            except Exception as e:
                self.logger.error(f"요소 터치 실패 (시도 {attempt + 1}/{max_attempts}): {by}={value}, {e}")
                if attempt < max_attempts - 1:
                    time.sleep(random.uniform(0.5, 1.0))
                    continue
        
        return False
    
    def touch_element_by_js(self, by, value, wait_time=0.5):
        """
        JavaScript를 사용한 요소 터치 (가려진 요소 클릭 가능)
        
        Args:
            by: 검색 방법
            value: 검색 값
            wait_time: 터치 후 대기 시간(초)
        """
        try:
            element = self.wait_for_element(by, value)
            self.driver.execute_script("arguments[0].click();", element)
            self.logger.info(f"요소 JS 터치 완료: {by}={value}")
            time.sleep(wait_time)
        except Exception as e:
            self.logger.error(f"요소 JS 터치 실패: {by}={value}, {e}")
            raise
    
    def touch_at_coordinates(self, x, y, wait_time=0.5):
        """
        특정 좌표 터치
        
        Args:
            x: X 좌표
            y: Y 좌표
            wait_time: 터치 후 대기 시간(초)
        """
        try:
            self.driver.execute_script(f"document.elementFromPoint({x}, {y}).click();")
            self.logger.info(f"좌표 터치 완료: ({x}, {y})")
            time.sleep(wait_time)
        except Exception as e:
            self.logger.error(f"좌표 터치 실패: ({x}, {y}), {e}")
            raise
    
    def double_touch(self, by, value, wait_time=0.5):
        """
        요소 더블 터치
        
        Args:
            by: 검색 방법
            value: 검색 값
            wait_time: 터치 후 대기 시간(초)
        """
        try:
            element = self.wait_for_element_clickable(by, value)
            element.click()
            time.sleep(0.2)
            element.click()
            self.logger.info(f"요소 더블 터치 완료: {by}={value}")
            time.sleep(wait_time)
        except Exception as e:
            self.logger.error(f"요소 더블 터치 실패: {by}={value}, {e}")
            raise
    
    def long_touch(self, by, value, duration=1.0):
        """
        요소 롱터치 (길게 누르기)
        
        Args:
            by: 검색 방법
            value: 검색 값
            duration: 누르고 있을 시간(초)
        """
        try:
            element = self.wait_for_element(by, value)
            
            actions = ActionChains(self.driver)
            actions.click_and_hold(element).perform()
            time.sleep(duration)
            actions.release(element).perform()
            
            self.logger.info(f"요소 롱터치 완료: {by}={value}")
        except Exception as e:
            self.logger.error(f"요소 롱터치 실패: {by}={value}, {e}")
            raise
    
    def random_corner_click(self):
        """화면 구석 무작위 클릭 (팝업 닫기 등에 유용)"""
        try:
            # 화면 크기 가져오기
            viewport_width = self.driver.execute_script("return window.innerWidth;")
            viewport_height = self.driver.execute_script("return window.innerHeight;")
            
            # 구석 영역 정의 (화면의 가장자리 20% 영역)
            edge_size = 0.2
            corners = [
                (0, edge_size, 0, edge_size),              # 좌상단
                (1 - edge_size, 1, 0, edge_size),          # 우상단
                (0, edge_size, 1 - edge_size, 1),          # 좌하단
                (1 - edge_size, 1, 1 - edge_size, 1)       # 우하단
            ]
            
            # 무작위 구석 선택
            x_min, x_max, y_min, y_max = random.choice(corners)
            
            # 선택된 구석 내에서 무작위 좌표 생성
            x = int(random.uniform(x_min * viewport_width, x_max * viewport_width))
            y = int(random.uniform(y_min * viewport_height, y_max * viewport_height))
            
            # 클릭 실행
            action = ActionChains(self.driver)
            action.move_by_offset(x, y)
            action.click()
            action.perform()
            action.move_by_offset(-x, -y)  # 마우스 위치 초기화
            
            self.logger.debug(f"무작위 구석 클릭: ({x}, {y})")
            time.sleep(random.uniform(0.3, 0.7))
            return True
            
        except Exception as e:
            self.logger.error(f"무작위 구석 클릭 실패: {str(e)}")
            return False
    
    def slow_typing(self, element: WebElement, text: str, min_delay: float = 0.1, max_delay: float = 0.5) -> bool:
        """
        사람처럼 천천히 텍스트 입력
        
        Args:
            element: 입력할 요소
            text: 입력할 텍스트
            min_delay: 최소 지연 시간(초)
            max_delay: 최대 지연 시간(초)
        
        Returns:
            bool: 성공 여부
        """
        try:
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(min_delay, max_delay))
            
            self.logger.info(f"텍스트 입력 완료: {text[:20]}...")

            element.send_keys(Keys.ENTER)
            time.sleep(random.uniform(0.5, 1.0))

            return True
        except Exception as e:
            self.logger.error(f"텍스트 입력 실패: {str(e)}")
            return False
    
    # ==================== 스크롤 동작 메서드 ====================
    
    def scroll_down(self, amount=500, wait_time=0.5):
        """
        페이지 아래로 스크롤
        
        Args:
            amount: 스크롤 양 (픽셀)
            wait_time: 스크롤 후 대기 시간(초)
        """
        try:
            self.driver.execute_script(f"window.scrollBy(0, {amount});")
            self.logger.info(f"아래로 스크롤: {amount}px")
            time.sleep(wait_time)
        except Exception as e:
            self.logger.error(f"스크롤 다운 실패: {e}")
            raise
    
    def scroll_up(self, amount=500, wait_time=0.5):
        """
        페이지 위로 스크롤
        
        Args:
            amount: 스크롤 양 (픽셀)
            wait_time: 스크롤 후 대기 시간(초)
        """
        try:
            self.driver.execute_script(f"window.scrollBy(0, -{amount});")
            self.logger.info(f"위로 스크롤: {amount}px")
            time.sleep(wait_time)
        except Exception as e:
            self.logger.error(f"스크롤 업 실패: {e}")
            raise
    
    def dynamic_scroll(self, target: Optional[WebElement] = None, distance: int = 200, 
                      pause: float = None, step: int = None, is_blog: bool = False) -> bool:
        """
        동적 스크롤 (사람처럼 자연스럽게)
        
        Args:
            target: 스크롤할 대상 요소 (None이면 픽셀 거리 사용)
            distance: 스크롤 거리 (픽셀)
            pause: 스크롤 간 대기 시간 (None이면 기본값 사용)
            step: 스크롤 스텝 크기 (None이면 랜덤)
            is_blog: 블로그 모드 (더 자연스러운 동작)
        
        Returns:
            bool: 성공 여부
        """
        try:
            if step is None:
                step = random.randint(self.SCROLL_CONFIG['min_step'], 
                                    self.SCROLL_CONFIG['max_step'])
            if pause is None:
                pause = self.SCROLL_CONFIG['base_pause']
            
            offset = random.randint(self.SCROLL_CONFIG['min_offset'], 
                                  self.SCROLL_CONFIG['max_offset'])
            
            # 현재 스크롤 위치 가져오기
            current_position = self.driver.execute_script("return window.pageYOffset;")
            
            # 목표 위치 계산
            if target:
                target_position = self.driver.execute_script(
                    "return arguments[0].getBoundingClientRect().top + window.pageYOffset;",
                    target
                )
            else:
                target_position = current_position + distance
            
            self.logger.debug(f"동적 스크롤 시작 - 현재: {current_position}, 목표: {target_position}")
            
            # 스크롤 방향 결정
            scrolling_down = target_position > current_position
            total_distance = abs(target_position - current_position)
            distance_scrolled = 0
            
            while (scrolling_down and current_position < target_position + offset) or \
                  (not scrolling_down and current_position > target_position + offset):
                
                # 남은 거리 계산
                remaining = abs(target_position + offset - current_position)
                scroll_step = min(step, remaining)
                
                if not scrolling_down:
                    scroll_step = -scroll_step
                
                # 스크롤 실행
                self.driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                
                # 위치 업데이트
                previous_position = current_position
                current_position = self.driver.execute_script("return window.pageYOffset;")
                
                # 진행률 계산
                distance_scrolled += abs(current_position - previous_position)
                progress = min(100, int((distance_scrolled / total_distance) * 100)) if total_distance > 0 else 100
                
                # 20%마다 로그
                if progress % 20 == 0:
                    self.logger.debug(
                        f"스크롤 {'다운' if scrolling_down else '업'} - 진행률: {progress}% - 위치: {current_position}")
                
                # 랜덤 지연
                time.sleep(pause * random.uniform(0.5, 1.5))
                
                # 멈춤 감지
                if abs(current_position - previous_position) == 0:
                    self.logger.debug("스크롤 중지 - 경계 도달")
                    break
            
            self.logger.info(f"동적 스크롤 완료 - 최종 위치: {current_position}")
            return True
            
        except Exception as e:
            self.logger.error(f"동적 스크롤 실패: {str(e)}")
            return False
    
    def scroll_to_top(self, wait_time=0.5):
        """
        페이지 최상단으로 스크롤
        
        Args:
            wait_time: 스크롤 후 대기 시간(초)
        """
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.logger.info("페이지 최상단으로 스크롤")
            time.sleep(wait_time)
        except Exception as e:
            self.logger.error(f"최상단 스크롤 실패: {e}")
            raise
    
    def scroll_to_bottom(self, wait_time=0.5):
        """
        페이지 최하단으로 스크롤
        
        Args:
            wait_time: 스크롤 후 대기 시간(초)
        """
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.logger.info("페이지 최하단으로 스크롤")
            time.sleep(wait_time)
        except Exception as e:
            self.logger.error(f"최하단 스크롤 실패: {e}")
            raise
    
    def scroll_to_element(self, by, value, wait_time=0.5):
        """
        특정 요소까지 스크롤
        
        Args:
            by: 검색 방법
            value: 검색 값
            wait_time: 스크롤 후 대기 시간(초)
        """
        try:
            element = self.wait_for_element(by, value)
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            self.logger.info(f"요소까지 스크롤 완료: {by}={value}")
            time.sleep(wait_time)
        except Exception as e:
            self.logger.error(f"요소까지 스크롤 실패: {by}={value}, {e}")
            raise
    
    def scroll_element(self, by, value, amount=300, wait_time=0.5):
        """
        특정 요소 내부 스크롤 (스크롤 가능한 div 등)
        
        Args:
            by: 검색 방법
            value: 검색 값
            amount: 스크롤 양 (픽셀)
            wait_time: 스크롤 후 대기 시간(초)
        """
        try:
            element = self.wait_for_element(by, value)
            self.driver.execute_script(f"arguments[0].scrollTop += {amount};", element)
            self.logger.info(f"요소 내부 스크롤: {by}={value}, {amount}px")
            time.sleep(wait_time)
        except Exception as e:
            self.logger.error(f"요소 내부 스크롤 실패: {by}={value}, {e}")
            raise
    
    def infinite_scroll(self, max_scrolls=10, scroll_pause=1.0):
        """
        무한 스크롤 페이지 로딩 (더 이상 새 콘텐츠가 없을 때까지)
        
        Args:
            max_scrolls: 최대 스크롤 횟수
            scroll_pause: 각 스크롤 후 대기 시간(초)
            
        Returns:
            int: 실제 수행한 스크롤 횟수
        """
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0
            
            for i in range(max_scrolls):
                # 최하단까지 스크롤
                self.scroll_to_bottom(wait_time=scroll_pause)
                scroll_count += 1
                
                # 새 높이 체크
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                # 더 이상 새 콘텐츠가 없으면 중단
                if new_height == last_height:
                    self.logger.info(f"무한 스크롤 완료: {scroll_count}회")
                    break
                
                last_height = new_height
                self.logger.info(f"무한 스크롤 진행 중: {i+1}/{max_scrolls}")
            
            return scroll_count
            
        except Exception as e:
            self.logger.error(f"무한 스크롤 실패: {e}")
            raise
    
    def get_scroll_position(self):
        """
        현재 스크롤 위치 가져오기
        
        Returns:
            dict: {'x': x좌표, 'y': y좌표}
        """
        try:
            x = self.driver.execute_script("return window.pageXOffset;")
            y = self.driver.execute_script("return window.pageYOffset;")
            return {'x': x, 'y': y}
        except Exception as e:
            self.logger.error(f"스크롤 위치 가져오기 실패: {e}")
            return {'x': 0, 'y': 0}
    
    def swipe(self, start_y: int, end_y: int, duration: float = 0.3) -> bool:
        """
        모바일 스와이프 동작 시뮬레이션
        
        Args:
            start_y: 시작 Y 좌표
            end_y: 종료 Y 좌표
            duration: 스와이프 지속 시간(초)
        
        Returns:
            bool: 성공 여부
        """
        try:
            swipe_script = """
                const start = new Touch({
                    identifier: Date.now(),
                    target: document.body,
                    clientY: arguments[0],
                    clientX: window.innerWidth / 2,
                    radiusX: 2.5,
                    radiusY: 2.5,
                    force: 0.5
                });
                
                const end = new Touch({
                    identifier: Date.now(),
                    target: document.body,
                    clientY: arguments[1],
                    clientX: window.innerWidth / 2,
                    radiusX: 2.5,
                    radiusY: 2.5,
                    force: 0.5
                });
                
                document.body.dispatchEvent(new TouchEvent('touchstart', {
                    bubbles: true,
                    touches: [start],
                    targetTouches: [start],
                    changedTouches: [start]
                }));
                
                setTimeout(() => {
                    document.body.dispatchEvent(new TouchEvent('touchend', {
                        bubbles: true,
                        touches: [],
                        targetTouches: [],
                        changedTouches: [end]
                    }));
                }, arguments[2]);
            """
            
            self.driver.execute_script(swipe_script, start_y, end_y, int(duration * 1000))
            time.sleep(duration + random.uniform(0.1, 0.3))
            self.logger.info(f"스와이프 완료: {start_y} -> {end_y}")
            return True
            
        except Exception as e:
            self.logger.error(f"스와이프 실패: {str(e)}")
            return False
    
    def scroll_to_feed_section(self, direction: str = "down", scroll_amount: int = 1000) -> bool:
        """
        피드 섹션 스크롤 (진행률 추적)
        
        Args:
            direction: 방향 ("up" 또는 "down")
            scroll_amount: 스크롤 양 (픽셀)
        
        Returns:
            bool: 성공 여부
        """
        try:
            if direction.lower() == "up":
                return self.dynamic_scroll(distance=-scroll_amount)
            else:
                return self.dynamic_scroll(distance=scroll_amount)
        except Exception as e:
            self.logger.error(f"피드 섹션 스크롤 실패: {str(e)}")
            return False
    
    def smooth_scroll_by(self, total_scroll_distance: int, duration: float = None) -> bool:
        """
        부드러운 스크롤 (easing 적용)
        
        Args:
            total_scroll_distance: 총 스크롤 거리 (픽셀)
            duration: 지속 시간(초) - None이면 자동 계산
        
        Returns:
            bool: 성공 여부
        """
        try:
            if duration is None:
                duration = abs(total_scroll_distance) / 300
                duration = min(max(duration, 0.5), 2.0)
            
            steps = int(duration * 60)  # 60fps
            interval = duration / steps
            current_scroll = 0
            
            for i in range(steps):
                progress = i / steps
                
                # Ease-in-out 함수
                if progress < 0.5:
                    ease = 2 * progress * progress
                else:
                    progress = 2 * progress - 1
                    ease = -0.5 * (progress * (progress - 2) - 1)
                
                target_scroll = total_scroll_distance * ease
                scroll_this_step = target_scroll - current_scroll
                
                self.driver.execute_script(f"window.scrollBy(0, {scroll_this_step});")
                current_scroll = target_scroll
                time.sleep(interval)
            
            self.logger.info(f"부드러운 스크롤 완료: {total_scroll_distance}px")
            return True
            
        except Exception as e:
            self.logger.error(f"부드러운 스크롤 실패: {str(e)}")
            return False
    
    def simulate_natural_reading(self, min_read_time: float = 25, max_read_time: float = 50) -> bool:
        """
        자연스러운 읽기 시뮬레이션 (모바일 환경)
        랜덤한 스크롤 다운/업, 일시 정지 등을 조합
        
        Args:
            min_read_time: 최소 읽기 시간(초)
            max_read_time: 최대 읽기 시간(초)
        
        Returns:
            bool: 성공 여부
        """
        try:
            total_read_time = random.uniform(min_read_time, max_read_time)
            start_time = time.time()
            
            self.logger.info(f"자연스러운 읽기 시작: {total_read_time:.1f}초")
            
            while (time.time() - start_time) < total_read_time:
                # 랜덤 동작 선택
                action = random.choice(['scroll_down', 'scroll_up', 'pause'])
                
                if action == 'scroll_down':
                    scroll_amount = random.randint(300, 600)
                    self.smooth_scroll_by(scroll_amount)
                    time.sleep(random.uniform(0.5, 1))
                    
                elif action == 'scroll_up':
                    if random.random() < 0.2:  # 20% 확률로 위로 스크롤
                        scroll_amount = random.randint(-200, -100)
                        self.smooth_scroll_by(scroll_amount)
                        time.sleep(random.uniform(0.5, 1))
                        
                else:  # pause
                    time.sleep(random.uniform(3, 5))
                
                # 현재 위치 체크
                current_pos = self.driver.execute_script("return window.pageYOffset;")
                total_height = self.driver.execute_script("return document.documentElement.scrollHeight;")
                viewport_height = self.driver.execute_script("return window.innerHeight;")
                
                # 최하단 도달 시 위로
                if current_pos + viewport_height >= total_height:
                    self.smooth_scroll_by(-current_pos, duration=2.0)
                    time.sleep(random.uniform(1, 2))
                    
                # 최상단 도달 시 아래로
                elif current_pos <= 0:
                    self.smooth_scroll_by(random.randint(200, 400))
                    time.sleep(random.uniform(1, 2))
            
            self.logger.info("자연스러운 읽기 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"자연스러운 읽기 시뮬레이션 실패: {str(e)}")
            return False
    
    # ==================== 유틸리티 메서드 ====================
    
    def extract_cid(self, url: str) -> Optional[str]:
        """
        URL에서 CID (Content ID) 추출
        
        Args:
            url: CID를 추출할 URL
        
        Returns:
            str: 추출된 CID, 없으면 None
        """
        patterns = [
            r'/(\d+)[/?=]',
            r'/(\d+)',
            r'/(\d+)(?:[/?=]|$)'
        ]
        
        try:
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    cid = match.group(1)
                    self.logger.debug(f"CID 추출 성공: {cid}")
                    return cid
            
            self.logger.warning(f"CID 추출 실패: {url}")
            return None
            
        except Exception as e:
            self.logger.error(f"CID 추출 중 오류: {str(e)}")
            return None
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            self.logger.info("드라이버 종료")
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()

