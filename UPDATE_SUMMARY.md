# 🎉 Config 설정 통합 업데이트 완료

## 📋 업데이트 요약

`config/config.json` 파일을 통한 **중앙화된 설정 관리** 시스템이 프로젝트에 통합되었습니다!

---

## ✨ 주요 변경 사항

### 1️⃣ 설정 파일 자동 로드

**`main.py`**에 `load_config()` 함수가 추가되어 자동으로 설정을 로드합니다:

```python
def load_config(config_path="config/config.json"):
    """config.json 파일 로드"""
    # ✅ 파일이 있으면 로드
    # ⚠️ 파일이 없으면 기본 설정 사용
    # ❌ 로드 실패 시 기본 설정 사용
```

**실행 결과:**
```
✅ 설정 파일 로드 완료: config/config.json

============================================================
🔍 galaxy_s24 테스트 시작
============================================================

📋 현재 설정:
  - 기기: galaxy_s24
  - 헤드리스 모드: False
  - 대기 시간: 3초
  - 타임아웃: 10초
============================================================
```

### 2️⃣ NaverCrawler에 설정 적용

**`src/crawler.py`**가 config를 받아서 자동으로 적용합니다:

```python
# ✅ 이전
crawler = NaverCrawler(driver=driver)

# 🎯 현재 (config 자동 적용)
crawler = NaverCrawler(driver=driver, config=config)

# 자동으로 적용되는 설정:
# - timeout → DEFAULT_TIMEOUT
# - wait_time → get_page() 기본값
```

### 3️⃣ 유연한 함수 호출

**`single_device()` 함수 개선:**

```python
# 방법 1: config만 전달 (device는 config에서 가져옴)
single_device(url_list=url_list, config=config)

# 방법 2: device 명시적 지정 (config 설정 덮어쓰기)
single_device(device_name="iphone_15_pro", url_list=url_list, config=config)

# 방법 3: config 없이 사용 (자동 로드)
single_device(device_name="galaxy_s24", url_list=url_list)
```

---

## 📁 변경된 파일

### 수정된 파일 (3개)

1. **`main.py`**
   - `load_config()` 함수 추가
   - `single_device()` 함수 개선 (config 매개변수 추가)
   - 설정 정보 출력 기능 추가

2. **`src/crawler.py`**
   - `NaverCrawler.__init__()`: config 매개변수 추가
   - `get_page()`: wait_time을 config에서 가져오도록 수정
   - `DEFAULT_TIMEOUT`을 config의 timeout으로 설정

3. **`README.md`**
   - "설정 파일 (config.json)" 섹션 추가
   - "문서" 섹션에 CONFIG_USAGE.md 추가
   - 문제 해결에 설정 관련 항목 추가

### 새로 추가된 파일 (3개)

4. **`docs/CONFIG_USAGE.md`** ⭐ **NEW**
   - 설정 파일 사용법 완전 가이드
   - 40+ 줄의 상세 설명

5. **`CHANGELOG.md`** ⭐ **NEW**
   - 변경 이력 문서

6. **`UPDATE_SUMMARY.md`** ⭐ **NEW**
   - 이 문서!

---

## 🎯 적용되는 설정 항목

| 설정 항목 | 기본값 | 적용 위치 | 설명 |
|----------|-------|----------|------|
| `headless` | `false` | MobileDriver | 브라우저 창 표시 여부 |
| `device` | `"galaxy_s24"` | MobileDriver | 모바일 기기 선택 |
| `wait_time` | `3` | get_page() | 페이지 로드 후 대기 시간(초) |
| `timeout` | `10` | wait_for_element() | 요소 찾기 최대 대기 시간(초) |
| `use_mobile` | `true` | NaverCrawler | 모바일 에뮬레이션 사용 |

---

## 🚀 사용 방법

### 기본 사용 (추천)

**1. 설정 파일 확인**

`config/config.json`:
```json
{
  "headless": false,
  "wait_time": 3,
  "timeout": 10,
  "use_mobile": true,
  "device": "galaxy_s24"
}
```

