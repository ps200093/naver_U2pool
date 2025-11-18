# 변경 이력 (Changelog)

## [업데이트] 2024-11-18 - Config 설정 통합

### ✨ 새로운 기능

#### 중앙화된 설정 관리
- `config/config.json` 파일을 통한 중앙 설정 관리 추가
- 모든 설정을 한 곳에서 관리 가능

#### 자동 설정 로드
- `main.py` 실행 시 `config.json` 자동 로드
- 설정 파일이 없을 경우 기본값 사용

### 🔧 개선 사항

#### `main.py`
- `load_config()` 함수 추가: config.json 로드 및 에러 처리
- `single_device()` 함수 개선:
  - `config` 매개변수 추가
  - `device_name`이 없으면 config에서 자동으로 가져오기
  - 현재 설정 출력 기능 추가
  - `wait_time`을 config에서 가져오도록 수정

#### `src/crawler.py` (NaverCrawler)
- `__init__()`:
  - `config` 매개변수 추가
  - `DEFAULT_TIMEOUT`을 config의 `timeout` 값으로 설정
- `get_page()`:
  - `wait_time` 매개변수를 선택적으로 변경
  - 값이 없으면 config의 `wait_time` 사용

### 📄 새로운 문서

#### `docs/CONFIG_USAGE.md`
- 설정 파일 사용법 상세 가이드
- 설정 항목 설명
- 사용 예제
- 문제 해결 가이드

### 📝 문서 업데이트

#### `README.md`
- "설정 파일 (config.json)" 섹션 추가
- 주요 설정 항목 설명
- 사용 가능한 기기 목록
- 설정 변경 예시
- "문서" 섹션에 CONFIG_USAGE.md 링크 추가
- 문제 해결에 설정 관련 내용 추가

### 🎯 적용된 설정

| 설정 | 적용 위치 | 효과 |
|------|----------|------|
| `headless` | `MobileDriver`, `NaverCrawler` | 브라우저 창 표시 여부 |
| `device` | `MobileDriver` | 모바일 기기 선택 |
| `wait_time` | `get_page()`, 페이지 로드 후 | 기본 대기 시간 |
| `timeout` | `wait_for_element()` 등 | 요소 찾기 타임아웃 |
| `use_mobile` | `NaverCrawler` | 모바일 에뮬레이션 사용 |

### 🔄 사용 방법 변경

#### 이전 방식
```python
# 하드코딩된 값 사용
mobile = MobileDriver(headless=False, device="galaxy_s24")
crawler = NaverCrawler(driver=driver)
```

#### 새로운 방식
```python
# config.json에서 설정 로드
config = load_config()
mobile = MobileDriver(
    headless=config.get("headless", False),
    device=config.get("device", "galaxy_s24")
)
crawler = NaverCrawler(driver=driver, config=config)
```

### 💡 주요 장점

1. **중앙 관리**: 모든 설정을 한 곳에서 관리
2. **유연성**: 코드 수정 없이 설정만 변경
3. **재사용성**: 여러 프로젝트에서 동일한 구조 사용 가능
4. **에러 처리**: 설정 파일이 없어도 기본값으로 동작
5. **가독성**: 코드가 더 깔끔해짐

### 🐛 버그 수정
- 없음 (기능 추가만)

### ⚠️ Breaking Changes
- 없음 (하위 호환성 유지)
- 기존 코드도 그대로 동작합니다

### 📋 Todo
- [ ] 설정 검증 기능 추가
- [ ] 설정 프리셋 (개발/프로덕션) 추가
- [ ] 환경 변수 지원 추가

---

## 이전 버전

프로젝트 초기 버전 - 기본 크롤링 기능 구현

