# 모바일 에뮬레이션 완벽 가이드

## 📱 모바일 에뮬레이션이란?

모바일 에뮬레이션은 데스크톱 브라우저에서 실제 모바일 기기처럼 동작하도록 만드는 기술입니다.
이 프로젝트는 완벽한 모바일 위장을 위해 다음 기술들을 활용합니다:

## 🎯 핵심 기술

### 1. User Agent 설정
```python
# 실제 Galaxy S24 User Agent
"Mozilla/5.0 (Linux; Android 14; SM-S928N Build/UP1A.231005.007) 
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.109 Mobile Safari/537.36"
```

### 2. 모바일 메트릭 설정
- **화면 크기**: 412x915 (Galaxy S24)
- **픽셀 비율**: 3.5
- **터치 포인트**: 5개
- **모바일 플래그**: True

### 3. CDP (Chrome DevTools Protocol)

CDP를 통해 저수준에서 브라우저를 제어합니다:

```python
# Navigator 오버라이드
driver.execute_cdp_cmd('Emulation.setNavigatorOverrides', {
    'platform': 'Android',
    'userAgent': user_agent,
    'acceptLanguage': 'ko-KR,ko'
})

# 터치 에뮬레이션
driver.execute_cdp_cmd('Emulation.setTouchEmulationEnabled', {
    'enabled': True,
    'maxTouchPoints': 5,
    'configuration': 'mobile'
})

# 디바이스 메트릭
driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
    'mobile': True,
    'width': 412,
    'height': 915,
    'deviceScaleFactor': 3.5,
    'screenOrientation': {
        'angle': 0,
        'type': 'portraitPrimary'
    }
})
```

### 4. JavaScript 주입

자동화 감지를 방지하고 모바일 속성을 완벽하게 위장:

```javascript
// Navigator 프록시
const navigatorProxy = new Proxy(originalNavigator, {
    get: function(target, prop) {
        switch (prop) {
            case 'platform':
                return 'Android';
            case 'maxTouchPoints':
                return 5;
            case 'webdriver':
                return undefined;  // 자동화 감지 방지
            // ... 더 많은 속성
        }
    }
});

// 터치 이벤트 지원
window.ontouchstart = null;
window.ontouchmove = null;
window.ontouchend = null;

// matchMedia 모바일 지원
window.matchMedia = function(query) {
    if (query.includes('hover')) {
        return { matches: false };  // 모바일은 hover 없음
    }
    if (query.includes('pointer') && query.includes('coarse')) {
        return { matches: true };  // 모바일은 coarse pointer
    }
    return originalMatchMedia(query);
};
```

## 🔍 검증 방법

### 자동 검증

프로그램이 자동으로 다음을 확인합니다:

```python
verification_script = """
return {
    platform: navigator.platform,
    userAgent: navigator.userAgent,
    mobile: /Android|iPhone|iPad|iPod/i.test(navigator.userAgent),
    touchPoints: navigator.maxTouchPoints,
    width: window.screen.width,
    height: window.screen.height,
    webdriver: navigator.webdriver,
    vendor: navigator.vendor
};
"""
```

### 수동 검증 사이트

1. **User Agent 확인**
   - https://www.whatismybrowser.com/detect/what-is-my-user-agent
   - 실제 모바일 User Agent가 표시되어야 함

2. **모바일 감지 확인**
   - https://m.naver.com
   - 모바일 버전으로 리다이렉트되어야 함

3. **터치 이벤트 확인**
   - F12 → Console: `navigator.maxTouchPoints`
   - 결과: 5 (모바일 기기는 보통 5개 이상)

4. **플랫폼 확인**
   - F12 → Console: `navigator.platform`
   - 안드로이드: "Android" 또는 "Linux armv8l"
   - iOS: "iPhone" 또는 "iPad"

5. **WebDriver 감지 확인**
   - F12 → Console: `navigator.webdriver`
   - 결과: undefined (자동화 감지 방지)

## 📊 지원 기기

### Android 기기

#### Galaxy S24 Ultra
```python
{
    "width": 412,
    "height": 915,
    "pixel_ratio": 3.5,
    "platform_version": "14",
    "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-S928N...)"
}
```

#### Galaxy S23
```python
{
    "width": 360,
    "height": 800,
    "pixel_ratio": 3.0,
    "platform_version": "13",
    "user_agent": "Mozilla/5.0 (Linux; Android 13; SM-S911N...)"
}
```

### iOS 기기

