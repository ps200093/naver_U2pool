# 고급 크롤링 동작 가이드

`NaverCrawler` 클래스에 추가된 고급 크롤링 동작 메서드들에 대한 상세 가이드입니다.

## 📋 목차

1. [Element 탐색 메서드](#element-탐색-메서드)
2. [터치 동작 메서드](#터치-동작-메서드)
3. [스크롤 동작 메서드](#스크롤-동작-메서드)
4. [유틸리티 메서드](#유틸리티-메서드)
5. [실전 예제](#실전-예제)

---

## Element 탐색 메서드

### 1. `find_element(by, value)`
단일 요소를 찾습니다.

```python
from selenium.webdriver.common.by import By

element = crawler.find_element(By.CSS_SELECTOR, "input.search")
```

### 2. `find_elements(by, value)`
여러 요소를 찾아 리스트로 반환합니다.

```python
links = crawler.find_elements(By.TAG_NAME, "a")
print(f"총 {len(links)}개의 링크 발견")
```

### 3. `wait_for_element(by, value, timeout=None, condition=...)`
요소가 나타날 때까지 대기합니다. 고급 버전으로 조건과 타임아웃을 커스터마이징할 수 있습니다.

```python
# 기본 사용
element = crawler.wait_for_element(By.ID, "login-button")

# 타임아웃 지정
element = crawler.wait_for_element(By.CLASS_NAME, "content", timeout=20)

# 커스텀 조건
from selenium.webdriver.support import expected_conditions as EC
element = crawler.wait_for_element(
    By.ID, "button", 
    condition=EC.visibility_of_element_located
)
```

### 4. `wait_for_element_clickable(by, value, timeout=10)`
요소가 클릭 가능할 때까지 대기합니다.

```python
button = crawler.wait_for_element_clickable(By.ID, "submit-btn")
button.click()
```

### 5. `wait_for_elements(by, value, timeout=10, min_count=1)`
여러 요소가 나타날 때까지 대기하며, 최소 개수를 지정할 수 있습니다.

```python
# 최소 10개의 상품 카드가 나타날 때까지 대기
items = crawler.wait_for_elements(By.CLASS_NAME, "product-card", min_count=10)
```

### 6. `is_element_present(by, value)`
요소의 존재 여부를 즉시 확인합니다 (대기 없음).

```python
if crawler.is_element_present(By.ID, "popup"):
    print("팝업이 존재합니다")
```

---

## 터치 동작 메서드

### 1. `touch_element(by, value, wait_time=0.5, max_attempts=3)`
요소를 터치합니다. 랜덤 오프셋과 재시도 로직이 포함되어 사람처럼 자연스럽습니다.

```python
# 기본 사용
crawler.touch_element(By.CLASS_NAME, "button")

# 재시도 횟수 지정
crawler.touch_element(By.ID, "tricky-button", max_attempts=5)
```

**특징:**
- 랜덤 오프셋 (-5~5px) 적용
- 클릭 차단 시 자동 재시도
- 실패 시 구석 클릭 시도

### 2. `touch_element_by_js(by, value, wait_time=0.5)`
JavaScript를 사용한 터치. 가려진 요소도 클릭 가능합니다.

```python
# 다른 요소에 가려진 버튼 클릭
crawler.touch_element_by_js(By.CLASS_NAME, "hidden-button")
```

### 3. `touch_at_coordinates(x, y, wait_time=0.5)`
특정 좌표를 터치합니다.

```python
crawler.touch_at_coordinates(200, 300)
```

### 4. `double_touch(by, value, wait_time=0.5)`
더블 터치를 수행합니다.

```python
crawler.double_touch(By.CLASS_NAME, "zoom-target")
```

### 5. `long_touch(by, value, duration=1.0)`
롱터치(길게 누르기)를 수행합니다.

```python
crawler.long_touch(By.CLASS_NAME, "context-menu-trigger", duration=1.5)
```

### 6. `random_corner_click()`
화면 구석을 무작위로 클릭합니다. 팝업 닫기 등에 유용합니다.

```python
crawler.random_corner_click()
```

### 7. `slow_typing(element, text, min_delay=0.1, max_delay=0.5)`
사람처럼 천천히 텍스트를 입력합니다.

```python
search_box = crawler.find_element(By.ID, "search")
crawler.slow_typing(search_box, "검색어", min_delay=0.1, max_delay=0.3)
```

---

## 스크롤 동작 메서드

### 기본 스크롤

#### `scroll_down(amount=500, wait_time=0.5)`
```python
crawler.scroll_down(300)  # 300px 아래로
```

#### `scroll_up(amount=500, wait_time=0.5)`
```python
crawler.scroll_up(200)  # 200px 위로
```

#### `scroll_to_top(wait_time=0.5)`
```python
crawler.scroll_to_top()  # 최상단으로
```

#### `scroll_to_bottom(wait_time=0.5)`
```python
crawler.scroll_to_bottom()  # 최하단으로
```

### 고급 스크롤

#### `dynamic_scroll(target=None, distance=200, pause=None, step=None, is_blog=False)`
사람처럼 자연스럽게 스크롤합니다.

```python
# 거리 지정
crawler.dynamic_scroll(distance=800)

# 요소까지 스크롤
element = crawler.find_element(By.ID, "footer")
crawler.dynamic_scroll(target=element)

# 커스텀 설정
crawler.dynamic_scroll(distance=1000, pause=0.1, step=50)
```

**특징:**
- 랜덤 스텝 크기
- 진행률 추적 (20%마다 로그)
- 경계 도달 자동 감지

#### `smooth_scroll_by(total_scroll_distance, duration=None)`
easing 함수가 적용된 부드러운 스크롤입니다.

```python
# 500px 부드럽게 스크롤
crawler.smooth_scroll_by(500)

# 지속 시간 지정
crawler.smooth_scroll_by(800, duration=1.5)
```

**특징:**
- Ease-in-out 애니메이션
- 60fps로 부드럽게 실행
- 자동 지속 시간 계산

#### `swipe(start_y, end_y, duration=0.3)`
모바일 스와이프 제스처를 시뮬레이션합니다.

```python
viewport_height = crawler.driver.execute_script("return window.innerHeight;")

# 아래로 스와이프
start_y = int(viewport_height * 0.8)
end_y = int(viewport_height * 0.2)
crawler.swipe(start_y, end_y, duration=0.4)

# 위로 스와이프
crawler.swipe(end_y, start_y, duration=0.4)
```

**특징:**
- 실제 터치 이벤트 발생
- 터치 포인트 시뮬레이션
- 모바일 네이티브 동작과 동일

#### `scroll_to_element(by, value, wait_time=0.5)`
특정 요소까지 부드럽게 스크롤합니다.

```python
crawler.scroll_to_element(By.ID, "comments-section")
```

#### `scroll_element(by, value, amount=300, wait_time=0.5)`
특정 요소 내부를 스크롤합니다 (스크롤 가능한 div 등).

```python
crawler.scroll_element(By.CLASS_NAME, "scrollable-list", amount=500)
```

#### `infinite_scroll(max_scrolls=10, scroll_pause=1.0)`
무한 스크롤 페이지를 자동으로 로드합니다.

```python
# 최대 10회 또는 더 이상 새 콘텐츠가 없을 때까지
scroll_count = crawler.infinite_scroll(max_scrolls=10, scroll_pause=1.5)
print(f"총 {scroll_count}회 스크롤 완료")
```

**특징:**
- 페이지 높이 자동 감지
- 새 콘텐츠 없으면 자동 중단
- 실제 스크롤 횟수 반환

#### `simulate_natural_reading(min_read_time=25, max_read_time=50)`
사람이 글을 읽는 것처럼 자연스러운 스크롤 패턴을 시뮬레이션합니다.

```python
# 25~50초 동안 자연스럽게 읽기
crawler.simulate_natural_reading(min_read_time=25, max_read_time=50)

# 짧게 읽기
crawler.simulate_natural_reading(min_read_time=10, max_read_time=20)
```

**특징:**
- 랜덤 스크롤 다운/업
- 중간중간 일시 정지 (3~5초)
- 최하단/최상단 도달 시 반대 방향으로 이동
- 20% 확률로 위로 스크롤
- 진짜 사람처럼 동작

#### `scroll_to_feed_section(direction="down", scroll_amount=1000)`
피드 섹션을 스크롤합니다. 진행률을 추적합니다.

```python
# 아래로
crawler.scroll_to_feed_section(direction="down", scroll_amount=1000)

# 위로
crawler.scroll_to_feed_section(direction="up", scroll_amount=500)
```

#### `get_scroll_position()`
현재 스크롤 위치를 가져옵니다.

```python
position = crawler.get_scroll_position()
print(f"X: {position['x']}, Y: {position['y']}")
```

---

## 유틸리티 메서드

### `extract_cid(url)`
URL에서 Content ID (CID)를 추출합니다.

```python
url = "https://blog.naver.com/user/123456789"
cid = crawler.extract_cid(url)
print(f"CID: {cid}")  # 출력: CID: 123456789
```

**지원 패턴:**
- `/123456789/`
- `/123456789?param=value`
- `logNo=123456789`

---

## 실전 예제

### 예제 1: 네이버 블로그 자연스럽게 읽기

```python
from src.crawler import NaverCrawler
from selenium.webdriver.common.by import By

with NaverCrawler(use_mobile=True, device="galaxy_s24", headless=False) as crawler:
    # 블로그 포스트 접속
    crawler.get_page("https://m.blog.naver.com/...")
    
    # 초반 로딩 대기
    crawler.wait_for_element(By.CLASS_NAME, "se-main-container", timeout=10)
    
    # 자연스럽게 읽기 (30~60초)
    crawler.simulate_natural_reading(min_read_time=30, max_read_time=60)
    
    # 댓글 섹션으로 스크롤
    if crawler.is_element_present(By.CLASS_NAME, "u_cbox"):
        crawler.scroll_to_element(By.CLASS_NAME, "u_cbox")
```

### 예제 2: 검색 후 결과 탐색

```python
with NaverCrawler(use_mobile=True) as crawler:
    crawler.get_page("https://m.naver.com")
    
    # 검색창 찾아서 터치
    search_box = crawler.wait_for_element(By.CSS_SELECTOR, "input.search_input")
    crawler.touch_element(By.CSS_SELECTOR, "input.search_input")
    
    # 검색어 천천히 입력
    crawler.slow_typing(search_box, "파이썬 크롤링", min_delay=0.1, max_delay=0.3)
    
    # 검색 버튼 클릭
    crawler.touch_element(By.CLASS_NAME, "search_btn")
    
    # 결과 로딩 대기
    crawler.wait_for_elements(By.CLASS_NAME, "result_item", min_count=5)
    
    # 결과 스크롤하며 탐색
    crawler.dynamic_scroll(distance=1000)
```

### 예제 3: 무한 스크롤 피드 수집

```python
with NaverCrawler(use_mobile=True) as crawler:
    crawler.get_page("https://m.naver.com/...")
    
    # 무한 스크롤로 더 많은 콘텐츠 로드
    scroll_count = crawler.infinite_scroll(max_scrolls=20, scroll_pause=2.0)
    
    # 모든 아이템 수집
    items = crawler.find_elements(By.CLASS_NAME, "feed-item")
    print(f"{len(items)}개의 아이템 발견 (총 {scroll_count}회 스크롤)")
    
    # 데이터 추출
    data = []
    for item in items:
        title = item.find_element(By.CLASS_NAME, "title").text
        data.append({"title": title})
```

### 예제 4: 팝업 처리 및 인터랙션

```python
with NaverCrawler(use_mobile=True) as crawler:
    crawler.get_page("https://m.naver.com")
    
    # 팝업이 있으면 구석 클릭으로 닫기
    if crawler.is_element_present(By.CLASS_NAME, "popup"):
        crawler.random_corner_click()
        time.sleep(1)
    
    # 여러 시도가 필요한 버튼 클릭
    success = crawler.touch_element(
        By.CLASS_NAME, "tricky-button", 
        max_attempts=5
    )
    
    if not success:
        # JavaScript로 강제 클릭
        crawler.touch_element_by_js(By.CLASS_NAME, "tricky-button")
```

### 예제 5: 모바일 스와이프로 캐러셀 탐색

```python
with NaverCrawler(use_mobile=True) as crawler:
    crawler.get_page("https://m.naver.com")
    
    viewport_height = crawler.driver.execute_script("return window.innerHeight;")
    
    # 5번 스와이프 (다음 항목 보기)
    for i in range(5):
        start_y = int(viewport_height * 0.5)
        end_y = int(viewport_height * 0.3)
        crawler.swipe(start_y, end_y, duration=0.3)
        time.sleep(1)
        
        # 현재 항목 데이터 수집
        title = crawler.find_element(By.CLASS_NAME, "title").text
        print(f"항목 {i+1}: {title}")
```

---

## 🎯 베스트 프랙티스

### 1. 자연스러운 동작 조합
```python
# 좋은 예: 여러 자연스러운 동작 조합
crawler.touch_element(By.ID, "button")
time.sleep(random.uniform(1, 2))
crawler.dynamic_scroll(distance=500)
time.sleep(random.uniform(0.5, 1.5))
crawler.simulate_natural_reading(20, 30)
```

### 2. 에러 처리
```python
# 요소 존재 확인 후 동작
if crawler.is_element_present(By.ID, "target"):
    crawler.touch_element(By.ID, "target")
else:
    print("요소를 찾을 수 없습니다")
```

### 3. 재시도 로직 활용
```python
# touch_element는 이미 재시도 로직이 내장되어 있음
success = crawler.touch_element(By.CLASS_NAME, "btn", max_attempts=5)
if not success:
    # 대체 방법 시도
    crawler.touch_element_by_js(By.CLASS_NAME, "btn")
```

### 4. 적절한 대기 시간
```python
# 너무 빠르지 않게
crawler.touch_element(By.ID, "btn1")
time.sleep(random.uniform(1, 2))  # 1~2초 랜덤 대기
crawler.touch_element(By.ID, "btn2")
```

---

## 📊 메서드 참조 표

| 카테고리 | 메서드 | 용도 | 난이도 |
|---------|--------|------|--------|
| 탐색 | `find_element()` | 요소 찾기 | ⭐ |
| 탐색 | `wait_for_element()` | 요소 대기 | ⭐ |
| 탐색 | `is_element_present()` | 존재 확인 | ⭐ |
| 터치 | `touch_element()` | 기본 터치 | ⭐ |
| 터치 | `slow_typing()` | 텍스트 입력 | ⭐ |
| 터치 | `random_corner_click()` | 팝업 처리 | ⭐⭐ |
| 스크롤 | `scroll_down()` | 기본 스크롤 | ⭐ |
| 스크롤 | `dynamic_scroll()` | 자연스러운 스크롤 | ⭐⭐ |
| 스크롤 | `smooth_scroll_by()` | 부드러운 스크롤 | ⭐⭐ |
| 스크롤 | `swipe()` | 모바일 스와이프 | ⭐⭐⭐ |
| 스크롤 | `simulate_natural_reading()` | 읽기 시뮬레이션 | ⭐⭐⭐ |
| 스크롤 | `infinite_scroll()` | 무한 스크롤 | ⭐⭐ |

---

## 🔗 관련 문서

- [QUICKSTART.md](./QUICKSTART.md) - 빠른 시작 가이드
- [MOBILE_EMULATION_GUIDE.md](./MOBILE_EMULATION_GUIDE.md) - 모바일 에뮬레이션 가이드
- [examples/advanced_actions_example.py](../examples/advanced_actions_example.py) - 실행 가능한 예제

---

**업데이트:** 2025-11-18  
**버전:** 1.0.0

