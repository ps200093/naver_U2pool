# 빠른 시작 가이드 ⚡

5분 안에 모바일 크롤러를 실행해보세요!

## 1단계: 설치 (2분)

### Windows PowerShell에서:

```powershell
# 1. 프로젝트 폴더로 이동
cd C:\Users\ps200\Desktop\coding\naver_U2pool

# 2. 가상환경 활성화
.\venv\Scripts\Activate.ps1

# 3. 패키지가 설치되어 있는지 확인
pip list
```

이미 설치되어 있다면 다음 단계로!

## 2단계: 첫 실행 (1분)

### 기본 테스트:

```powershell
python test_mobile.py
```

브라우저가 열리면서:
1. ✅ 네이버 모바일 접속
2. ✅ User Agent 확인
3. ✅ 모바일 뷰포트 확인

## 3단계: 실제 사용 (2분)

### 네이버 모바일 크롤링:

```python
from src.crawler import NaverCrawler

# Galaxy S24로 크롤링
with NaverCrawler(
    headless=False,
    use_mobile=True,
    device="galaxy_s24"
) as crawler:
    # 네이버 모바일 접속
    crawler.get_page("https://m.naver.com")
    
    # 여기에 크롤링 로직 추가
    print(f"페이지 제목: {crawler.driver.title}")
```

## 주요 명령어 치트시트 📝

### 기본 실행
```bash
# 메인 프로그램
python main.py

# 모바일 테스트
python test_mobile.py

# 간단한 예제
python examples/simple_example.py

# 고급 예제
python examples/advanced_example.py
```

### 기기 선택
```python
device="galaxy_s24"     # 갤럭시 S24 (권장)
device="galaxy_s23"     # 갤럭시 S23
device="iphone_15_pro"  # 아이폰 15 Pro
device="iphone_14"      # 아이폰 14
```

### 모드 선택
```python
headless=False  # 브라우저 보임 (디버깅용)
headless=True   # 백그라운드 실행 (빠름)
```

## 자주 묻는 질문 ❓

### Q: 브라우저가 안 열려요!
**A**: ChromeDriver 경로 확인
```bash
# 1. drivers 폴더에 chromedriver.exe가 있는지 확인
dir drivers\

# 2. 없다면 다운로드
# https://googlechromelabs.github.io/chrome-for-testing/
```

### Q: 모바일로 안 보여요!
**A**: 로그 확인
```python
# 콘솔 출력에서 다음을 확인:
# "=== 모바일 설정 검증 결과 ==="
# 모바일 감지: True  <- 이게 True여야 함
```

### Q: Headless 모드에서 오류가 나요!
**A**: 권한 문제일 수 있음
```python
# 일단 headless=False로 테스트
with NaverCrawler(headless=False, ...) as crawler:
    ...
```

## 다음 단계 🚀

### 1. 예제 실행해보기
```bash
python examples/simple_example.py
```
- 네이버 검색
- 쇼핑 둘러보기
- 여러 기기 비교

### 2. 고급 기능 사용
```bash
python examples/advanced_example.py
```
- Headless 크롤링
- 스크린샷 저장
- 쿠키 관리
- 페이지 정보 추출

### 3. 문서 읽어보기
- `docs/MOBILE_EMULATION_GUIDE.md` - 모바일 에뮬레이션 완벽 가이드
- `README.md` - 전체 프로젝트 문서

## 문제 해결 🔧

### 일반적인 오류

**1. ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**2. selenium.common.exceptions.WebDriverException**
```bash
# Chrome 브라우저 업데이트 필요
# Chrome 다운로드: https://www.google.com/chrome/
```

**3. 권한 오류 (PowerShell)**
```powershell
# PowerShell 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 도움이 필요하면? 💬

1. **로그 확인**: `logs/crawler.log` 파일 확인
2. **문서 확인**: `docs/` 폴더의 가이드 읽기
3. **예제 참고**: `examples/` 폴더의 코드 확인

## 주요 팁 💡

### 1. 자동화 감지 피하기
```python
# 실제 사용자처럼 행동
import time
import random

time.sleep(random.uniform(1, 3))  # 랜덤 대기
```

### 2. 여러 기기로 테스트
```python
devices = ["galaxy_s24", "iphone_15_pro"]
for device in devices:
    with NaverCrawler(..., device=device) as crawler:
        crawler.get_page("https://m.naver.com")
```

### 3. 스크린샷으로 확인
```python
crawler.driver.save_screenshot("screenshot.png")
```

## 성공적인 첫 실행! 🎉

축하합니다! 이제 완벽한 모바일 에뮬레이션으로 크롤링할 수 있습니다.

**다음 학습 추천:**
1. `examples/simple_example.py` 수정해서 실행
2. 네이버 쇼핑 검색 크롤러 만들기
3. 데이터를 JSON/CSV로 저장하기

---

**행운을 빕니다!** 🚀

