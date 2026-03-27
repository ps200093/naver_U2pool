"""
Simple URL Visitor - Config File Version
설정 파일(simple_config.json)을 사용하는 버전
"""

import json
import logging
from pathlib import Path
from simple_visitor import SimpleVisitor


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path="simple_config.json"):
    """설정 파일 로드"""
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            logger.error(f"[ERROR] 설정 파일을 찾을 수 없습니다: {config_path}")
            return None
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"[OK] 설정 파일 로드: {config_path}")
            return config
    
    except Exception as e:
        logger.error(f"[ERROR] 설정 파일 로드 실패: {e}")
        return None


def main():
    """메인 함수"""
    # 설정 파일 로드
    config = load_config()
    
    if not config:
        logger.error("[ERROR] 설정 파일을 로드할 수 없습니다. 종료합니다.")
        return
    
    # 필수 항목 체크
    if not config.get('url'):
        logger.error("[ERROR] URL이 설정되지 않았습니다.")
        return
    
    # 설정 출력
    logger.info(f"\n{'='*70}")
    logger.info(f"[CONFIG] 설정 정보")
    logger.info(f"{'='*70}")
    logger.info(f"  - URL: {config.get('url')}")
    logger.info(f"  - 반복 횟수: {config.get('repeat_count', 10)}")
    logger.info(f"  - 대기 시간: {config.get('wait_min', 3)}~{config.get('wait_max', 10)}초")
    logger.info(f"  - 휴식 시간: {config.get('rest_minutes', 0)}분")
    logger.info(f"  - 헤드리스: {config.get('headless', False)}")
    logger.info(f"  - 게스트 모드: {config.get('guest_mode', True)}")
    logger.info(f"  - NordVPN: {config.get('use_nordvpn', False)}")
    if config.get('use_nordvpn'):
        logger.info(f"  - NordVPN 계정: {config.get('nordvpn_username', '설정 안 됨')}")
        target_countries = config.get('target_countries')
        if target_countries:
            logger.info(f"  - 타겟 국가: {', '.join(target_countries)}")
        else:
            logger.info(f"  - 타겟 국가: 모든 국가")
    logger.info(f"{'='*70}\n")
    
    # Visitor 생성
    visitor = SimpleVisitor(
        headless=config.get('headless', False),
        use_nordvpn=config.get('use_nordvpn', False),
        nordvpn_username=config.get('nordvpn_username'),
        nordvpn_password=config.get('nordvpn_password'),
        target_countries=config.get('target_countries'),
        guest_mode=config.get('guest_mode', True)  # 기본값: True (게스트 모드)
    )
    
    try:
        # 실행
        visitor.run(
            url=config['url'],
            repeat_count=config.get('repeat_count', 10),
            wait_min=config.get('wait_min', 3),
            wait_max=config.get('wait_max', 10),
            rest_minutes=config.get('rest_minutes', 0)
        )
    except KeyboardInterrupt:
        logger.info("\n[STOP] 사용자 중단")
    finally:
        visitor.close()


if __name__ == "__main__":
    main()