#### iPhone 15 Pro
```python
{
    "width": 393,
    "height": 852,
    "pixel_ratio": 3.0,
    "platform_version": "17.0",
    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0...)"
}
```

#### iPhone 14
```python
{
    "width": 390,
    "height": 844,
    "pixel_ratio": 3.0,
    "platform_version": "16.0",
    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0...)"
}
```

## 🚀 고급 기능

### 커스텀 기기 추가

`src/mobile_driver.py`의 `DEVICES` 딕셔너리에 추가:

```python
DEVICES = {
    "custom_device": {
        "user_agent": "Your User Agent String",
        "width": 360,
        "height": 800,
        "pixel_ratio": 2.0,
        "platform_version": "13",
        "architecture": "arm",
        "device_model": "CustomDevice"
    }
}
```

### Headless 모드에서의 완벽한 에뮬레이션

Headless 모드에서도 모든 모바일 속성이 유지됩니다:

```python
mobile = MobileDriver(
    headless=True,  # 백그라운드 실행
    device="galaxy_s24"
)
driver = mobile.create_driver()
```

## ⚠️ 주의사항

### 1. Chrome 버전 동기화

프로그램이 자동으로 Chrome 버전을 감지하여 User Agent를 업데이트합니다:

```python
# Chrome/131.0.6778.109 → 실제 설치된 Chrome 버전으로 자동 교체
```

### 2. WebRTC IP 유출 방지

설정에 포함된 WebRTC 차단:

```python
prefs = {
    'webrtc.ip_handling_policy': 'disable_non_proxied_udp',
    'webrtc.multiple_routes_enabled': False,
    'webrtc.nonproxied_udp_enabled': False
}
```

### 3. 자동화 감지 방지

다음 속성들이 자동으로 처리됩니다:
- `navigator.webdriver` → undefined
- `window.chrome` → 제거
- Automation 플래그 → 비활성화

## 🔧 문제 해결

### 모바일로 감지되지 않는 경우

1. **검증 확인**: 로그에서 검증 결과 확인
2. **플랫폼 확인**: `navigator.platform`이 올바른지 확인
3. **User Agent 확인**: Chrome 버전이 매칭되는지 확인

### Headless 모드에서 오류 발생

일부 사이트는 Headless를 감지할 수 있습니다:

```python
# 추가 옵션 설정
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
```

### 사이트별 대응

특정 사이트가 여전히 감지한다면:

1. **User Agent 변경**: 다른 기기 프리셋 사용
2. **대기 시간 추가**: 자연스러운 사용자 행동 모방
3. **랜덤 딜레이**: 요청 간 랜덤 대기

```python
import random
import time

# 랜덤 대기 (1-3초)
time.sleep(random.uniform(1, 3))
```

## 📚 참고 자료

### CDP 문서
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Emulation Domain](https://chromedevtools.github.io/devtools-protocol/tot/Emulation/)

### Selenium 문서
- [Selenium Python Docs](https://selenium-python.readthedocs.io/)
- [Chrome Options](https://www.selenium.dev/documentation/webdriver/browsers/chrome/)

### User Agent 정보
- [User Agent String](https://www.useragentstring.com/)
- [WhatIsMyBrowser](https://www.whatismybrowser.com/)

## 💡 팁

### 1. 실제 기기처럼 행동하기

```python
from selenium.webdriver.common.action_chains import ActionChains
import time

# 스크롤 시뮬레이션
for _ in range(3):
    driver.execute_script("window.scrollBy(0, 300);")
    time.sleep(0.5)

# 터치 제스처 시뮬레이션
actions = ActionChains(driver)
actions.move_by_offset(100, 200).perform()
```

### 2. 네트워크 조건 설정

```python
# 모바일 네트워크 시뮬레이션 (4G)
driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
    'offline': False,
    'downloadThroughput': 10 * 1024 * 1024 / 8,  # 10Mbps
    'uploadThroughput': 5 * 1024 * 1024 / 8,     # 5Mbps
    'latency': 50  # 50ms
})
```

### 3. 위치 정보 설정

```python
# 서울 좌표
driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
    'latitude': 37.5665,
    'longitude': 126.9780,
    'accuracy': 100
})
```

## 🎓 학습 예제

예제 코드는 `examples/` 폴더에서 확인하세요:

- `simple_example.py`: 기본 사용법
- `advanced_example.py`: 고급 기능

---

**만든이**: naver_U2pool 프로젝트  
**최종 업데이트**: 2025-11-18

