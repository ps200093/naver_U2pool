"""
Wikitree Visitor - Config File Version
설정 파일(wikitree_config.json)을 사용하는 버전
"""

import json
import logging
from pathlib import Path
from wikitree_visitor import WikitreeVisitor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path="wikitree_config.json"):
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
    config = load_config()

    if not config:
        logger.error("[ERROR] 설정 파일을 로드할 수 없습니다. 종료합니다.")
        return

    logger.info(f"\n{'='*70}")
    logger.info(f"[CONFIG] 위키트리 방문기 설정")
    logger.info(f"{'='*70}")
    logger.info(f"  - 반복 횟수: {config.get('repeat_count', 10)}")
    logger.info(f"  - 체류 시간: {config.get('dwell_min', 10)}~{config.get('dwell_max', 30)}초")
    logger.info(f"  - 휴식 시간: {config.get('rest_minutes', 0)}분")
    logger.info(f"  - 헤드리스: {config.get('headless', False)}")
    logger.info(f"  - 게스트 모드: {config.get('guest_mode', True)}")
    logger.info(f"  - NordVPN: {config.get('use_nordvpn', False)}")
    if config.get('use_nordvpn'):
        use_cli = config.get('use_cli', True)
        logger.info(f"  - VPN 방식: {'CLI (권장)' if use_cli else '프록시'}")
        target_countries = config.get('target_countries')
        if target_countries:
            logger.info(f"  - 타겟 국가: {', '.join(target_countries)}")
    logger.info(f"{'='*70}\n")

    visitor = WikitreeVisitor(
        headless=config.get('headless', False),
        use_nordvpn=config.get('use_nordvpn', False),
        nordvpn_username=config.get('nordvpn_username'),
        nordvpn_password=config.get('nordvpn_password'),
        target_countries=config.get('target_countries'),
        guest_mode=config.get('guest_mode', True),
        use_cli=config.get('use_cli', True),
    )

    try:
        visitor.run(
            repeat_count=config.get('repeat_count', 10),
            dwell_min=config.get('dwell_min', 10),
            dwell_max=config.get('dwell_max', 30),
            max_scroll_time=config.get('max_scroll_time', 60),
            rest_minutes=config.get('rest_minutes', 0),
        )
    except KeyboardInterrupt:
        logger.info("\n[STOP] 사용자 중단")
    finally:
        visitor.close()


if __name__ == "__main__":
    main()
