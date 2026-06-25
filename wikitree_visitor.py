"""
Wikitree Visitor - 위키트리 기사 자연 방문기
위키트리 메인 → 랜덤 기사 클릭 → 자연스러운 스크롤 → 체류
"""

import time
import random
import logging
import gc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from simple_visitor import NordVPNCLI, NordVPNRotator

logger = logging.getLogger(__name__)


class WikitreeVisitor:
    """위키트리 기사 자연 방문기"""

    MAIN_URL = "https://www.wikitree.co.kr/"

    ARTICLE_CSS_SELECTORS = [
        "a[href*='/articles/']",
        "a[href*='/news/']",
    ]

    def __init__(self, headless=False, use_nordvpn=False,
                 nordvpn_username=None, nordvpn_password=None,
                 target_countries=None, guest_mode=True, use_cli=True):
        self.headless = headless
        self.use_nordvpn = use_nordvpn
        self.use_cli = use_cli
        self.nordvpn = None
        self.nordvpn_cli = None
        self.driver = None
        self.guest_mode = guest_mode

        if use_nordvpn:
            if use_cli:
                target_country = target_countries[0] if target_countries else "KR"
                self.nordvpn_cli = NordVPNCLI(target_country)
                logger.info("[VPN] NordVPN CLI 모드")
            else:
                self.nordvpn = NordVPNRotator(nordvpn_username, nordvpn_password)
                self.nordvpn.fetch_nordvpn_servers(
                    limit=100, use_http=True, target_countries=target_countries
                )
                logger.info("[VPN] NordVPN 프록시 모드")

    def create_driver(self, proxy_server=None):
        """Chrome 드라이버 생성"""
        try:
            options = Options()

            if self.headless:
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")

            if self.guest_mode:
                options.add_argument("--guest")

            if proxy_server and self.nordvpn:
                host = proxy_server['host']
                port = proxy_server['port']
                proto = proxy_server.get('protocol', 'socks5')
                username = self.nordvpn.username
                password = self.nordvpn.password

                if username and password:
                    options.add_argument(
                        f'--proxy-server={proto}://{username}:{password}@{host}:{port}'
                    )
                else:
                    options.add_argument(f'--proxy-server={proto}://{host}:{port}')

            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            ]
            options.add_argument(f"--user-agent={random.choice(user_agents)}")

            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            logger.info("[OK] 드라이버 생성 완료")
            return self.driver
        except Exception as e:
            logger.error(f"[ERROR] 드라이버 생성 실패: {e}")
            raise

    # ------------------------------------------------------------------
    # 핵심 로직
    # ------------------------------------------------------------------

    def _collect_article_links(self):
        """메인 페이지에서 기사 링크 수집"""
        links = set()
        for selector in self.ARTICLE_CSS_SELECTORS:
            try:
                elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elems:
                    href = el.get_attribute("href")
                    if href and "wikitree.co.kr" in href:
                        links.add(href)
            except Exception:
                continue

        # fallback: <a> 태그 전체에서 기사 패턴 추출
        if len(links) < 3:
            all_a = self.driver.find_elements(By.TAG_NAME, "a")
            for a in all_a:
                try:
                    href = a.get_attribute("href")
                    if not href:
                        continue
                    if "wikitree.co.kr" in href and any(
                        p in href for p in ["/articles/", "/news/", "articleView"]
                    ):
                        links.add(href)
                except Exception:
                    continue

        logger.info(f"[FIND] 기사 링크 {len(links)}개 수집")
        return list(links)

    def _smooth_scroll_to_bottom(self, pause_min=0.8, pause_max=2.5,
                                  scroll_step_min=200, scroll_step_max=500,
                                  max_scroll_time=60):
        """자연스럽게 페이지 끝까지 스크롤 (최대 시간 제한)"""
        try:
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            current = self.driver.execute_script("return window.pageYOffset")
            viewport = self.driver.execute_script("return window.innerHeight")
            start_time = time.time()

            logger.info(f"[SCROLL] 페이지 높이: {total_height}px, 최대 {max_scroll_time}초")

            while current + viewport < total_height:
                elapsed = time.time() - start_time
                if elapsed >= max_scroll_time:
                    logger.info(f"[SCROLL] 최대 시간 도달 ({max_scroll_time}초), 스크롤 중단")
                    break

                step = random.randint(scroll_step_min, scroll_step_max)
                target = min(current + step, total_height - viewport)

                self.driver.execute_script(
                    "window.scrollTo({top: arguments[0], behavior: 'smooth'});",
                    target,
                )
                pause = random.uniform(pause_min, pause_max)
                time.sleep(pause)

                if random.random() < 0.25:
                    extra = random.uniform(1.0, 3.0)
                    time.sleep(extra)

                current = self.driver.execute_script("return window.pageYOffset")
                total_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )

            else:
                logger.info("[SCROLL] 페이지 끝까지 스크롤 완료")

            elapsed = time.time() - start_time
            logger.info(f"[SCROLL] 스크롤 소요 시간: {elapsed:.1f}초")
        except Exception as e:
            logger.warning(f"[WARNING] 스크롤 중 오류: {e}")

    def visit_random_article(self, dwell_min=10, dwell_max=30, max_scroll_time=60):
        """메인 접속 → 랜덤 기사 클릭 → 스크롤 → 체류"""
        try:
            # 1) 위키트리 메인
            logger.info(f"[VISIT] 위키트리 메인 접속: {self.MAIN_URL}")
            self.driver.get(self.MAIN_URL)
            time.sleep(random.uniform(2.0, 4.0))

            # 2) 기사 링크 수집
            articles = self._collect_article_links()
            if not articles:
                logger.warning("[FAIL] 기사 링크를 찾지 못했습니다.")
                return False

            chosen = random.choice(articles)
            logger.info(f"[CLICK] 랜덤 기사 선택: {chosen}")

            # 3) 기사 접속
            self.driver.get(chosen)
            time.sleep(random.uniform(2.0, 4.0))

            page_title = self.driver.title
            logger.info(f"[ARTICLE] 제목: {page_title}")

            # 4) 자연스러운 스크롤 (최대 시간 제한)
            self._smooth_scroll_to_bottom(max_scroll_time=max_scroll_time)

            # 5) 하단 체류
            dwell = random.uniform(dwell_min, dwell_max)
            logger.info(f"[DWELL] {dwell:.1f}초 체류 중...")
            time.sleep(dwell)

            logger.info("[OK] 기사 방문 완료")
            return True

        except Exception as e:
            logger.error(f"[ERROR] 기사 방문 실패: {e}")
            return False

    # ------------------------------------------------------------------
    # 실행 / 종료
    # ------------------------------------------------------------------

    def close(self):
        """드라이버 종료 및 메모리 정리"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("[OK] 드라이버 종료")
            except Exception as e:
                logger.warning(f"[WARNING] 드라이버 종료 중 오류: {e}")
            finally:
                self.driver = None
        gc.collect()

    def run(self, repeat_count=10, dwell_min=10, dwell_max=30,
            max_scroll_time=60, rest_minutes=0):
        """
        반복 실행

        Args:
            repeat_count: 반복 횟수
            dwell_min: 기사 페이지 최소 체류 시간 (초)
            dwell_max: 기사 페이지 최대 체류 시간 (초)
            max_scroll_time: 스크롤 최대 시간 (초)
            rest_minutes: 사이클 간 휴식 (분)
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"[START] 위키트리 방문 시작")
        logger.info(f"{'='*70}")
        logger.info(f"  - 반복 횟수: {repeat_count}")
        logger.info(f"  - 체류 시간: {dwell_min}~{dwell_max}초")
        logger.info(f"  - 스크롤 최대: {max_scroll_time}초")
        logger.info(f"  - 휴식 시간: {rest_minutes}분")
        logger.info(f"  - 게스트 모드: {'사용' if self.guest_mode else '미사용'}")
        logger.info(f"  - NordVPN: {'사용' if self.use_nordvpn else '사용 안 함'}")
        logger.info(f"{'='*70}\n")

        success_count = 0
        fail_count = 0

        for i in range(1, repeat_count + 1):
            logger.info(f"\n{'='*70}")
            logger.info(f"[CYCLE] {i}/{repeat_count}")
            logger.info(f"{'='*70}")

            try:
                proxy_server = None
                if self.use_nordvpn:
                    if self.use_cli and self.nordvpn_cli:
                        self.nordvpn_cli.connect()
                    elif self.nordvpn:
                        proxy_server = self.nordvpn.get_random_server()
                        if proxy_server:
                            logger.info(f"[VPN] 서버 변경: {proxy_server['country']}")

                self.create_driver(proxy_server if not self.use_cli else None)

                if self.visit_random_article(dwell_min, dwell_max, max_scroll_time):
                    success_count += 1
                else:
                    fail_count += 1

            except Exception as e:
                logger.error(f"[ERROR] 사이클 {i} 실패: {e}")
                fail_count += 1

            finally:
                self.close()

                if i % 10 == 0:
                    logger.info(f"[MEMORY] 주기적 메모리 정리 ({i}/{repeat_count})")
                    gc.collect()
                    time.sleep(1)

                if i < repeat_count and rest_minutes > 0:
                    rest_sec = int(rest_minutes * 60)
                    logger.info(f"\n[REST] {rest_minutes}분 휴식 중...")
                    time.sleep(rest_sec)

        logger.info(f"\n{'='*70}")
        logger.info(f"[DONE] 완료!")
        logger.info(f"{'='*70}")
        logger.info(f"  - 성공: {success_count}")
        logger.info(f"  - 실패: {fail_count}")
        if repeat_count > 0:
            logger.info(f"  - 성공률: {success_count / repeat_count * 100:.1f}%")
        logger.info(f"{'='*70}")

        gc.collect()

        if self.use_nordvpn and self.use_cli and self.nordvpn_cli:
            self.nordvpn_cli.disconnect()

        logger.info("[OK] 모든 작업 완료")
