"""
유틸리티 함수들
"""
import json
import csv
from pathlib import Path
from datetime import datetime


def save_to_json(data, filename=None):
    """
    데이터를 JSON 파일로 저장
    
    Args:
        data: 저장할 데이터
        filename: 파일명 (없으면 타임스탬프 사용)
    """
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_{timestamp}.json"
    
    filepath = data_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"데이터 저장 완료: {filepath}")
    return filepath


def save_to_csv(data, filename=None, fieldnames=None):
    """
    데이터를 CSV 파일로 저장
    
    Args:
        data: 저장할 데이터 (리스트 또는 딕셔너리 리스트)
        filename: 파일명 (없으면 타임스탬프 사용)
        fieldnames: CSV 헤더 필드명
    """
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_{timestamp}.csv"
    
    filepath = data_dir / filename
    
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        if isinstance(data[0], dict):
            if fieldnames is None:
                fieldnames = data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        else:
            writer = csv.writer(f)
            writer.writerows(data)
    
    print(f"데이터 저장 완료: {filepath}")
    return filepath


def load_config(config_file='config.json'):
    """
    설정 파일 로드
    
    Args:
        config_file: 설정 파일명
    """
    config_path = Path(__file__).parent.parent / "config" / config_file
    
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config, config_file='config.json'):
    """
    설정 파일 저장
    
    Args:
        config: 설정 데이터
        config_file: 설정 파일명
    """
    config_dir = Path(__file__).parent.parent / "config"
    config_dir.mkdir(exist_ok=True)
    
    config_path = config_dir / config_file
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    return config_path

