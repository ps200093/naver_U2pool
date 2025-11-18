# 네이버 모바일 크롤러 (U2pool)

완벽한 모바일 에뮬레이션 기능을 갖춘 네이버 크롤링 프로젝트입니다.

## 📋 프로젝트 소개

실제 모바일 기기처럼 완벽하게 위장하여 네이버 모바일 사이트를 크롤링하는 도구입니다.
Galaxy S24, iPhone 15 Pro 등 다양한 최신 모바일 기기를 에뮬레이션할 수 있습니다.

## 📁 프로젝트 구조

```
naver_U2pool/
│
├── src/                    # 소스 코드
│   ├── __init__.py
│   ├── crawler.py         # 메인 크롤러 클래스 (고급 동작 메서드 포함)
│   ├── mobile_driver.py   # 모바일 에뮬레이션 드라이버 (핵심!)
│   └── utils.py           # 유틸리티 함수들
│
├── examples/               # 예제 코드
│   ├── simple_example.py
│   ├── advanced_example.py
│   └── advanced_actions_example.py  # 고급 동작 예제
│
├── config/                 # 설정 파일
│   └── config.json        # 크롤러 설정
│
├── logs/                   # 로그 파일 (자동 생성)
│   └── crawler.log
│
├── data/                   # 크롤링 데이터 저장 (자동 생성)
│   ├── *.json
│   └── *.csv
│
├── drivers/                # 크롬드라이버 저장 위치
│   └── chromedriver.exe
│
├── main.py                 # 메인 실행 파일
├── requirements.txt        # 필요한 패키지 목록
├── .gitignore
└── README.md
```

## 🚀 설치 및 실행

### 1. 가상환경 생성 (권장)

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 크롬드라이버 설치

**✅ 자동 탐색 (권장)**
- 프로젝트가 자동으로 `drivers/chromedriver.exe`를 찾습니다
- Chrome 브라우저만 설치되어 있으면 됩니다

