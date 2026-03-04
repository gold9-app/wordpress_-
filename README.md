# WordPress 자동 발행 시스템 with Elementor

항노화 김응석 박사의 건강 칼럼을 자동으로 생성하고, Elementor 프로급 디자인으로 WordPress에 발행하는 완전 자동화 시스템입니다.

---

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [주요 기능](#주요-기능)
3. [설정 방법](#설정-방법)
4. [배포 워크플로우](#배포-워크플로우)
5. [환경 변수](#환경-변수)
6. [사용 방법](#사용-방법)
7. [문제 해결](#문제-해결)

---

## 🎯 시스템 개요

### 구조
```
GitHub (gold9-app)
    ↓ Push
    ↓
GitHub (thenext0202) ← Fork
    ↓ Sync Fork
    ↓
Railway (자동 배포)
    ↓
웹 UI (https://xxx.up.railway.app)
    ↓
WordPress (blog.meditial.co.kr)
    ↓
Elementor 프로급 디자인 자동 적용
```

### 기술 스택
- **Backend**: Flask (Python)
- **AI**: Claude Sonnet 4.5 (글 생성)
- **CMS**: WordPress REST API
- **SEO**: Rank Math
- **Design**: Elementor (자동 레이아웃)
- **Deploy**: Railway (GitHub 연동)

---

## ✨ 주요 기능

### 1. AI 글 자동 생성 (조건부 커스텀 지침)
- **Claude API**로 1000-1500 단어 칼럼 생성
- **조건부 지침 시스템**:
  - 응석 김(ID: 4) + 건강 칼럼(ID: 22): 의료 전문가 톤 자동 적용
  - 다른 작성자/카테고리: **커스텀 지침 입력 가능**
- 제목 자동 추출 및 입력
- HTML 미리보기 (렌더링/소스)
- 다운로드 기능

### 2. Elementor 프로급 디자인 자동 적용
- 그라디언트 헤더 섹션
- 스타일 적용된 본문
- CTA 섹션 (저자 소개 + 인스타그램 버튼)
- 모바일 반응형

### 3. SEO 완벽 최적화 (Rank Math)
- Focus Keyword 자동 추출
- 메타 설명 생성
- 슬러그 최적화
- 이미지 alt 텍스트
- Article 스키마

---

## 🔧 설정 방법

### 1. 로컬 환경 설정

#### 필수 파일
```bash
.env                    # 환경 변수
config.json            # WordPress 설정
requirements.txt       # Python 패키지
```

#### Python 패키지 설치
```bash
pip install -r requirements.txt
```

#### .env 파일 생성
```env
WP_URL=https://blog.meditial.co.kr
WP_USERNAME=mincompanyad
WP_APP_PASSWORD=RzRh mJOi Q8kY 9hpR sarb rOD4
APP_PASSWORD=test1234
USE_ELEMENTOR=true
ELEMENTOR_METHOD=simple
CLAUDE_API_KEY=sk-ant-api03-xxxxx...
```

### 2. Railway 배포 설정

#### ⚠️ 중요: GitHub 저장소 구조
```
원본 저장소:  gold9-app/wordpress_-       (개발용)
              ↓ Fork
배포 저장소:  thenext0202/wordpress_-     (Railway 연결)
```

#### Railway 프로젝트 설정

**Settings → Source:**
```
Repository: thenext0202/wordpress_-
Branch: main
Auto Deploy: On (파란색 토글)
```

**Settings → Deploy:**
```
Start Command: gunicorn app:app --timeout 300
```

**Variables (RAW Editor):**
```env
WP_URL=https://blog.meditial.co.kr
WP_USERNAME=mincompanyad
WP_APP_PASSWORD=RzRh mJOi Q8kY 9hpR sarb rOD4
APP_PASSWORD=test1234
USE_ELEMENTOR=true
ELEMENTOR_METHOD=simple
CLAUDE_API_KEY=여기에-Claude-API-키
```

---

## 🔄 배포 워크플로우

### 코드 수정 후 배포

```bash
# 1. 로컬에서 코드 수정
git add .
git commit -m "변경 내용"
git push origin main
```

```
# 2. GitHub에서 Sync Fork
https://github.com/thenext0202/wordpress_-
→ [Sync fork] 버튼 클릭
→ [Update branch] 클릭
```

```
# 3. Railway 자동 배포 (2-3분)
Railway Deployments 탭에서 진행 상황 확인
🟡 Building... → 🟡 Deploying... → 🟢 Success!
```

### 배포 시간
- 감지: 30초~1분
- 빌드: 1-2분
- 배포: 30초
- **총 소요 시간: 2-4분**

---

## 🔑 환경 변수

### 필수 변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `WP_URL` | WordPress 사이트 URL | `https://blog.meditial.co.kr` |
| `WP_USERNAME` | WordPress 관리자 계정 | `mincompanyad` |
| `WP_APP_PASSWORD` | WordPress 앱 비밀번호 | `RzRh mJOi Q8kY 9hpR sarb rOD4` |
| `APP_PASSWORD` | 웹 UI 로그인 비밀번호 | `test1234` |
| `USE_ELEMENTOR` | Elementor 사용 여부 | `true` |
| `ELEMENTOR_METHOD` | Elementor 모드 | `simple` |
| `CLAUDE_API_KEY` | Claude AI API 키 | `sk-ant-api03-xxxxx...` |

### WordPress 앱 비밀번호 발급

1. WordPress 관리자 → 사용자 → 프로필
2. 아래로 스크롤 → **애플리케이션 비밀번호**
3. 이름 입력 (예: "Railway")
4. **새 애플리케이션 비밀번호 추가** 클릭
5. 생성된 비밀번호 복사 (공백 포함!)

### Claude API 키 발급

1. https://console.anthropic.com/ 접속
2. API Keys → Create Key
3. 이름 입력 → Create
4. 생성된 키 복사 (`sk-ant-api03-xxxxx...`)

---

## 📱 사용 방법

### 웹 UI 접속
```
https://web-production-xxxx.up.railway.app
```

### 1. 로그인
- 비밀번호: `test1234` (APP_PASSWORD)

### 2. AI로 글 생성 (조건부)

#### A. 응석 김 + 건강 칼럼 (의료 칼럼 모드)
1. 작성자: **항노화 김응석 박사** 선택
2. 카테고리: **건강 칼럼** 선택
3. **"AI로 생성"** 클릭
4. **주제만 입력**:
   ```
   예: 오메가3의 건강 효과
   예: 비타민D 부족 증상과 예방법
   ```
5. **생성하기** → 의료 전문가 톤으로 자동 생성

#### B. 다른 작성자/카테고리 (커스텀 모드)
1. 다른 작성자 또는 다른 카테고리 선택
2. **"AI로 생성"** 클릭
3. **글 작성 지침 입력** (선택사항):
   ```
   예: 친근한 톤으로 이모지를 사용해서 작성해주세요.
   예: 전문 개발자 대상으로 기술적 세부사항을 다루세요.
   예: 객관적인 뉴스 기사 스타일로 작성해주세요.
   ```
4. **주제 입력**
5. **생성하기** → 커스텀 지침대로 생성

#### 공통 기능
- ✨ **미리보기 자동 열림** (렌더링/소스)
- ✨ **제목 자동 입력**
- 📥 **다운로드 가능** (백업용)

### 3. 이미지 업로드
- 대표 이미지 드래그 앤 드롭
- 또는 클릭하여 파일 선택

### 4. 발행
1. 작성자 선택 (기본: 항노화 김응석 박사)
2. 카테고리 선택 (기본: 건강 칼럼)
3. **발행하기** 또는 **임시글 저장** 클릭

### 5. WordPress 확인
1. 발행된 글 링크 클릭
2. ✨ **Elementor 프로급 디자인 자동 적용됨!**
   - 그라디언트 헤더
   - 스타일 본문
   - 저자 소개 + 인스타그램 버튼

---

## 🎨 Elementor 디자인 구조

### 자동 생성되는 레이아웃

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 헤더 섹션                 ┃
┃ (그라디언트 배경)         ┃
┃   제목 (36px, 흰색)       ┃
┃   작성자 | 날짜            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─────────────────────────┐
│ 본문 섹션 (800px 너비)   │
│  • h2: 파란색, 24px      │
│  • h3: 20px, 굵게        │
│  • p: 1.8 줄간격         │
│  • 링크: 파란색 밑줄     │
└─────────────────────────┘

┌─────────────────────────┐
│ CTA 섹션                 │
│  👨‍⚕️ 저자 소개 박스       │
│  [버튼: 인스타그램 →]   │
└─────────────────────────┘
```

### 색상 팔레트
- Primary: `#1a73e8` (블루)
- Secondary: `#34a853` (그린)
- Text: `#333333`
- Background: `#f5f7fa`

### 모바일 반응형
- 데스크톱: 36px 제목, 800px 너비
- 태블릿: 자동 조정
- 모바일: 24px 제목, 전체 너비

---

## 🐛 문제 해결

### 1. Railway 배포가 안 됨

**원인:** GitHub 저장소 연결 문제

**해결:**
1. Railway에 Sync Fork 했는지 확인
   ```
   https://github.com/thenext0202/wordpress_-
   → [Sync fork] 클릭
   ```

2. Railway Settings → Source 확인
   ```
   Repository: thenext0202/wordpress_- ✅
   Branch: main ✅
   Auto Deploy: On (파란색) ✅
   ```

3. 강제 배포
   ```bash
   git commit --allow-empty -m "배포 트리거"
   git push
   ```

### 2. 작성자/카테고리가 안 보임

**원인:** WordPress 연결 문제

**해결:**
1. `.env` 또는 Railway Variables 확인
   ```
   WP_URL=https://blog.meditial.co.kr (슬래시 없음!)
   WP_APP_PASSWORD=RzRh mJOi Q8kY 9hpR sarb rOD4 (공백 포함!)
   ```

2. WordPress 앱 비밀번호 재발급
3. Railway Variables 업데이트
4. 재배포 대기 (2-3분)

### 3. AI 생성이 안 됨

**원인:** Claude API 키 문제

**해결:**
1. Railway Variables에 `CLAUDE_API_KEY` 확인
2. Claude Console에서 크레딧 잔액 확인
3. 새 API 키 발급 및 업데이트

### 4. Elementor 디자인이 안 나옴

**원인:** Elementor 설정 누락

**해결:**
```env
USE_ELEMENTOR=true
ELEMENTOR_METHOD=simple
```

Railway Variables에 추가 후 재배포

### 5. 배포 후 변경사항이 안 보임

**원인:** 브라우저 캐시

**해결:**
```
Ctrl + Shift + R (강력 새로고침)
또는 시크릿 모드로 접속
```

---

## 📁 프로젝트 구조

```
wordpress_-/
├── app.py                      # Flask 웹 서버 (메인)
├── post.py                     # CLI 발행 스크립트 (레거시)
├── elementor_helper.py         # Elementor 통합 (기본)
├── elementor_helper_pro.py     # Elementor 프로급 레이아웃
├── config.json                 # WordPress 기본 설정
├── .env                        # 환경 변수 (로컬)
├── requirements.txt            # Python 패키지
├── Procfile                    # Heroku/Railway 실행 명령
├── render.yaml                 # Render 배포 설정
├── static/
│   ├── index.html             # 웹 UI (PWA)
│   ├── manifest.json          # PWA 매니페스트
│   ├── sw.js                  # Service Worker
│   └── icon.svg               # PWA 아이콘
├── publish/                    # CLI 발행용 폴더 (선택)
│   └── [글제목]/
│       ├── *.html
│       ├── *.png
│       └── meta.json
└── docs/
    ├── README.md              # 이 문서
    ├── ELEMENTOR_SETUP.md     # Elementor 상세 가이드
    ├── QUICK_START_ELEMENTOR.md
    └── ELEMENTOR_AUTO_COMPLETE.md
```

---

## 🔗 관련 링크

### 서비스
- **WordPress**: https://blog.meditial.co.kr
- **Railway**: https://railway.app/dashboard
- **GitHub (원본)**: https://github.com/gold9-app/wordpress_-
- **GitHub (배포)**: https://github.com/thenext0202/wordpress_-

### API & 문서
- **Claude API**: https://console.anthropic.com/
- **WordPress REST API**: https://blog.meditial.co.kr/wp-json/
- **Rank Math**: https://rankmath.com/kb/
- **Elementor**: https://developers.elementor.com/

---

## 📊 배포 히스토리

### 주요 업데이트

```
2024-XX-XX - Elementor 프로급 자동 디자인 추가
2024-XX-XX - AI 생성 HTML 미리보기 기능
2024-XX-XX - AI 생성 시 제목 자동 입력
2024-XX-XX - Railway 배포 자동화 설정
```

---

## 💡 팁 & 트릭

### 빠른 글 발행
1. AI 생성 (1분)
2. 이미지 업로드 (10초)
3. 발행 (20초)
4. **총 소요 시간: 약 2분**

### SEO 점수 최대화
- AI가 자동으로 최적화
- Focus Keyword 자동 추출
- 메타 설명 자동 생성
- 이미지 alt 텍스트 자동 설정

### Elementor 수동 편집
1. WordPress에서 글 열기
2. "Elementor로 편집" 클릭
3. 색상, 간격 등 세밀 조정
4. 저장 → 즉시 반영

### 여러 작성자 관리
- 웹 UI에서 작성자 선택 가능
- 응석 김(ID: 4): 자동 인스타그램 링크
- 다른 작성자: 커스텀 외부 링크 입력 가능

---

## 🤝 기여

### 코드 수정 시
1. `gold9-app/wordpress_-`에 Push
2. `thenext0202/wordpress_-`로 Sync Fork
3. Railway 자동 배포

### 버그 리포트
- GitHub Issues 활용
- 또는 직접 수정 후 커밋

---

## 📝 라이센스

이 프로젝트는 메디셜(Meditial) 내부용입니다.

---

## 👨‍⚕️ 작성자

**항노화 김응석 박사**
- 대한줄기세포치료학회 회장
- 국제미용항노화학회 회장
- 대한비만건강학회 고문
- Instagram: [@medi_eungsuk](https://www.instagram.com/medi_eungsuk/)

---

## 🎉 완료!

이제 완벽한 자동화 시스템이 준비되었습니다!

**워크플로우:**
```
코드 수정 → Push → Sync Fork → 자동 배포 → 완료! 🚀
```

**사용:**
```
AI 생성 → 미리보기 → 발행 → Elementor 디자인 적용 → 완료! ✨
```

---

**마지막 업데이트:** 2024년
**버전:** 2.0 (Elementor 프로급 디자인 자동화)
