# Simple URL Visitor - 사용법

간단한 URL 반복 방문 도구 (NordVPN IP 변경 지원)

## 📋 개요

- **단일 URL** 반복 접속
- **NordVPN API** 연동 (IP 자동 변경)
- **랜덤 대기 시간** (자연스러운 방문 패턴)
- **간단한 설정**

## 🚀 빠른 시작

### 1. 기본 실행 (NordVPN 없이)

```bash
python simple_visitor.py --url "https://brand.naver.com/sennheiserstore/products/12534300529" --repeat 10
```

### 2. NordVPN 사용

```bash
python simple_visitor.py \
  --url "https://brand.naver.com/sennheiserstore/products/12534300529" \
  --repeat 10 \
  --nordvpn \
  --username YOUR_USERNAME \
  --password YOUR_PASSWORD
```

### 3. 설정 파일로 실행

`simple_config.json` 수정 후:

```bash
python simple_visitor_config.py
```

## 📝 명령어 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--url` | 방문할 URL (필수) | - |
| `--repeat`, `-r` | 반복 횟수 | 10 |
| `--wait-min` | 최소 대기 시간 (초) | 3 |
| `--wait-max` | 최대 대기 시간 (초) | 10 |
| `--rest` | 사이클 간 휴식 (분) | 0 |
| `--headless` | 헤드리스 모드 | False |
| `--no-guest` | 게스트 모드 비활성화 | False (게스트 모드 기본) |
| `--nordvpn` | NordVPN 사용 | False |
| `--username` | NordVPN 계정 | - |
| `--password` | NordVPN 비밀번호 | - |
| `--countries` | 국가 코드 (쉼표 구분, 예: KR,JP,US) | 모든 국가 |

## 💡 사용 예시

### 예시 1: 헤드리스 모드로 20회 방문

```bash
python simple_visitor.py \
  --url "https://example.com" \
  --repeat 20 \
  --headless
```

### 예시 2: 대기 시간 5~15초로 설정

```bash
python simple_visitor.py \
  --url "https://example.com" \
  --repeat 10 \
  --wait-min 5 \
  --wait-max 15
```

### 예시 3: 10회 방문, 각 사이클마다 2분 휴식

```bash
python simple_visitor.py \
  --url "https://example.com" \
  --repeat 10 \
  --rest 2
```

### 예시 4: 모든 옵션 조합 (한국 서버만)

```bash
python simple_visitor.py \
  --url "https://brand.naver.com/sennheiserstore/products/12534300529" \
  --repeat 50 \
  --wait-min 5 \
  --wait-max 20 \
  --rest 1 \
  --nordvpn \
  --username your_username \
  --password your_password \
  --countries KR
```

### 예시 5: 여러 국가 지정 (한국, 일본, 미국)

```bash
python simple_visitor.py \
  --url "https://example.com" \
  --repeat 20 \
  --nordvpn \
  --username your_username \
  --password your_password \
  --countries KR,JP,US
```

### 예시 6: 게스트 모드 비활성화

```bash
python simple_visitor.py \
  --url "https://example.com" \
  --repeat 10 \
  --no-guest
```

## 🔧 NordVPN 설정

### 방법 1: NordVPN API 사용 (자동)

스크립트가 자동으로 NordVPN 서버 목록을 가져옵니다:
- https://api.nordvpn.com/v1/servers
- 프록시 지원 서버만 선택
- 각 방문마다 랜덤 서버 선택

**필요한 것:**
- NordVPN 계정 (username/password)

**장점:**
- 자동으로 서버 목록 업데이트
- 다양한 국가 서버 자동 선택
- 간편한 설정

### 방법 2: 프록시 리스트 사용 (수동)

별도의 프록시 서버 목록을 사용하려면 코드 수정 필요.

## 📊 실행 로그 예시

```
======================================================================
[CONFIG] 설정 정보
======================================================================
  - URL: https://smartstore.naver.com/samhyeongzefish
  - 반복 횟수: 500
  - 대기 시간: 3~10초
  - 휴식 시간: 0분
  - 헤드리스: False
  - 게스트 모드: True  ← 게스트 모드!
  - NordVPN: True
  - NordVPN 계정: TwmEbYfELnwjnFKC7fvBbRAg
  - 타겟 국가: KR
======================================================================

[API] NordVPN 서버 목록 가져오는 중... (국가: KR, 최대 100개)
[OK] 12개 서버 로드 완료 (HTTPS 프록시)
[INFO] 국가별 분포: South Korea: 12개

======================================================================
[CYCLE] 1/500
======================================================================
[VPN] 서버 변경: South Korea
[GUEST] 게스트 모드 활성화  ← 게스트 모드 확인!
[PROXY] HTTPS kr1234.nordvpn.com:89 (South Korea) (KR) [인증 적용]
[OK] 드라이버 생성 완료
[VISIT] https://smartstore.naver.com/samhyeongzefish
[WAIT] 7.3초 대기 중...
[OK] 방문 완료
[OK] 드라이버 종료 완료

======================================================================
[CYCLE] 2/500
======================================================================
[VPN] 서버 변경: South Korea
[PROXY] HTTPS kr5678.nordvpn.com:89 (South Korea) (KR) [인증 적용]
...

======================================================================
[DONE] 완료!
======================================================================
  - 성공: 500
  - 실패: 0
  - 성공률: 100.0%
======================================================================
```