**방법 1: 수동 설치**
1. Chrome 브라우저 버전 확인: `chrome://version`
2. [ChromeDriver 다운로드](https://googlechromelabs.github.io/chrome-for-testing/)
3. `drivers/` 폴더에 `chromedriver.exe` 저장

**방법 2: 환경변수 설정**
```bash
# PowerShell
$env:CHROME_DRIVER_PATH = "C:\path\to\chromedriver.exe"
```

### 4. 실행

**기본 실행:**
```bash
python main.py
```

**테스트 실행:**
```bash
# 모바일 드라이버 테스트
python test_mobile.py

# 사용 예제 실행
python examples/simple_example.py
```

**직접 사용:**
```bash
# Python 인터프리터에서
python
>>> from src.mobile_driver import MobileDriver
>>> mobile = MobileDriver(headless=False, device="galaxy_s24")
>>> driver = mobile.create_driver()
>>> driver.get("https://m.naver.com")
```

## 📖 사용 예시

### 🎯 모바일 에뮬레이션 사용법 (추천!)

#### 기본 사용법
```python
from src.crawler import NaverCrawler

# Galaxy S24로 모바일 크롤링
with NaverCrawler(
    headless=False,      # False면 브라우저 보임
    use_mobile=True,     # 모바일 모드 활성화
    device="galaxy_s24"  # 기기 선택
) as crawler:
    crawler.get_page("https://m.naver.com")
    # 모바일 페이지 크롤링 수행
```

#### URL 파라미터 사용 (선택사항)
```python
# 초기 URL을 파라미터로 저장 (나중에 접속)
with NaverCrawler(url="https://m.naver.com", use_mobile=True) as crawler:
    # 저장된 URL로 접속
    crawler.get_page(crawler.url)
    crawler.scroll_down(500)
    
    # 다른 페이지로도 자유롭게 이동
    crawler.get_page("https://m.daum.net")
    crawler.scroll_down(500)
```

#### 여러 사이트 크롤링
```python
urls = ["https://m.naver.com", "https://m.daum.net", "https://www.google.com"]

with NaverCrawler(use_mobile=True) as crawler:
    for url in urls:
        crawler.get_page(url)
        crawler.scroll_down(300)
        # 크롤링 작업
```

### 📱 지원 기기 목록

```python
# 안드로이드
- "galaxy_s24"      # Galaxy S24 Ultra (최신)
- "galaxy_s23"      # Galaxy S23

# iOS  
- "iphone_15_pro"   # iPhone 15 Pro (최신)
- "iphone_14"       # iPhone 14
```

### 🔧 데스크톱 모드로 사용

```python
# 기존 방식 (데스크톱)
with NaverCrawler(
    headless=False,
    use_mobile=False  # 모바일 모드 비활성화
) as crawler:
    crawler.get_page("https://www.naver.com")
```

### 💾 데이터 저장

```python
from src.utils import save_to_json, save_to_csv

data = [
    {"title": "제목1", "price": "10000원"},
    {"title": "제목2", "price": "20000원"}
]

save_to_json(data, "result.json")
save_to_csv(data, "result.csv")
```

### 🎨 여러 기기로 테스트

```python
devices = ["galaxy_s24", "iphone_15_pro"]

for device in devices:
    with NaverCrawler(headless=False, use_mobile=True, device=device) as crawler:
        crawler.get_page("https://m.naver.com")
        print(f"{device} 테스트 완료!")
```

## ⚙️ 설정

`config/config.json` 파일에서 다음을 설정할 수 있습니다:

- `driver_path`: 크롬드라이버 경로 (비워두면 자동으로 찾음)
- `headless`: 헤드리스 모드 사용 여부
- `wait_time`: 페이지 로드 대기 시간
- `timeout`: 요소 대기 최대 시간
- `user_agent`: 사용자 에이전트 문자열

## 🚀 주요 기능

### 🎭 완벽한 모바일 위장
- ✅ **실제 모바일 기기 에뮬레이션**: Galaxy S24, iPhone 15 Pro 등
- ✅ **User Agent 자동 매칭**: Chrome 버전 자동 감지 및 동기화
- ✅ **터치 이벤트 지원**: 5개 터치 포인트 에뮬레이션
- ✅ **플랫폼 위장**: Android/iOS 완벽 위장
- ✅ **Navigator 속성 덮어쓰기**: platform, mobile, connection 등
- ✅ **CDP (Chrome DevTools Protocol) 활용**: 저수준 설정
- ✅ **JavaScript 주입**: 자동화 감지 방지

### 🎯 고급 크롤링 동작 (NEW!)

#### Element 탐색 (6개 메서드)
- `find_element()` - 단일 요소 찾기
- `find_elements()` - 여러 요소 찾기
- `wait_for_element()` - 요소 대기 (타임아웃/조건 커스터마이징)
- `wait_for_element_clickable()` - 클릭 가능할 때까지 대기
- `wait_for_elements()` - 여러 요소 대기 (최소 개수 지정)
- `is_element_present()` - 요소 존재 여부 즉시 확인

#### 터치 동작 (7개 메서드)
- `touch_element()` - 자연스러운 터치 (랜덤 오프셋, 재시도)
- `touch_element_by_js()` - JavaScript 터치 (가려진 요소도 가능)
- `touch_at_coordinates()` - 특정 좌표 터치
- `double_touch()` - 더블 터치
- `long_touch()` - 롱터치 (길게 누르기)
- `random_corner_click()` - 무작위 구석 클릭 (팝업 닫기)
- `slow_typing()` - 사람처럼 천천히 텍스트 입력

#### 스크롤 동작 (12개 메서드)
- `scroll_down()` / `scroll_up()` - 기본 스크롤
- `scroll_to_top()` / `scroll_to_bottom()` - 최상단/최하단
- `scroll_to_element()` - 특정 요소까지 스크롤
- `scroll_element()` - 요소 내부 스크롤
- `dynamic_scroll()` - 동적 스크롤 (사람처럼 자연스럽게)
- `smooth_scroll_by()` - 부드러운 스크롤 (easing 적용)
- `swipe()` - 모바일 스와이프 제스처
- `infinite_scroll()` - 무한 스크롤 자동화
- `simulate_natural_reading()` - 자연스러운 읽기 시뮬레이션
- `get_scroll_position()` - 현재 스크롤 위치 확인

#### 유틸리티
- `extract_cid()` - URL에서 Content ID 추출

### 🛠️ 기타 기능
- ✅ Chrome WebDriver 자동 탐색
- ✅ Headless 모드 지원
- ✅ 로깅 기능 (파일 및 콘솔)
- ✅ JSON/CSV 데이터 저장
- ✅ 컨텍스트 매니저 지원
- ✅ 네이버 모바일/데스크톱 크롤링

## 💡 고급 사용 예제

### 자연스러운 스크롤링
```python
from src.crawler import NaverCrawler

with NaverCrawler(use_mobile=True, device="galaxy_s24") as crawler:
    crawler.get_page("https://m.naver.com")
    
    # 동적 스크롤 (사람처럼 자연스럽게)
    crawler.dynamic_scroll(distance=800)
    
    # 부드러운 스크롤 (easing 적용)
    crawler.smooth_scroll_by(500)
    
    # 자연스러운 읽기 시뮬레이션 (20~30초)
    crawler.simulate_natural_reading(min_read_time=20, max_read_time=30)
```

### 터치 인터랙션
```python
from selenium.webdriver.common.by import By

with NaverCrawler(use_mobile=True) as crawler:
    crawler.get_page("https://m.naver.com")
    
    # 검색창 터치 (재시도 및 랜덤 오프셋)
    crawler.touch_element(By.CSS_SELECTOR, "input.search_input")
    
    # 천천히 텍스트 입력
    search_box = crawler.find_element(By.CSS_SELECTOR, "input.search_input")
    crawler.slow_typing(search_box, "네이버 뉴스", min_delay=0.1, max_delay=0.3)
    
    # 무작위 구석 클릭 (팝업 닫기)
    crawler.random_corner_click()
```

### 스와이프 제스처
```python
with NaverCrawler(use_mobile=True) as crawler:
    crawler.get_page("https://m.naver.com")
    
    # 화면 높이 가져오기
    viewport_height = crawler.driver.execute_script("return window.innerHeight;")
    
    # 아래로 스와이프
    start_y = int(viewport_height * 0.8)
    end_y = int(viewport_height * 0.2)
    crawler.swipe(start_y, end_y, duration=0.4)
```

### 더 많은 예제
`examples/advanced_actions_example.py` 파일을 실행하면 모든 고급 기능을 테스트할 수 있습니다:

```bash
python examples/advanced_actions_example.py
```

## 🔍 모바일 에뮬레이션 검증

프로그램 실행 시 자동으로 다음 정보를 검증합니다:

```
=== 모바일 설정 검증 결과 ===
플랫폼: Android
User Agent: Mozilla/5.0 (Linux; Android 14; SM-S928N Build/UP1A.231005.007) ...
모바일 감지: True
터치 포인트: 5
화면 크기: 412x915
WebDriver: undefined (자동화 감지 방지됨)
Vendor: Google Inc.
```

### 직접 확인하는 방법

1. 프로그램 실행 후 User Agent 확인:
   - https://www.whatismybrowser.com/detect/what-is-my-user-agent

2. 모바일 감지 확인:
   - https://m.naver.com (모바일 페이지로 접속되는지 확인)

3. 터치 이벤트 확인:
   - 개발자 도구(F12) → Console에서: `navigator.maxTouchPoints`

## ⚙️ 설정 파일 (config.json)

프로젝트는 `config/config.json` 파일을 통해 중앙에서 설정을 관리합니다.

### 주요 설정 항목

```json
{
  "headless": false,          // 브라우저 창 표시 여부
  "wait_time": 3,             // 페이지 로드 대기 시간(초)
  "timeout": 10,              // 요소 찾기 타임아웃(초)
  "use_mobile": true,         // 모바일 에뮬레이션 사용
  "device": "galaxy_s24",     // 사용할 모바일 기기
  "use_debug_mode": true,     // Chrome 디버깅 모드 (VBA 원본 방식, 권장)
  "debug_port": 9222,         // 디버깅 포트 번호
  "profile_path": null        // 프로필 경로 (null이면 ~/ChromeTEMP)
}
```

**🔧 디버깅 모드 (VBA 원본 방식)**
- 자동화 감지 우회 ✅
- 로그인 세션 유지 ✅
- 안정적인 크롤링 ✅

자세한 내용: [Chrome 디버깅 모드 가이드](docs/CHROME_DEBUG_MODE.md)

### 사용 가능한 기기

- `galaxy_s24`: Galaxy S24 Ultra (Android 14)
- `galaxy_s23`: Galaxy S23 (Android 13)
- `iphone_15_pro`: iPhone 15 Pro (iOS 17.0)
- `iphone_14`: iPhone 14 (iOS 16.0)

### 설정 변경 예시

```python
# main.py를 실행하면 자동으로 config.json을 로드합니다
python main.py
```

**헤드리스 모드로 실행:**
```json
{
  "headless": true,  // 브라우저 창이 보이지 않음
  ...
}
```

**다른 기기로 변경:**
```json
{
  "device": "iphone_15_pro",  // iPhone으로 변경
  ...
}
```

**자세한 내용:** [설정 가이드](docs/CONFIG_USAGE.md)

## 🔧 문제 해결

### ChromeDriver 버전 불일치
- `webdriver-manager`를 사용하면 자동으로 버전을 관리합니다.
- 수동 설치 시 Chrome 버전과 ChromeDriver 버전이 일치해야 합니다.

### 인코딩 에러
- 모든 파일은 UTF-8 인코딩을 사용합니다.
- CSV 저장 시 `utf-8-sig` 인코딩을 사용하여 Excel에서도 정상 표시됩니다.

### 크롤링 실패
- 네이버 페이지 구조가 변경되었을 수 있습니다.
- 네트워크 연결 상태를 확인하세요.
- `config.json`에서 `wait_time`과 `timeout`을 늘려보세요.

### 설정이 적용되지 않을 때
- `config/config.json` 파일이 존재하는지 확인
- JSON 형식이 올바른지 확인 (쉼표, 따옴표)
- 프로그램 재시작

## ⚠️ 주의사항

1. **법적 책임**: 크롤링 시 네이버의 이용약관 및 robots.txt를 준수해야 합니다.
2. **요청 간격**: 서버에 부담을 주지 않도록 적절한 대기 시간을 설정하세요.
3. **개인정보**: 수집한 데이터의 개인정보 보호법 준수가 필요합니다.
4. **상업적 이용**: 상업적 목적으로 사용 시 네이버의 사전 허가가 필요할 수 있습니다.

## 📚 문서

자세한 사용법은 `docs/` 폴더의 문서를 참고하세요:

- [빠른 시작 가이드](docs/QUICKSTART.md)
- [설정 파일 사용 가이드](docs/CONFIG_USAGE.md) ⭐ **NEW**
- [Chrome 디버깅 모드 가이드](docs/CHROME_DEBUG_MODE.md) ⭐ **NEW**
- [모바일 에뮬레이션 가이드](docs/MOBILE_EMULATION_GUIDE.md)
- [고급 동작 가이드](docs/ADVANCED_ACTIONS.md)
- [URL 파라미터 가이드](docs/URL_PARAMETER_GUIDE.md)

## 📝 라이선스

이 프로젝트는 개인 학습 및 연구 목적으로 제작되었습니다.

---

**면책 조항**: 이 프로젝트는 교육 및 연구 목적으로만 사용되어야 합니다. 크롤링으로 인한 법적 책임은 사용자에게 있습니다.
