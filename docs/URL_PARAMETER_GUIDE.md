# URL 파라미터 사용 가이드

`NaverCrawler`의 `url` 파라미터 사용법을 설명합니다.

## 📋 개요

`url` 파라미터는 **선택사항**이며, 초기 URL을 저장하는 용도로 사용됩니다.  
실제 페이지 접속은 `get_page()` 메서드로 수동으로 수행합니다.

## 🎯 사용 방법

### 1. URL 파라미터 없이 사용 (기본)

```python
from src.crawler import NaverCrawler

with NaverCrawler(use_mobile=True) as crawler:
    # 원하는 페이지로 접속
    crawler.get_page("https://m.naver.com")
    crawler.scroll_down(500)
    
    # 다른 페이지로 이동
    crawler.get_page("https://m.daum.net")
    crawler.scroll_down(500)
```

### 2. URL 파라미터와 함께 사용

```python
from src.crawler import NaverCrawler

# 초기 URL을 파라미터로 전달 (저장만 됨, 접속은 안됨)
with NaverCrawler(url="https://m.naver.com", use_mobile=True) as crawler:
    # 저장된 URL로 접속
    crawler.get_page(crawler.url)
    crawler.scroll_down(500)
    
    # 다른 페이지도 자유롭게 접속
    crawler.get_page("https://m.daum.net")
```

### 3. 여러 사이트 순회

```python
# URL 리스트
urls = [
    "https://m.naver.com",
    "https://m.daum.net",
    "https://www.google.com"
]

with NaverCrawler(use_mobile=True) as crawler:
    for url in urls:
        print(f"접속: {url}")
        crawler.get_page(url)
        crawler.dynamic_scroll(distance=800)
        time.sleep(2)
```

## 💡 왜 이렇게 설계했나요?

### 장점

1. **유연성**: 하나의 크롤러로 여러 사이트를 자유롭게 방문
2. **효율성**: 드라이버를 한 번만 생성하고 재사용
3. **명확성**: 언제 페이지에 접속하는지 명확하게 제어

### 사용 시나리오

#### ✅ 좋은 사용 예

```python
# 여러 블로그 글 크롤링
blog_urls = [
    "https://m.blog.naver.com/user1/123",
    "https://m.blog.naver.com/user2/456",
    "https://m.blog.naver.com/user3/789",
]

with NaverCrawler(use_mobile=True) as crawler:
    for url in blog_urls:
        crawler.get_page(url)
        # 자연스럽게 읽기
        crawler.simulate_natural_reading(20, 40)
```

#### ✅ 초기 URL 활용

```python
# 메인 URL을 기억해두고 필요할 때 돌아가기
with NaverCrawler(url="https://m.naver.com") as crawler:
    # 메인으로 시작
    crawler.get_page(crawler.url)
    
    # 검색 결과로 이동
    crawler.get_page("https://m.naver.com/search?query=...")
    
    # 다시 메인으로
    crawler.get_page(crawler.url)  # 저장된 URL 재사용
```

## 📚 실전 예제

### 예제 1: 카테고리별 크롤링

```python
categories = {
    "뉴스": "https://m.news.naver.com",
    "쇼핑": "https://shopping.naver.com",
    "블로그": "https://section.blog.naver.com",
}

with NaverCrawler(use_mobile=True, device="galaxy_s24") as crawler:
    for name, url in categories.items():
        print(f"[{name}] 크롤링 중...")
        crawler.get_page(url)
        
        # 스크롤하며 데이터 수집
        crawler.infinite_scroll(max_scrolls=5)
        
        # 데이터 수집 로직
        items = crawler.find_elements(By.CLASS_NAME, "item")
        print(f"[{name}] {len(items)}개 아이템 발견")
```

### 예제 2: 검색 키워드별 크롤링

```python
keywords = ["파이썬", "크롤링", "셀레니움"]

with NaverCrawler(url="https://m.naver.com", use_mobile=True) as crawler:
    for keyword in keywords:
        # 메인으로 돌아가기
        crawler.get_page(crawler.url)
        time.sleep(1)
        
        # 검색
        search_box = crawler.find_element(By.CSS_SELECTOR, "input.search_input")
        search_box.clear()
        crawler.slow_typing(search_box, keyword)
        time.sleep(2)
        
        # 결과 수집
        # ...
```

### 예제 3: 파일에서 URL 목록 읽기

```python
# urls.txt 파일 내용:
# https://m.naver.com
# https://m.daum.net
# https://www.google.com

with open('urls.txt', 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

with NaverCrawler(use_mobile=True) as crawler:
    results = []
    
    for url in urls:
        try:
            crawler.get_page(url)
            title = crawler.driver.title
            
            results.append({
                "url": url,
                "title": title,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "url": url,
                "status": "failed",
                "error": str(e)
            })
    
    # 결과 저장
    from src.utils import save_to_json
    save_to_json(results, "crawl_results.json")
```

### 예제 4: 조건부 페이지 이동

```python
with NaverCrawler(url="https://m.naver.com", use_mobile=True) as crawler:
    # 메인 페이지
    crawler.get_page(crawler.url)
    
    # 조건에 따라 다른 페이지로 이동
    if crawler.is_element_present(By.CLASS_NAME, "news_area"):
        print("뉴스 영역 발견 → 뉴스 페이지로")
        crawler.get_page("https://m.news.naver.com")
    elif crawler.is_element_present(By.CLASS_NAME, "shopping_area"):
        print("쇼핑 영역 발견 → 쇼핑 페이지로")
        crawler.get_page("https://shopping.naver.com")
    else:
        print("기본 블로그로")
        crawler.get_page("https://section.blog.naver.com")
```

## 🔄 기존 코드와의 비교

### 변경 전 (기존)
```python
with NaverCrawler(use_mobile=True) as crawler:
    crawler.get_page("https://m.naver.com")
    # 크롤링
```

### 변경 후 (URL 파라미터 추가)
```python
# 방법 1: 그대로 사용 (변경 없음)
with NaverCrawler(use_mobile=True) as crawler:
    crawler.get_page("https://m.naver.com")
    # 크롤링

# 방법 2: URL 파라미터 활용 (선택사항)
with NaverCrawler(url="https://m.naver.com", use_mobile=True) as crawler:
    crawler.get_page(crawler.url)  # 저장된 URL 사용
    # 크롤링
```

**→ 기존 코드는 그대로 동작합니다!**

## 📌 주요 포인트

1. **`url` 파라미터는 선택사항**: 없어도 정상 작동
2. **자동 접속 안됨**: `get_page()`로 명시적으로 접속해야 함
3. **여러 페이지 접속 가능**: 하나의 크롤러로 여러 사이트 방문
4. **기존 코드 호환**: 기존 방식 그대로 사용 가능

## 🎓 더 알아보기

- [examples/multiple_sites_example.py](../examples/multiple_sites_example.py) - 실행 가능한 예제
- [ADVANCED_ACTIONS.md](./ADVANCED_ACTIONS.md) - 고급 크롤링 동작
- [README.md](../README.md) - 전체 문서

---

**업데이트:** 2025-11-18  
**버전:** 1.1.0

