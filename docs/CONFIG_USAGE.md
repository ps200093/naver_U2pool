# 📋 Config 설정 사용 가이드

## 개요

이 프로젝트는 `config/config.json` 파일을 통해 크롤러의 동작을 중앙에서 관리할 수 있습니다.

## 설정 파일 위치

```
naver_U2pool/
├── config/
│   └── config.json  ← 설정 파일
├── main.py
└── src/
    ├── crawler.py
    └── mobile_driver.py
```

## 설정 항목

### `config/config.json` 구조

```json
{
  "driver_path": "",
  "headless": false,
  "wait_time": 3,
  "timeout": 10,
  "use_mobile": true,
  "device": "galaxy_s24",
  "mobile_devices": {
    "galaxy_s24": {
      "name": "Galaxy S24 Ultra",
      "platform": "Android",
      "version": "14"
    },
    "galaxy_s23": {
      "name": "Galaxy S23",
      "platform": "Android",
      "version": "13"
    },
    "iphone_15_pro": {
      "name": "iPhone 15 Pro",
      "platform": "iOS",
      "version": "17.0"
    },
    "iphone_14": {
      "name": "iPhone 14",
      "platform": "iOS",
      "version": "16.0"
    }
  },
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "notes": "use_mobile=true일 때는 device 설정에 따라 User Agent가 자동으로 설정됩니다."
}
```

### 설정 항목 설명

| 항목 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `driver_path` | string | `""` | 크롬 드라이버 경로 (비어있으면 자동 감지) |
| `headless` | boolean | `false` | 헤드리스 모드 사용 여부 (true: 브라우저 창 안 보임) |
| `wait_time` | number | `3` | 페이지 로드 후 기본 대기 시간 (초) |
| `timeout` | number | `10` | 요소 찾기 최대 대기 시간 (초) |
| `use_mobile` | boolean | `true` | 모바일 에뮬레이션 사용 여부 |
| `device` | string | `"galaxy_s24"` | 사용할 모바일 기기 (mobile_devices의 키 값) |
| `mobile_devices` | object | - | 사용 가능한 모바일 기기 목록 |
| `user_agent` | string | - | 사용자 에이전트 문자열 (데스크톱 모드에서 사용) |

## 사용 방법

### 1️⃣ 기본 사용 (main.py)

`main.py`를 실행하면 자동으로 `config/config.json`을 로드합니다:

```python
if __name__ == "__main__":
    # config.json 설정 로드
    config = load_config()
    
    url_list = {
        "다이어리": "https://smartstore.naver.com/...",
        # ...
    }
    
    # config 설정 사용
    single_device(url_list=url_list, config=config)
```

**실행 결과 예시:**

```
✅ 설정 파일 로드 완료: config/config.json

============================================================
🔍 galaxy_s24 테스트 시작
🔍 dict_keys(['다이어리', '바디스크럽', ...]) 테스트 시작
============================================================

📋 현재 설정:
  - 기기: galaxy_s24
  - 헤드리스 모드: False
  - 대기 시간: 3초
  - 타임아웃: 10초
============================================================
```

### 2️⃣ 수동으로 설정 지정

특정 기기를 명시적으로 지정할 수도 있습니다:

```python
# iPhone 15 Pro 사용
single_device(device_name="iphone_15_pro", url_list=url_list, config=config)

# Galaxy S23 사용
single_device(device_name="galaxy_s23", url_list=url_list, config=config)
```

### 3️⃣ NaverCrawler에서 직접 사용

```python
from src.crawler import NaverCrawler
from src.mobile_driver import MobileDriver
import json

# config 로드
with open("config/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# 드라이버 생성
mobile = MobileDriver(
    headless=config["headless"],
    device=config["device"]
)
driver = mobile.create_driver()

# 크롤러 생성 (config 전달)
crawler = NaverCrawler(
    driver=driver,
    config=config
)

# 페이지 접속 (wait_time이 config에서 자동으로 적용됨)
crawler.get_page("https://m.naver.com")
```

## 설정 변경 예시

### 헤드리스 모드로 실행하기

```json
{
  "headless": true,  // false → true로 변경
  "device": "galaxy_s24",
  ...
}
```

### 다른 기기로 변경하기

```json
{
  "device": "iphone_15_pro",  // galaxy_s24 → iphone_15_pro로 변경
  ...
}
```

### 타임아웃 늘리기 (느린 네트워크 환경)

```json
{
  "wait_time": 5,    // 3 → 5초로 증가
  "timeout": 20,     // 10 → 20초로 증가
  ...
}
```

## 적용되는 코드

### ✅ `main.py`

- `load_config()`: config.json 로드
- `single_device()`: config 설정 적용
  - `headless` → MobileDriver 생성 시 적용
  - `device` → 기기 선택
  - `wait_time` → 페이지 로드 대기

### ✅ `src/crawler.py` (NaverCrawler)

- `__init__()`: config 저장
  - `timeout` → `DEFAULT_TIMEOUT`으로 설정
- `get_page()`: `wait_time` 자동 적용
- `wait_for_element()`: `timeout` 자동 적용

### ✅ `src/mobile_driver.py` (MobileDriver)

- `__init__()`: 
  - `headless` → Chrome 옵션 적용
  - `device` → 모바일 기기 선택

## 에러 처리

### 설정 파일이 없는 경우

```
⚠️ 설정 파일을 찾을 수 없습니다: config/config.json
기본 설정을 사용합니다.
```

**기본 설정:**

```python
{
    "headless": False,
    "device": "galaxy_s24",
    "wait_time": 3,
    "timeout": 10,
    "use_mobile": True
}
```

### 설정 파일 로드 실패

```
❌ 설정 파일 로드 실패: [에러 메시지]
기본 설정을 사용합니다.
```

## 추천 설정

### 개발 중 (빠른 테스트)

```json
{
  "headless": false,     // 브라우저 보이기
  "wait_time": 2,        // 짧은 대기
  "timeout": 10,
  "device": "galaxy_s24"
}
```

### 프로덕션 (안정성 중시)

```json
{
  "headless": true,      // 백그라운드 실행
  "wait_time": 3,        // 안정적 대기
  "timeout": 15,         // 여유로운 타임아웃
  "device": "galaxy_s24"
}
```

### 디버깅 (느린 네트워크)

```json
{
  "headless": false,
  "wait_time": 5,        // 긴 대기
  "timeout": 30,         // 매우 긴 타임아웃
  "device": "galaxy_s24"
}
```

## 주의사항

1. **JSON 형식 준수**: 주석(`//`)은 실제 JSON에서 사용 불가 (위 예시는 설명용)
2. **boolean 값**: `true`/`false` (소문자, 따옴표 없음)
3. **device 값**: `mobile_devices`에 정의된 키만 사용 가능
4. **문자열 인코딩**: UTF-8 사용

## 문제 해결

### Q. 설정이 적용되지 않아요!

**A.** 다음을 확인하세요:
1. `config/config.json` 파일이 존재하는지
2. JSON 형식이 올바른지 (쉼표, 따옴표 확인)
3. 프로그램을 재시작했는지

### Q. 특정 기기가 작동하지 않아요!

**A.** `mobile_devices`에 해당 기기가 정의되어 있는지 확인하세요.

### Q. 타임아웃 에러가 계속 발생해요!

**A.** `timeout` 값을 20~30으로 늘려보세요.

---

## 📚 관련 문서

- [빠른 시작 가이드](QUICKSTART.md)
- [모바일 에뮬레이션 가이드](MOBILE_EMULATION_GUIDE.md)
- [고급 동작 가이드](ADVANCED_ACTIONS.md)

