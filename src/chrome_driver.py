"""
Chrome 디버깅 모드 드라이버 (VBA 원본 방식)
"""
import os
import time
import logging
import subprocess
import platform
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pathlib import Path

logger = logging.getLogger(__name__)


class ChromeDriver:
    """Chrome 디버깅 모드 드라이버 (VBA 원본 방식)"""
    
    def __init__(self, driver_path=None, headless: bool = False, 
                 use_debug_mode: bool = True, debug_port: int = 9222, 
                 profile_path: str = None):
        """
        초기화
        
        Args:
            driver_path: ChromeDriver 경로 (None이면 자동 탐색)
            headless: 헤드리스 모드 여부
            use_debug_mode: 디버깅 모드 사용 여부 (VBA 원본 방식, 권장)
            debug_port: 디버깅 포트 번호 (기본 9222)
            profile_path: Chrome 프로필 경로 (None이면 ~/ChromeTEMP 사용)
        """
        self.driver_path = driver_path or self._find_chromedriver()
        self.headless = headless
        self.use_debug_mode = use_debug_mode
        self.debug_port = debug_port
        self.profile_path = profile_path or os.path.expanduser("~/ChromeTEMP")
        self.chrome_pid = None
        
        logger.info(f"ChromeDriver 초기화: headless={headless}, debug_mode={use_debug_mode}")
        if use_debug_mode:
            logger.info(f"프로필 경로: {self.profile_path}")
    
    def _find_chrome_path(self) -> Optional[str]:
        """Chrome 실행 파일 경로 찾기"""
        system = platform.system()
        
        if system == "Windows":
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]
        elif system == "Darwin":  # macOS
            possible_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ]
        else:  # Linux
            possible_paths = [
                "/usr/bin/google-chrome",
                "/usr/local/bin/google-chrome",
                "/usr/bin/chromium-browser",
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Chrome 실행 파일 발견: {path}")
                return path
        
        logger.error("Chrome 실행 파일을 찾을 수 없습니다.")
        return None
    
    def _find_chromedriver(self) -> str:
        """ChromeDriver 경로 자동 탐색"""
        # 프로젝트 내 drivers 폴더 확인
        project_root = Path(__file__).parent.parent
        driver_path = project_root / "drivers" / "chromedriver.exe"
        
        if driver_path.exists():
            logger.info(f"ChromeDriver 발견: {driver_path}")
            return str(driver_path)
        
        # 환경변수 확인
        env_path = os.getenv("CHROME_DRIVER_PATH")
        if env_path and Path(env_path).exists():
            return env_path
        
        logger.warning("ChromeDriver 경로를 찾을 수 없습니다. 시스템 PATH를 사용합니다.")
        return "chromedriver"
    
    def start_chrome_debug_mode(self) -> Optional[int]:
        """
        Chrome을 디버깅 모드로 시작 (VBA 원본 방식)
        
        Returns:
            Chrome 프로세스 PID, 실패 시 None
        """
        try:
            chrome_path = self._find_chrome_path()
            if not chrome_path:
                logger.error("Chrome 실행 파일을 찾을 수 없습니다.")
                return None
            
            # 프로필 디렉토리 생성
            os.makedirs(self.profile_path, exist_ok=True)
            logger.info(f"프로필 디렉토리 준비: {self.profile_path}")
            
            # Chrome 디버깅 모드 명령어
            cmd = [
                chrome_path,
                f"--remote-debugging-port={self.debug_port}",
                f"--user-data-dir={self.profile_path}",
                "--disable-sync",                      # 동기화 비활성화
                "--no-first-run",                      # 첫 실행 페이지 스킵
                "--no-default-browser-check",          # 기본 브라우저 확인 스킵
            ]
            
            logger.info(f"Chrome 디버깅 모드 시작: 포트 {self.debug_port}")
            
            # 백그라운드로 프로세스 시작
            if platform.system() == "Windows":
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            self.chrome_pid = process.pid
            logger.info(f"Chrome 프로세스 시작 완료: PID={self.chrome_pid}")
            
            # Chrome이 준비될 때까지 대기
            time.sleep(3)
            
            return self.chrome_pid
            
        except Exception as e:
            logger.error(f"Chrome 디버깅 모드 시작 실패: {e}")
            return None
    
    def create_driver(self) -> webdriver.Chrome:
        """Chrome 드라이버 생성"""
        try:
            # 디버깅 모드 사용 시 Chrome 먼저 시작
            if self.use_debug_mode:
                logger.info("🔧 디버깅 모드로 Chrome 시작 (VBA 원본 방식)")
                pid = self.start_chrome_debug_mode()
                if not pid:
                    logger.error("디버깅 모드 시작 실패, 일반 모드로 전환")
                    self.use_debug_mode = False
            
            # Chrome 옵션 생성
            options = self._create_chrome_options()
            
            # 드라이버 생성
            if self.use_debug_mode:
                # 디버깅 포트에 연결
                logger.info(f"디버깅 포트 {self.debug_port}에 연결 중...")
                driver = webdriver.Chrome(options=options)
            else:
                # 일반 모드
                service = Service(self.driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            
            logger.info("✅ 드라이버 생성 완료")
            
            return driver
            
        except Exception as e:
            logger.error(f"드라이버 생성 실패: {e}")
            raise
    
    def _create_chrome_options(self) -> Options:
        """Chrome 옵션 설정"""
        options = Options()
        
        # 디버깅 모드 사용 시
        if self.use_debug_mode:
            logger.info(f"디버깅 포트 연결: localhost:{self.debug_port}")
            options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")
            return options
        
        # 일반 모드 설정
        if self.headless:
            logger.info("Headless 모드 활성화")
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
        
        # 자동화 감지 방지
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # 기본 설정
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        
        return options
    
    def human_delay(self, min_seconds: float = 1.0, max_seconds: float = 2.0) -> None:
        """
        사람처럼 자연스러운 랜덤 대기
        
        Args:
            min_seconds: 최소 대기 시간 (초)
            max_seconds: 최대 대기 시간 (초)
        """
        import random
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def quit_driver(self, driver: webdriver.Chrome, kill_chrome: bool = False) -> None:
        """
        드라이버 종료
        
        Args:
            driver: Selenium 드라이버 인스턴스
            kill_chrome: Chrome 프로세스도 강제 종료할지 여부 (디버깅 모드 전용)
        """
        try:
            if driver:
                driver.quit()
                logger.info("드라이버 종료 완료")
            
            # 디버깅 모드에서 Chrome 프로세스도 종료
            if kill_chrome and self.chrome_pid:
                self.kill_chrome_process()
                
        except Exception as e:
            logger.error(f"드라이버 종료 실패: {e}")
    
    def kill_chrome_process(self) -> None:
        """Chrome 프로세스 강제 종료"""
        try:
            if not self.chrome_pid:
                logger.warning("종료할 Chrome PID가 없습니다.")
                return
            
            logger.info(f"Chrome 프로세스 종료 중: PID={self.chrome_pid}")
            
            if platform.system() == "Windows":
                # 특정 PID 종료
                subprocess.run(["taskkill", "/F", "/PID", str(self.chrome_pid)], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # 디버깅 포트를 사용하는 모든 Chrome 프로세스 종료 (안전장치)
                time.sleep(0.5)
                subprocess.run(
                    ["powershell", "-Command", 
                     f"Get-Process chrome -ErrorAction SilentlyContinue | Where-Object {{$_.CommandLine -like '*{self.debug_port}*'}} | Stop-Process -Force"],
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
            else:
                subprocess.run(["kill", "-9", str(self.chrome_pid)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.chrome_pid = None
            logger.info("Chrome 프로세스 종료 완료")
            
            # 프로세스가 완전히 종료될 시간 확보
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"Chrome 프로세스 종료 실패: {e}")


def test_chrome_driver():
    """테스트 함수"""
    import time
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 디버깅 모드로 테스트
    chrome = ChromeDriver(headless=False, use_debug_mode=True)
    driver = chrome.create_driver()
    
    try:
        # 테스트 페이지 방문
        print("\n네이버 접속 중...")
        driver.get("https://www.naver.com")
        time.sleep(3)
        
        print("\n5초 후 종료합니다...")
        time.sleep(5)
        
    finally:
        chrome.quit_driver(driver, kill_chrome=True)


if __name__ == "__main__":
    test_chrome_driver()