**2. 프로그램 실행**

```bash
python main.py
```

설정이 자동으로 로드되고 적용됩니다! 🎉

### 설정 변경

#### 헤드리스 모드로 실행

```json
{
  "headless": true,  // ← 변경
  ...
}
```

#### 다른 기기 사용

```json
{
  "device": "iphone_15_pro",  // ← 변경
  ...
}
```

#### 느린 네트워크 대응

```json
{
  "wait_time": 5,   // 3 → 5
  "timeout": 20,    // 10 → 20
  ...
}
```

---

## 📚 문서

자세한 내용은 아래 문서를 참고하세요:

- [설정 파일 사용 가이드](docs/CONFIG_USAGE.md) ⭐ **필독**
- [변경 이력](CHANGELOG.md)
- [README](README.md)

---

## ✅ 검증 완료

- ✅ 설정 파일 로드 동작 확인
- ✅ 기본값 fallback 동작 확인
- ✅ 모든 설정 항목 적용 확인
- ✅ 하위 호환성 유지 확인
- ✅ 린터 에러 없음

---

## 💡 주요 장점

### 1. 코드 수정 없이 설정 변경
```
기기 변경: config.json 수정 → 저장 → 실행
(코드 수정 불필요!)
```

### 2. 중앙 관리
```
이전: main.py, crawler.py, mobile_driver.py 각각 수정
현재: config.json 하나만 수정
```

### 3. 에러 처리
```
설정 파일 없음 → 기본값 사용
설정 파일 손상 → 기본값 사용
프로그램 정상 동작 보장!
```

### 4. 유연성
```python
# 코드에서 덮어쓰기 가능
single_device(device_name="iphone_15_pro", config=config)
# config의 device를 무시하고 iPhone 사용
```

---

## 🎓 예제 코드

### 전체 흐름

```python
# main.py (자동으로 실행됨)

# 1. 설정 로드
config = load_config()

# 2. URL 리스트 준비
url_list = {
    "다이어리": "https://smartstore.naver.com/...",
    # ...
}

# 3. 크롤링 실행 (설정 자동 적용)
single_device(url_list=url_list, config=config)
```

### 수동 사용

```python
from src.crawler import NaverCrawler
from src.mobile_driver import MobileDriver
import json

# 설정 로드
with open("config/config.json", "r") as f:
    config = json.load(f)

# 드라이버 생성
mobile = MobileDriver(
    headless=config["headless"],
    device=config["device"]
)
driver = mobile.create_driver()

# 크롤러 생성
crawler = NaverCrawler(driver=driver, config=config)

# 사용 (wait_time이 자동으로 적용됨)
crawler.get_page("https://m.naver.com")
```

---

## 🐛 문제 해결

### Q. 설정이 적용되지 않아요!

**A.** 다음을 확인하세요:
1. `config/config.json` 파일이 있는지
2. JSON 형식이 올바른지 (쉼표, 따옴표)
3. 프로그램을 재시작했는지

### Q. 설정 파일이 없는데 실행되나요?

**A.** 네! 기본 설정으로 자동 실행됩니다:
```
⚠️ 설정 파일을 찾을 수 없습니다: config/config.json
기본 설정을 사용합니다.
```

### Q. 특정 설정만 덮어쓰고 싶어요

**A.** 함수 매개변수로 전달하세요:
```python
# config의 device를 무시하고 iPhone 사용
single_device(device_name="iphone_15_pro", config=config)
```

---

## 🔜 향후 계획

- [ ] 설정 검증 기능 (잘못된 값 체크)
- [ ] 프리셋 지원 (dev/prod/test)
- [ ] 환경 변수 지원 (.env)
- [ ] 설정 GUI 도구

---

## 📞 지원

문제가 발생하면 아래를 참고하세요:

1. [설정 가이드](docs/CONFIG_USAGE.md)
2. [README](README.md)
3. [변경 이력](CHANGELOG.md)

---

**업데이트 완료일**: 2024-11-18  
**버전**: Config Integration v1.0  
**상태**: ✅ 안정적 (Stable)

