"""
Simple URL Visitor with NordVPN IP Rotation
간단한 URL 방문기 (NordVPN IP 변경)
"""

import time
import random
import logging
import argparse
import requests
import gc
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NordVPNCLI:
    """NordVPN CLI 제어 (Windows 최적화)"""
    
    def __init__(self, target_country="KR"):
        """
        초기화
        
        Args:
            target_country: 타겟 국가 코드 (KR, JP, US 등)
        """
        self.target_country = target_country
        self.nordvpn_path = self._find_nordvpn_path()
        self.country_map = {
            "KR": "South Korea",
            "JP": "Japan",
            "US": "United States",
            "GB": "United Kingdom",
            "DE": "Germany",
            "FR": "France",
            "CA": "Canada",
            "AU": "Australia",
            "SG": "Singapore",
            "TW": "Taiwan"
        }
    
    def _find_nordvpn_path(self):
        """Windows에서 NordVPN CLI 경로 찾기"""
        import os
        
        # 가능한 경로들
        possible_paths = [
            r"C:\Program Files\NordVPN\nordvpn.exe",
            r"C:\Program Files (x86)\NordVPN\nordvpn.exe",
            os.path.expanduser(r"~\AppData\Local\NordVPN\nordvpn.exe"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"[OK] NordVPN CLI 발견: {path}")
                return path
        
        # PATH에서 찾기
        import shutil
        cli_path = shutil.which("nordvpn")
        if cli_path:
            logger.info(f"[OK] NordVPN CLI 발견: {cli_path}")
            return cli_path
        
        logger.warning("[WARNING] NordVPN CLI를 찾을 수 없습니다.")
        return None
    
    def _run_command(self, *args, timeout=30):
        """
        NordVPN CLI 명령 실행
        
        Args:
            *args: 명령 인자들
            timeout: 타임아웃 (초)
        
        Returns:
            tuple: (success, output)
        """
        import subprocess
        import os
        
        if not self.nordvpn_path:
            logger.error("[ERROR] NordVPN CLI 경로가 없습니다.")
            return False, "CLI not found"
        
        try:
            # NordVPN 디렉토리로 이동 (중요!)
            nordvpn_dir = os.path.dirname(self.nordvpn_path)
            original_dir = os.getcwd()
            
            if nordvpn_dir and os.path.exists(nordvpn_dir):
                os.chdir(nordvpn_dir)
                logger.debug(f"[DEBUG] 작업 디렉토리 변경: {nordvpn_dir}")
            
            # 명령 실행 (디렉토리 내에서 nordvpn 명령 직접 사용)
            cmd = ['nordvpn'] + list(args)
            logger.debug(f"[DEBUG] 실행: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = result.stdout + result.stderr
            success = result.returncode == 0
            
            # 원래 디렉토리로 복귀
            os.chdir(original_dir)
            
            return success, output
        
        except subprocess.TimeoutExpired:
            logger.error(f"[ERROR] 명령 타임아웃 ({timeout}초)")
            # 원래 디렉토리로 복귀
            try:
                os.chdir(original_dir)
            except:
                pass
            return False, "Timeout"
        except Exception as e:
            logger.error(f"[ERROR] 명령 실행 실패: {e}")
            # 원래 디렉토리로 복귀
            try:
                os.chdir(original_dir)
            except:
                pass
            return False, str(e)
    
    def connect(self, country_code=None):
        """
        NordVPN 서버에 연결
        
        Args:
            country_code: 국가 코드 (None이면 타겟 국가 사용)
        
        Returns:
            bool: 연결 성공 여부
        """
        if not self.nordvpn_path:
            logger.error("[ERROR] NordVPN CLI가 설치되지 않았습니다.")
            logger.error("[TIP] NordVPN 앱 설치: https://nordvpn.com/download/")
            return False
        
        try:
            country = country_code or self.target_country
            country_name = self.country_map.get(country, "South Korea")
            
            logger.info(f"[VPN] NordVPN 연결 중... ({country_name})")
            
            # NordVPN 연결
            success, output = self._run_command("-c", "-g", country_name)
            
            logger.debug(f"[DEBUG] 출력: {output[:200]}")
            
            if success or "connected" in output.lower() or "연결" in output.lower():
                logger.info(f"[OK] VPN 연결 완료: {country_name}")
                time.sleep(3)  # 연결 안정화
                return True
            else:
                logger.error(f"[ERROR] VPN 연결 실패: {output[:200]}")
                return False
        
        except Exception as e:
            logger.error(f"[ERROR] VPN 연결 오류: {e}")
            return False
    
    def disconnect(self):
        """VPN 연결 해제"""
        if not self.nordvpn_path:
            return False
        
        try:
            logger.info("[VPN] VPN 연결 해제 중...")
            
            success, output = self._run_command("-d", timeout=15)
            
            if success or "disconnected" in output.lower() or "연결 해제" in output.lower():
                logger.info("[OK] VPN 연결 해제 완료")
                time.sleep(2)
                return True
            else:
                logger.warning(f"[WARNING] VPN 해제 실패: {output[:200]}")
                return False
        
        except Exception as e:
            logger.warning(f"[WARNING] VPN 해제 오류: {e}")
            return False
    
    def get_status(self):
        """현재 VPN 상태 확인"""
        if not self.nordvpn_path:
            return None
        
        try:
            success, output = self._run_command("-status", timeout=10)
            
            if success:
                logger.info(f"[STATUS] {output[:200]}")
                return output
            else:
                return None
        
        except Exception as e:
            logger.error(f"[ERROR] 상태 확인 오류: {e}")
            return None


class NordVPNRotator:
    """NordVPN 프록시 로테이션"""
    
    def __init__(self, username=None, password=None):
        """
        초기화
        
        Args:
            username: NordVPN 계정 (또는 프록시 사용자명)
            password: NordVPN 비밀번호 (또는 프록시 비밀번호)
        """
        self.username = username
        self.password = password
        self.servers = []
        self.current_index = 0
    
    def fetch_nordvpn_servers(self, limit=50, use_http=True, target_countries=None):
        """
        NordVPN 서버 목록 가져오기 (공식 API)
        https://api.nordvpn.com/v1/servers
        
        Args:
            limit: 가져올 서버 개수
            use_http: True면 HTTP 프록시 (권장), False면 SOCKS5
            target_countries: 국가 코드 리스트 (예: ["KR", "JP"]), None이면 모든 국가
        """
        try:
            # 국가 필터 표시
            if target_countries:
                country_str = ", ".join(target_countries)
                logger.info(f"[API] NordVPN 서버 목록 가져오는 중... (국가: {country_str}, 최대 {limit}개)")
            else:
                logger.info(f"[API] NordVPN 서버 목록 가져오는 중... (모든 국가, 최대 {limit}개)")
            
            # NordVPN 공식 API
            tech_filter = "proxy_ssl" if use_http else "proxy"  # HTTP or SOCKS5
            
            params = {
                "limit": limit,
                "filters[servers_technologies][identifier]": tech_filter,
            }
            
            # 국가 필터 추가
            if target_countries:
                # 예: filters[country_id]=87 (한국은 87)
                # 여러 국가는 OR 조건
                params["filters[country_code]"] = ",".join(target_countries)
            
            response = requests.get(
                "https://api.nordvpn.com/v1/servers",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # HTTP 프록시: 89 포트, SOCKS5: 1080 포트
                port = 89 if use_http else 1080
                protocol = "https" if use_http else "socks5"
                
                # 프록시 서버 추출
                for server in data:
                    hostname = server.get('hostname')
                    if hostname:
                        country_name = server.get('locations', [{}])[0].get('country', {}).get('name', 'Unknown')
                        country_code = server.get('locations', [{}])[0].get('country', {}).get('code', 'XX')
                        
                        # 국가 필터링 (API 필터가 작동하지 않을 경우 대비)
                        if target_countries and country_code not in target_countries:
                            continue
                        
                        self.servers.append({
                            'host': hostname,
                            'port': port,
                            'protocol': protocol,
                            'country': country_name,
                            'country_code': country_code
                        })
                
                # 폴백: 타겟 국가 서버가 없으면 모든 국가 서버 재시도
                if not self.servers and target_countries:
                    logger.warning(f"[WARNING] 타겟 국가({', '.join(target_countries)}) 서버를 찾을 수 없습니다.")
                    logger.info(f"[FALLBACK] 모든 국가 서버로 재시도 중...")
                    
                    # 국가 필터 없이 재시도
                    params_fallback = {
                        "limit": limit,
                        "filters[servers_technologies][identifier]": tech_filter,
                    }
                    
                    response_fallback = requests.get(
                        "https://api.nordvpn.com/v1/servers",
                        params=params_fallback
                    )
                    
                    if response_fallback.status_code == 200:
                        data_fallback = response_fallback.json()
                        
                        for server in data_fallback:
                            hostname = server.get('hostname')
                            if hostname:
                                country_name = server.get('locations', [{}])[0].get('country', {}).get('name', 'Unknown')
                                country_code = server.get('locations', [{}])[0].get('country', {}).get('code', 'XX')
                                
                                self.servers.append({
                                    'host': hostname,
                                    'port': port,
                                    'protocol': protocol,
                                    'country': country_name,
                                    'country_code': country_code
                                })
                        
                        logger.info(f"[OK] 폴백 성공: {len(self.servers)}개 서버 로드 (모든 국가)")
                
                # 국가별 개수 세기
                if self.servers:
                    country_counts = {}
                    for server in self.servers:
                        country = server['country']
                        country_counts[country] = country_counts.get(country, 0) + 1
                    
                    count_str = ", ".join([f"{country}: {count}개" for country, count in country_counts.items()])
                    logger.info(f"[OK] {len(self.servers)}개 서버 로드 완료 ({protocol.upper()} 프록시)")
                    logger.info(f"[INFO] 국가별 분포: {count_str}")
                else:
                    logger.error(f"[ERROR] 사용 가능한 서버가 없습니다.")
                    return False
                
                return True
            else:
                logger.error(f"[ERROR] API 요청 실패: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"[ERROR] 서버 목록 가져오기 실패: {e}")
            return False
    
    def get_next_server(self):
        """
        다음 서버 선택 (순환)
        
        Returns:
            dict: 서버 정보
        """
        if not self.servers:
            logger.warning("[WARNING] 사용 가능한 서버가 없습니다")
            return None
        
        server = self.servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.servers)
        
        return server
    
    def get_random_server(self):
        """
        랜덤 서버 선택
        
        Returns:
            dict: 서버 정보
        """
        if not self.servers:
            logger.warning("[WARNING] 사용 가능한 서버가 없습니다")
            return None
        
        return random.choice(self.servers)


class SimpleVisitor:
    """간단한 URL 방문기"""
    
    def __init__(self, headless=False, use_nordvpn=False, nordvpn_username=None, nordvpn_password=None, target_countries=None, guest_mode=True, use_cli=True):
        """
        초기화
        
        Args:
            headless: 헤드리스 모드
            use_nordvpn: NordVPN 사용 여부
            nordvpn_username: NordVPN 사용자명 (프록시 방식)
            nordvpn_password: NordVPN 비밀번호 (프록시 방식)
            target_countries: 국가 코드 리스트 (예: ["KR", "JP"]), None이면 모든 국가
            guest_mode: 게스트 모드 사용 (기본: True)
            use_cli: NordVPN CLI 사용 (기본: True, 프록시보다 안정적)
        """
        self.headless = headless
        self.use_nordvpn = use_nordvpn
        self.use_cli = use_cli
        self.nordvpn = None
        self.nordvpn_cli = None
        self.driver = None
        self.guest_mode = guest_mode
        
        if use_nordvpn:
            if use_cli:
                # CLI 방식 (권장)
                target_country = target_countries[0] if target_countries else "KR"
                self.nordvpn_cli = NordVPNCLI(target_country)
                logger.info("[VPN] NordVPN CLI 모드 (권장)")
            else:
                # 프록시 방식 (기존)
                self.nordvpn = NordVPNRotator(nordvpn_username, nordvpn_password)
                # 서버 목록 로드 (HTTP 프록시 사용 - 더 안정적)
                self.nordvpn.fetch_nordvpn_servers(limit=100, use_http=True, target_countries=target_countries)
                logger.info("[VPN] NordVPN 프록시 모드")
    
    def create_driver(self, proxy_server=None):
        """
        Chrome 드라이버 생성
        
        Args:
            proxy_server: 프록시 서버 정보 (dict)
        """
        try:
            options = Options()
            
            # 헤드리스 모드
            if self.headless:
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
            
            # 게스트 모드
            if self.guest_mode:
                options.add_argument("--guest")
                logger.info("[GUEST] 게스트 모드 활성화")
            
            # 프록시 설정 (인증 포함)
            if proxy_server and self.nordvpn:
                proxy_host = proxy_server['host']
                proxy_port = proxy_server['port']
                protocol = proxy_server.get('protocol', 'socks5')
                
                # NordVPN 프록시 인증 정보
                username = self.nordvpn.username
                password = self.nordvpn.password
                
                if username and password:
                    # 프록시 (인증 포함)
                    proxy_url = f'{protocol}://{username}:{password}@{proxy_host}:{proxy_port}'
                    options.add_argument(f'--proxy-server={proxy_url}')
                    country_info = f"{proxy_server.get('country', 'Unknown')} ({proxy_server.get('country_code', 'XX')})"
                    logger.info(f"[PROXY] {protocol.upper()} {proxy_host}:{proxy_port} {country_info} [인증 적용]")
                else:
                    # 인증 없이 (작동 안 될 수 있음)
                    options.add_argument(f'--proxy-server={protocol}://{proxy_host}:{proxy_port}')
                    logger.warning(f"[WARNING] 프록시 인증 정보 없음 - 연결 실패 가능")
                    logger.info(f"[PROXY] {protocol.upper()} {proxy_host}:{proxy_port} ({proxy_server.get('country', 'Unknown')})")
            
            # 기본 설정
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # 드라이버 생성
            self.driver = webdriver.Chrome(options=options)
            
            logger.info("[OK] 드라이버 생성 완료")
            return self.driver
        
        except Exception as e:
            logger.error(f"[ERROR] 드라이버 생성 실패: {e}")
            raise
    
    def visit_url(self, url, wait_min=3, wait_max=10):
        """
        URL 방문
        
        Args:
            url: 방문할 URL
            wait_min: 최소 대기 시간 (초)
            wait_max: 최대 대기 시간 (초)
        """
        try:
            logger.info(f"[VISIT] {url}")
            self.driver.get(url)
            
            # 페이지 로드 대기
            time.sleep(2)
            
            # 랜덤 대기
            wait_time = random.uniform(wait_min, wait_max)
            logger.info(f"[WAIT] {wait_time:.1f}초 대기 중...")
            time.sleep(wait_time)
            
            logger.info(f"[OK] 방문 완료")
            return True
        
        except Exception as e:
            logger.error(f"[ERROR] 방문 실패: {e}")
            return False
    
    def close(self):
        """드라이버 종료 및 메모리 정리"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("[OK] 드라이버 종료 완료")
            except Exception as e:
                logger.warning(f"[WARNING] 드라이버 종료 중 오류: {e}")
            finally:
                # 참조 해제
                self.driver = None
        
        # 명시적 가비지 컬렉션
        gc.collect()
        logger.debug("[MEMORY] 가비지 컬렉션 완료")
    
    def run(self, url, repeat_count=10, wait_min=3, wait_max=10, rest_minutes=0):
        """
        URL 반복 방문
        
        Args:
            url: 방문할 URL
            repeat_count: 반복 횟수
            wait_min: 최소 대기 시간 (초)
            wait_max: 최대 대기 시간 (초)
            rest_minutes: 사이클 간 휴식 시간 (분)
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"[START] URL 반복 방문 시작")
        logger.info(f"{'='*70}")
        logger.info(f"  - URL: {url}")
        logger.info(f"  - 반복 횟수: {repeat_count}")
        logger.info(f"  - 대기 시간: {wait_min}~{wait_max}초")
        logger.info(f"  - 게스트 모드: 사용")
        logger.info(f"  - NordVPN: {'사용' if self.use_nordvpn else '사용 안 함'}")
        logger.info(f"{'='*70}\n")
        
        success_count = 0
        fail_count = 0
        
        for i in range(1, repeat_count + 1):
            logger.info(f"\n{'='*70}")
            logger.info(f"[CYCLE] {i}/{repeat_count}")
            logger.info(f"{'='*70}")
            
            try:
                # IP 변경 (NordVPN)
                proxy_server = None
                if self.use_nordvpn:
                    if self.use_cli and self.nordvpn_cli:
                        # CLI 방식: VPN 연결
                        self.nordvpn_cli.connect()
                    elif self.nordvpn:
                        # 프록시 방식: 프록시 서버 선택
                        proxy_server = self.nordvpn.get_random_server()
                        if proxy_server:
                            logger.info(f"[VPN] 서버 변경: {proxy_server['country']}")
                
                # 새 드라이버 생성 (CLI 방식은 프록시 없음)
                if self.use_cli or not self.use_nordvpn:
                    self.create_driver(None)
                else:
                    self.create_driver(proxy_server)
                
                # URL 방문
                success = self.visit_url(url, wait_min, wait_max)
                
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                
            except Exception as e:
                logger.error(f"[ERROR] 사이클 {i} 실패: {e}")
                fail_count += 1
            
            finally:
                # 드라이버 종료 및 메모리 정리
                self.close()
                
                # 주기적 메모리 정리 (매 10회마다)
                if i % 10 == 0:
                    logger.info(f"[MEMORY] 주기적 메모리 정리 중... ({i}/{repeat_count})")
                    gc.collect()
                    time.sleep(1)  # 시스템 안정화
                
                # 휴식 시간
                if i < repeat_count and rest_minutes > 0:
                    rest_seconds = int(rest_minutes * 60)
                    logger.info(f"\n[REST] {rest_minutes}분 휴식 중...")
                    time.sleep(rest_seconds)
        
        # 최종 통계
        logger.info(f"\n{'='*70}")
        logger.info(f"[DONE] 완료!")
        logger.info(f"{'='*70}")
        logger.info(f"  - 성공: {success_count}")
        logger.info(f"  - 실패: {fail_count}")
        logger.info(f"  - 성공률: {success_count / repeat_count * 100:.1f}%")
        logger.info(f"{'='*70}")
        
        # 최종 메모리 정리
        logger.info(f"[MEMORY] 최종 메모리 정리 중...")
        gc.collect()
        
        # VPN 연결 해제 (CLI 방식)
        if self.use_nordvpn and self.use_cli and self.nordvpn_cli:
            self.nordvpn_cli.disconnect()
        
        logger.info(f"[OK] 모든 작업 완료 및 메모리 정리 완료")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='Simple URL Visitor with NordVPN',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # 기본 실행 (NordVPN 없이)
  python simple_visitor.py --url "https://example.com" --repeat 10
  
  # NordVPN 사용
  python simple_visitor.py --url "https://example.com" --repeat 10 --nordvpn --username YOUR_USERNAME --password YOUR_PASSWORD
  
  # 헤드리스 모드
  python simple_visitor.py --url "https://example.com" --repeat 5 --headless
  
  # 대기 시간 설정
  python simple_visitor.py --url "https://example.com" --repeat 10 --wait-min 5 --wait-max 15
        '''
    )
    
    parser.add_argument('--url', type=str, required=True, help='방문할 URL')
    parser.add_argument('--repeat', '-r', type=int, default=10, help='반복 횟수 (기본: 10)')
    parser.add_argument('--wait-min', type=float, default=3.0, help='최소 대기 시간 (초, 기본: 3)')
    parser.add_argument('--wait-max', type=float, default=10.0, help='최대 대기 시간 (초, 기본: 10)')
    parser.add_argument('--rest', type=float, default=0, help='사이클 간 휴식 시간 (분, 기본: 0)')
    parser.add_argument('--headless', action='store_true', help='헤드리스 모드')
    parser.add_argument('--no-guest', action='store_true', help='게스트 모드 비활성화 (기본: 활성화)')
    parser.add_argument('--nordvpn', action='store_true', help='NordVPN 사용')
    parser.add_argument('--username', type=str, help='NordVPN 사용자명')
    parser.add_argument('--password', type=str, help='NordVPN 비밀번호')
    parser.add_argument('--countries', type=str, help='국가 코드 (쉼표 구분, 예: KR,JP,US)')
    
    args = parser.parse_args()
    
    # 국가 코드 파싱
    target_countries = None
    if args.countries:
        target_countries = [c.strip().upper() for c in args.countries.split(',')]
    
    # Visitor 생성
    visitor = SimpleVisitor(
        headless=args.headless,
        use_nordvpn=args.nordvpn,
        nordvpn_username=args.username,
        nordvpn_password=args.password,
        target_countries=target_countries,
        guest_mode=not args.no_guest  # --no-guest가 없으면 True
    )
    
    try:
        # 실행
        visitor.run(
            url=args.url,
            repeat_count=args.repeat,
            wait_min=args.wait_min,
            wait_max=args.wait_max,
            rest_minutes=args.rest
        )
    except KeyboardInterrupt:
        logger.info("\n[STOP] 사용자 중단")
    finally:
        visitor.close()


if __name__ == "__main__":
    main()
