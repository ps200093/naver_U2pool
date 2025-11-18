"""
모바일 에뮬레이션을 위한 Selenium 드라이버
완벽한 모바일 위장을 위한 모든 설정 포함
VBA 원본의 디버깅 모드 방식 지원
"""
import re
import os
import sys
import time
import logging
import subprocess
import platform
from typing import Optional, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pathlib import Path

logger = logging.getLogger(__name__)


class MobileDriver:
    """모바일 환경을 완벽하게 에뮬레이션하는 드라이버"""
    
    # 인기 있는 모바일 기기 프리셋
    DEVICES = {
        "galaxy_s24": {
            "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-S928N Build/UP1A.231005.007) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.109 Mobile Safari/537.36",
            "width": 412,
            "height": 915,
            "pixel_ratio": 3.5,
            "platform_version": "14",
            "architecture": "arm",
            "device_model": "SM-S928N"
        },
        "galaxy_s23": {
            "user_agent": "Mozilla/5.0 (Linux; Android 13; SM-S911N Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.109 Mobile Safari/537.36",
            "width": 360,
            "height": 800,
            "pixel_ratio": 3.0,
            "platform_version": "13",
            "architecture": "arm",
            "device_model": "SM-S911N"
        },
        "iphone_15_pro": {
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.6778.109 Mobile/15E148 Safari/604.1",
            "width": 393,
            "height": 852,
            "pixel_ratio": 3.0,
            "platform_version": "17.0",
            "architecture": "arm64",
            "device_model": "iPhone15,3"
        },
        "iphone_14": {
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.6778.109 Mobile/15E148 Safari/604.1",
            "width": 390,
            "height": 844,
            "pixel_ratio": 3.0,
            "platform_version": "16.0",
            "architecture": "arm64",
            "device_model": "iPhone14,7"
        }
    }
    
    def __init__(self, driver_path=None, headless: bool = True, device: str = "galaxy_s24", 
                 use_debug_mode: bool = True, debug_port: int = 9222, profile_path: str = None):
        """
        초기화
        
        Args:
            driver_path: ChromeDriver 경로 (None이면 자동 탐색)
            headless: 헤드리스 모드 여부
            device: 사용할 기기 프리셋 (galaxy_s24, galaxy_s23, iphone_15_pro, iphone_14)
            use_debug_mode: 디버깅 모드 사용 여부 (VBA 원본 방식, 권장)
            debug_port: 디버깅 포트 번호 (기본 9222)
            profile_path: Chrome 프로필 경로 (None이면 ~/ChromeTEMP 사용)
        """
        self.driver_path = driver_path or self._find_chromedriver()
        self.headless = headless
        self.device_info = self.DEVICES.get(device, self.DEVICES["galaxy_s24"])
        self.use_debug_mode = use_debug_mode
        self.debug_port = debug_port
        self.profile_path = profile_path or os.path.expanduser("~/ChromeTEMP")
        self.chrome_pid = None
        self.chrome_version = self._get_chrome_version()
        
        logger.info(f"MobileDriver 초기화: device={device}, headless={headless}, debug_mode={use_debug_mode}")
        logger.info(f"Chrome 버전: {self.chrome_version['full']}")
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
    
    def _get_chrome_version(self) -> dict:
        """Chrome 버전 감지"""
        try:
            # 임시로 드라이버 생성하여 버전 확인
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            
            service = Service(self.driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            user_agent = driver.execute_script("return navigator.userAgent")
            driver.quit()
            
            # User Agent에서 Chrome 버전 추출
            version_match = re.search(r'Chrome/(\d+)\.(\d+)\.(\d+)\.(\d+)', user_agent)
            if version_match:
                major, minor, build, patch = version_match.groups()
                return {
                    "major": major,
                    "full": f"{major}.{minor}.{build}.{patch}",
                    "major_minor": f"{major}.{minor}",
                }
        except Exception as e:
            logger.warning(f"Chrome 버전 감지 실패: {e}")
        
        # 기본값 반환
        return {
            "major": "131",
            "full": "131.0.6778.109",
            "major_minor": "131.0",
        }
    
    def _update_user_agent_with_chrome_version(self) -> None:
        """User Agent의 Chrome 버전을 실제 버전으로 업데이트"""
        user_agent = self.device_info["user_agent"]
        updated_user_agent = re.sub(
            r'Chrome/\d+\.\d+\.\d+\.\d+',
            f'Chrome/{self.chrome_version["full"]}',
            user_agent
        )
        self.device_info["user_agent"] = updated_user_agent
    
    def create_driver(self) -> webdriver.Chrome:
        """모바일 에뮬레이션이 적용된 Chrome 드라이버 생성"""
        try:
            # User Agent 업데이트
            self._update_user_agent_with_chrome_version()
            
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
            
            # CDP(Chrome DevTools Protocol)를 통한 추가 설정
            self._apply_mobile_settings(driver)
            
            # JavaScript를 통한 최종 위장
            self._inject_mobile_javascript(driver)
            
            # 설정 검증
            self._verify_mobile_settings(driver)
            
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
            # 디버깅 모드에서는 대부분의 옵션이 불필요 (이미 Chrome이 실행 중)
            return options
        
        # 일반 모드 설정
        # Headless 모드 설정
        if self.headless:
            logger.info("Headless 모드 활성화")
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            
            # Headless 감지 방지
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--enable-features=NetworkService")
            options.add_argument("--disable-features=VizDisplayCompositor")
        else:
            options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 자동화 감지 방지
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # 기본 보안 설정
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        
        # 모바일 헤더 설정
        options.add_argument('sec-ch-ua-mobile=?1')
        
        # 디바이스가 안드로이드인지 iOS인지 확인
        is_android = "Android" in self.device_info["user_agent"]
        platform = "Android" if is_android else "iOS"
        options.add_argument(f'sec-ch-ua-platform="{platform}"')
        
        # WebRTC IP 유출 방지
        options.add_argument('--disable-webrtc')
        options.add_argument('--disable-rtc-smoothness-algorithm')
        
        # 모바일 에뮬레이션 설정
        mobile_emulation = {
            'deviceMetrics': {
                'width': self.device_info['width'],
                'height': self.device_info['height'],
                'pixelRatio': self.device_info['pixel_ratio'],
                'touch': True,
                'mobile': True
            },
            'userAgent': self.device_info['user_agent']
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # 터치 이벤트 활성화
        options.add_argument('--enable-touch-events')
        options.add_argument('--touch-events=enabled')
        
        # Preferences 설정
        prefs = {
            # 알림 차단
            'profile.default_content_setting_values.notifications': 2,
            # 팝업 허용
            'profile.default_content_settings.popups': 0,
            # 지리적 위치 차단 (선택사항)
            'profile.default_content_setting_values.geolocation': 2,
            # WebRTC IP 유출 방지
            'webrtc.ip_handling_policy': 'disable_non_proxied_udp',
            'webrtc.multiple_routes_enabled': False,
            'webrtc.nonproxied_udp_enabled': False,
        }
        options.add_experimental_option('prefs', prefs)
        
        return options
    
    def _apply_mobile_settings(self, driver: webdriver.Chrome) -> None:
        """CDP를 통한 모바일 설정 적용"""
        is_android = "Android" in self.device_info["user_agent"]
        platform = "Android" if is_android else "iOS"
        
        # 1. Navigator 오버라이드
        driver.execute_cdp_cmd('Emulation.setNavigatorOverrides', {
            'platform': platform,
            'userAgent': self.device_info["user_agent"],
            'acceptLanguage': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        })
        
        # 2. 터치 에뮬레이션 활성화
        driver.execute_cdp_cmd('Emulation.setTouchEmulationEnabled', {
            'enabled': True,
            'maxTouchPoints': 5,
            'configuration': 'mobile'
        })
        
        # 3. 디바이스 메트릭 설정
        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            'mobile': True,
            'width': self.device_info["width"],
            'height': self.device_info["height"],
            'deviceScaleFactor': self.device_info["pixel_ratio"],
            'screenOrientation': {
                'angle': 0,
                'type': 'portraitPrimary'
            }
        })
        
        # 4. User Agent 메타데이터 설정
        driver.execute_cdp_cmd('Network.enable', {})
        
        user_agent_metadata = {
            "userAgent": self.device_info["user_agent"],
            "platform": platform,
            "acceptLanguage": "ko-KR,ko;q=0.9",
            "userAgentMetadata": {
                "brands": [
                    {"brand": "Google Chrome", "version": self.chrome_version["major"]},
                    {"brand": "Chromium", "version": self.chrome_version["major"]},
                    {"brand": "Not=A?Brand", "version": "24"}
                ],
                "fullVersionList": [
                    {"brand": "Google Chrome", "version": self.chrome_version["full"]},
                    {"brand": "Chromium", "version": self.chrome_version["full"]},
                    {"brand": "Not=A?Brand", "version": "24.0.0.0"}
                ],
                "platform": platform,
                "platformVersion": self.device_info.get("platform_version", "14"),
                "architecture": self.device_info.get("architecture", "arm"),
                "model": self.device_info.get("device_model", ""),
                "mobile": True,
                "bitness": "64",
                "wow64": False
            }
        }
        
        driver.execute_cdp_cmd('Network.setUserAgentOverride', user_agent_metadata)
        
        logger.info(f"모바일 설정 적용 완료: {platform} / {self.device_info['device_model']}")
    
    def _inject_mobile_javascript(self, driver: webdriver.Chrome) -> None:
        """JavaScript를 통한 모바일 속성 주입"""
        is_android = "Android" in self.device_info["user_agent"]
        platform = "Android" if is_android else "iOS"
        
        js_script = """
        (() => {
            // Navigator 프록시 설정
            const originalNavigator = window.navigator;
            const navigatorProxy = new Proxy(originalNavigator, {
                get: function(target, prop) {
                    switch (prop) {
                        case 'platform':
                            return '%s';
                        case 'userAgent':
                            return '%s';
                        case 'appVersion':
                            return '%s';
                        case 'vendor':
                            return 'Google Inc.';
                        case 'languages':
                            return ['ko-KR', 'ko', 'en-US', 'en'];
                        case 'language':
                            return 'ko-KR';
                        case 'maxTouchPoints':
                            return 5;
                        case 'hardwareConcurrency':
                            return 8;
                        case 'deviceMemory':
                            return 8;
                        case 'connection':
                            return {
                                effectiveType: '4g',
                                rtt: 50,
                                downlink: 10,
                                saveData: false,
                                type: 'cellular'
                            };
                        case 'webdriver':
                            return undefined;
                        default:
                            return target[prop];
                    }
                }
            });
            
            Object.defineProperty(window, 'navigator', {
                value: navigatorProxy,
                configurable: false,
                writable: false
            });
            
            // 터치 이벤트 지원 추가
            window.ontouchstart = null;
            window.ontouchmove = null;
            window.ontouchend = null;
            window.ontouchcancel = null;
            
            // 화면 방향 설정
            Object.defineProperty(window, 'orientation', {
                get: function() { return 0; },
                configurable: false
            });
            
            // matchMedia 모바일 지원
            const originalMatchMedia = window.matchMedia;
            window.matchMedia = function(query) {
                const result = originalMatchMedia.call(window, query);
                if (query.includes('hover')) {
                    return { matches: false, media: query };
                }
                if (query.includes('pointer') && query.includes('coarse')) {
                    return { matches: true, media: query };
                }
                return result;
            };
            
            // screen 객체 설정
            Object.defineProperties(window.screen, {
                width: {
                    get: function() { return %d; }
                },
                height: {
                    get: function() { return %d; }
                },
                availWidth: {
                    get: function() { return %d; }
                },
                availHeight: {
                    get: function() { return %d; }
                }
            });
            
            // Chrome 객체 제거 (자동화 감지 방지)
            delete window.chrome;
            
            // Permissions API 모바일 동작
            if (navigator.permissions) {
                const originalQuery = navigator.permissions.query;
                navigator.permissions.query = function(parameters) {
                    return originalQuery.call(navigator.permissions, parameters);
                };
            }
            
            // 자동화 탐지 방지
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 플러그인 배열 비우기 (모바일은 플러그인 없음)
            Object.defineProperty(navigator, 'plugins', {
                get: () => []
            });
            
            console.log('모바일 에뮬레이션 JavaScript 적용 완료');
        })();
        """ % (
            platform,
            self.device_info["user_agent"],
            self.device_info["user_agent"].replace("Mozilla/", ""),
            self.device_info["width"],
            self.device_info["height"],
            self.device_info["width"],
            self.device_info["height"]
        )
        
        driver.execute_script(js_script)
        logger.info("모바일 JavaScript 주입 완료")
    
    def _verify_mobile_settings(self, driver: webdriver.Chrome) -> None:
        """모바일 설정 검증"""
        try:
            # 검증 스크립트
            verification_script = """
            return {
                platform: navigator.platform,
                userAgent: navigator.userAgent,
                mobile: /Android|iPhone|iPad|iPod/i.test(navigator.userAgent),
                touchPoints: navigator.maxTouchPoints,
                width: window.screen.width,
                height: window.screen.height,
                webdriver: navigator.webdriver,
                vendor: navigator.vendor
            };
            """
            
            result = driver.execute_script(verification_script)
            
            logger.info("=== 모바일 설정 검증 결과 ===")
            logger.info(f"플랫폼: {result['platform']}")
            logger.info(f"User Agent: {result['userAgent'][:80]}...")
            logger.info(f"모바일 감지: {result['mobile']}")
            logger.info(f"터치 포인트: {result['touchPoints']}")
            logger.info(f"화면 크기: {result['width']}x{result['height']}")
            logger.info(f"WebDriver: {result['webdriver']}")
            logger.info(f"Vendor: {result['vendor']}")
            logger.info("=" * 50)
            
            # 경고 출력
            is_android = "Android" in self.device_info["user_agent"]
            expected_platform = "Android" if is_android else "iOS"
            
            if result['platform'] != expected_platform and "iPhone" not in result['platform']:
                logger.warning(f"플랫폼 불일치: 예상={expected_platform}, 실제={result['platform']}")
            
            if not result['mobile']:
                logger.warning("모바일로 감지되지 않았습니다!")
            
            if result['touchPoints'] < 1:
                logger.warning("터치 포인트가 설정되지 않았습니다!")
                
        except Exception as e:
            logger.error(f"설정 검증 실패: {e}")
    
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
                subprocess.run(["taskkill", "/F", "/PID", str(self.chrome_pid)], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.run(["kill", "-9", str(self.chrome_pid)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.chrome_pid = None
            logger.info("Chrome 프로세스 종료 완료")
            
        except Exception as e:
            logger.error(f"Chrome 프로세스 종료 실패: {e}")


def test_mobile_driver():
    """테스트 함수"""
    import time
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Galaxy S24로 테스트
    mobile = MobileDriver(headless=False, device="galaxy_s24")
    driver = mobile.create_driver()
    
    try:
        # 테스트 페이지 방문
        print("\n네이버 모바일 사이트 접속 중...")
        driver.get("https://m.naver.com")
        time.sleep(3)
        
        print("\n5초 후 User Agent 확인 사이트 접속...")
        time.sleep(5)
        driver.get("https://www.whatismybrowser.com/detect/what-is-my-user-agent")
        time.sleep(5)
        
        print("\n테스트 완료! 브라우저를 확인하세요.")
        input("엔터를 누르면 종료합니다...")
        
    finally:
        mobile.quit_driver(driver)


if __name__ == "__main__":
    test_mobile_driver()