## ⚙️ 설정 파일 (simple_config.json)

```json
{
  "url": "https://example.com",
  "repeat_count": 10,
  "wait_min": 3,
  "wait_max": 10,
  "rest_minutes": 0,
  "headless": false,
  "guest_mode": true,
  "use_nordvpn": true,
  "nordvpn_username": "your_username",
  "nordvpn_password": "your_password",
  "target_countries": ["KR"]
}
```

### 게스트 모드 (기본: 활성화)

Chrome을 게스트 모드로 실행합니다:
- ✅ **활성화 (권장)**: `"guest_mode": true`
- ❌ **비활성화**: `"guest_mode": false`

**장점:**
- 로그인 정보 저장 안 됨
- 브라우저 히스토리 남지 않음
- 깨끗한 세션

### 국가 설정 옵션

#### 한국만 사용:
```json
"target_countries": ["KR"]
```

#### 여러 국가 사용:
```json
"target_countries": ["KR", "JP", "US"]
```

#### 모든 국가 사용:
```json
"target_countries": null
```

설정 파일 수정 후:

```bash
python simple_visitor_config.py
```

### 주요 국가 코드

| 코드 | 국가 |
|------|------|
| `KR` | 한국 🇰🇷 |
| `JP` | 일본 🇯🇵 |
| `US` | 미국 🇺🇸 |
| `GB` | 영국 🇬🇧 |
| `DE` | 독일 🇩🇪 |
| `FR` | 프랑스 🇫🇷 |
| `CA` | 캐나다 🇨🇦 |
| `AU` | 호주 🇦🇺 |
| `SG` | 싱가포르 🇸🇬 |
| `TW` | 대만 🇹🇼 |

### ⚠️ 자동 폴백 (Fallback)

지정한 국가의 서버가 없으면 **자동으로 모든 국가 서버**를 사용합니다.

예시:
```
[API] NordVPN 서버 목록 가져오는 중... (국가: KR, 최대 100개)
[WARNING] 타겟 국가(KR) 서버를 찾을 수 없습니다.
[FALLBACK] 모든 국가 서버로 재시도 중...
[OK] 폴백 성공: 50개 서버 로드 (모든 국가)
[INFO] 국가별 분포: United States: 20개, United Kingdom: 15개, Germany: 15개
```

## 🎯 동작 흐름

1. **NordVPN 서버 로드** (use_nordvpn=true인 경우)
   - 타겟 국가 서버 검색 (예: KR)
   - 서버가 없으면 **자동으로 모든 국가 재시도** ✅
2. **반복 시작**
3. 각 사이클마다:
   - 랜덤 NordVPN 서버 선택
   - 새 Chrome 드라이버 생성 (프록시 적용)
   - URL 접속
   - 랜덤 대기 시간 (wait_min ~ wait_max)
   - 드라이버 종료
4. **통계 출력**

## 🔍 NordVPN 없이 사용하는 경우

NordVPN 옵션을 빼면 일반 방문만 수행합니다:

```bash
python simple_visitor.py --url "https://example.com" --repeat 10
```

- IP 변경 없음
- 단순 반복 방문
- 로컬 IP 사용

## ⚠️ 주의사항

1. **NordVPN 계정 필요**: `--nordvpn` 옵션 사용 시 유효한 NordVPN 계정 필요
2. **프록시 인증**: 일부 NordVPN 서버는 추가 인증 필요
3. **속도**: 프록시 사용 시 접속 속도가 느려질 수 있음
4. **법적 책임**: 웹사이트 이용약관 준수 필요

## 🔧 문제 해결

### NordVPN 연결 실패

```
[ERROR] 프록시 연결 실패
```

**해결 방법:**
1. NordVPN 계정 확인
2. 프록시 인증 정보 확인
3. `--nordvpn` 없이 테스트

### 드라이버 생성 실패

```
[ERROR] 드라이버 생성 실패
```

**해결 방법:**
1. Chrome 브라우저 설치 확인
2. ChromeDriver 버전 확인
3. 관리자 권한으로 실행

## 📦 필요한 패키지

```bash
pip install selenium requests
```

---

**간단하고 빠르게 URL을 반복 방문하세요!** 🚀
