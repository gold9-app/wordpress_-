# 🎨 Elementor 통합 설정 가이드

이 가이드는 워드프레스 자동 발행 시스템에 Elementor를 통합하여 가시성을 높이는 방법을 설명합니다.

---

## 📋 목차
1. [전제 조건](#전제-조건)
2. [설정 방법](#설정-방법)
3. [3가지 통합 방식](#3가지-통합-방식)
4. [추천 워크플로우](#추천-워크플로우)
5. [문제 해결](#문제-해결)

---

## 전제 조건

### WordPress 플러그인
- ✅ **Elementor** (무료) 또는 **Elementor Pro** 설치 필요
- ✅ **Rank Math SEO** (이미 사용 중)

### 확인 사항
```bash
WordPress 관리자 → 플러그인 → Elementor 활성화 확인
```

---

## 설정 방법

### 1. `.env` 파일 수정

```env
# Elementor 사용 여부
USE_ELEMENTOR=true

# 통합 방법 선택 (simple, template, full)
ELEMENTOR_METHOD=simple

# 템플릿 ID (method=template일 때만 필요)
ELEMENTOR_TEMPLATE_ID=
```

### 2. 방법 선택 기준

| 방법 | 난이도 | 가시성 | SEO | 추천 대상 |
|------|--------|--------|-----|----------|
| **simple** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 빠른 시작 |
| **template** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 디자인 중시 (추천) |
| **full** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 완전 자동화 |

---

## 3가지 통합 방식

### 방법 1: Simple (HTML 위젯) ⚡

**가장 간단하고 빠른 방법**

```env
USE_ELEMENTOR=true
ELEMENTOR_METHOD=simple
```

#### 작동 방식
- 자동으로 Elementor를 활성화
- HTML 콘텐츠를 Elementor HTML 위젯으로 래핑
- 기본 섹션 레이아웃 자동 생성

#### 장점
✅ 설정 불필요
✅ 즉시 사용 가능
✅ SEO 완벽 유지

#### 단점
❌ 디자인 제한적
❌ Elementor 편집기에서 수동 스타일링 필요

#### 결과 예시
```
┌─────────────────────┐
│ [Elementor 섹션]     │
│   [HTML 위젯]        │
│     - 기존 HTML 콘텐츠│
└─────────────────────┘
```

---

### 방법 2: Template (템플릿 활용) ⭐ 추천

**디자인과 자동화의 균형**

#### Step 1: WordPress에서 템플릿 생성

1. **WordPress 관리자** → **템플릿** → **테마 빌더**
2. **단일 게시물** → **새로 추가**
3. 템플릿 이름: `건강 칼럼 레이아웃`

#### Step 2: Elementor로 레이아웃 디자인

```
┌──────────────────────────────┐
│ 헤더 섹션 (Elementor)          │
│ - 그라디언트 배경              │
│ - 동적 태그: 제목              │
│ - 동적 태그: 대표 이미지        │
│ - 저자 정보, 날짜              │
└──────────────────────────────┘
┌──────────────────────────────┐
│ 본문 섹션 (Elementor)          │
│ - Text Editor 위젯             │
│ - 동적 태그: Post Content      │
│ - 또는 HTML 위젯               │
└──────────────────────────────┘
┌──────────────────────────────┐
│ CTA 섹션 (Elementor)           │
│ - 작성자 소개 박스             │
│ - 인스타그램 버튼              │
│ - 관련 글 추천                 │
└──────────────────────────────┘
```

#### Step 3: 템플릿 ID 확인

템플릿 저장 후 **URL에서 ID 확인**:
```
예: .../post.php?post=1234&action=elementor
→ 템플릿 ID는 1234
```

#### Step 4: .env 설정

```env
USE_ELEMENTOR=true
ELEMENTOR_METHOD=template
ELEMENTOR_TEMPLATE_ID=1234
```

#### Step 5: 조건 설정 (중요!)

**템플릿 → 설정 → 조건**
- **카테고리가 "건강 칼럼"인 경우** (ID: 22)
- 또는 **모든 단일 게시물**

#### 장점
✅ 디자인 완전 커스터마이징
✅ 재사용 가능
✅ SEO 완벽 유지
✅ 자동화 가능

#### 단점
❌ 초기 템플릿 제작 필요 (1회)

---

### 방법 3: Full (완전 변환) 🔥

**HTML을 Elementor 위젯으로 완전 변환**

```env
USE_ELEMENTOR=true
ELEMENTOR_METHOD=full
```

#### 작동 방식
- HTML을 파싱하여 각 요소를 Elementor 위젯으로 변환
- `<h1>` → Heading 위젯
- `<p>` → Text Editor 위젯
- `<img>` → Image 위젯

#### 장점
✅ 완전한 Elementor 경험
✅ 각 요소 개별 편집 가능
✅ 모바일 반응형 완벽 지원

#### 단점
❌ 복잡한 HTML 구조는 변환 제한
❌ 일부 스타일 손실 가능

---

## 추천 워크플로우

### 🚀 빠른 시작 (5분)

1. `.env`에 다음 추가:
```env
USE_ELEMENTOR=true
ELEMENTOR_METHOD=simple
```

2. 글 발행 테스트
```bash
python app.py
```

3. WordPress에서 글 확인 → Elementor로 편집

---

### 🎨 프로 설정 (30분)

#### 1단계: 템플릿 제작 (WordPress)

**헤더 섹션**
- 배경: 그라디언트 (건강 테마 색상)
- 동적 태그 삽입:
  - 제목: `Post Title`
  - 대표 이미지: `Featured Image`
  - 날짜: `Post Date`

**본문 섹션**
- Text Editor 위젯 추가
- 동적 콘텐츠: `Post Content` 선택
- 타이포그래피 설정:
  - 본문: Noto Sans KR, 16px, 1.8 줄간격
  - h2: 24px, 700, 상단 여백 40px
  - h3: 20px, 600, 상단 여백 30px

**CTA 섹션**
- Call to Action 위젯
- 버튼: "더 많은 건강 정보 보기"
- 링크: 인스타그램

#### 2단계: 스타일 커스터마이징

**색상 팔레트**
- Primary: `#1a73e8` (블루)
- Secondary: `#34a853` (그린)
- Text: `#333333`
- Background: `#f5f7fa`

**여백 (Padding/Margin)**
- 섹션 상하: 80px
- 모바일 섹션 상하: 40px
- 제목 하단: 20px
- 단락 하단: 16px

#### 3단계: 모바일 최적화

**Elementor 반응형 모드**
- 태블릿: 768px 이하
- 모바일: 480px 이하

**조정 사항**
- 폰트 크기 10-20% 축소
- 패딩 50% 축소
- 이미지 높이 자동 조정

#### 4단계: 템플릿 ID 설정

```env
USE_ELEMENTOR=true
ELEMENTOR_METHOD=template
ELEMENTOR_TEMPLATE_ID=1234  # 실제 ID로 변경
```

---

## 문제 해결

### Q1. Elementor가 활성화되지 않아요

**해결 방법:**
1. WordPress에서 Elementor 플러그인 설치 확인
2. 글 편집 화면에서 "Elementor로 편집" 버튼이 보이는지 확인
3. `.env`에서 `USE_ELEMENTOR=true` 확인

### Q2. 템플릿이 적용되지 않아요

**해결 방법:**
1. 템플릿 ID가 정확한지 확인
2. 템플릿 조건에 해당 카테고리가 포함되어 있는지 확인
3. WordPress → 템플릿 → 조건 확인

### Q3. SEO 점수가 떨어졌어요

**해결 방법:**
- Elementor는 SEO 친화적입니다
- Rank Math는 Elementor 콘텐츠를 읽을 수 있습니다
- `ELEMENTOR_METHOD=simple`이 가장 SEO 안전

### Q4. 콘텐츠가 깨져 보여요

**해결 방법:**
1. `ELEMENTOR_METHOD=simple` 사용
2. 또는 Elementor 편집기에서 수동 조정
3. `full` 방식은 복잡한 HTML에는 부적합

### Q5. 속도가 느려졌어요

**해결 방법:**
- Elementor Pro의 CSS 최적화 기능 활성화
- WordPress → Elementor → 설정 → 고급 → CSS 인라인 제거
- 캐싱 플러그인 사용 (WP Rocket, W3 Total Cache)

---

## 베스트 프랙티스

### ✅ DO (권장)
- **Template 방식 사용** (디자인 + 자동화)
- **재사용 가능한 템플릿** 제작
- **모바일 반응형** 테스트
- **로딩 속도** 정기 체크

### ❌ DON'T (비추천)
- 너무 복잡한 Elementor 위젯 사용 (속도 저하)
- 템플릿 없이 `full` 방식 사용 (불안정)
- Elementor 없이 HTML만 발행 후 수동 전환 (비효율)

---

## 예제: 완벽한 건강 칼럼 템플릿

### 템플릿 구조 (코드)

WordPress Elementor 템플릿 JSON을 내보내려면:
1. 템플릿 편집
2. 저장 옵션 → **Export Template**
3. JSON 파일 다운로드

### 기본 색상 설정

Elementor → Site Settings → Global Colors:
```
Primary: #1a73e8
Secondary: #34a853
Text: #333333
Accent: #fbbc04
```

---

## 자동화 체크리스트

- [ ] Elementor 플러그인 설치 완료
- [ ] 템플릿 제작 완료 (method=template 사용 시)
- [ ] 템플릿 ID 확인 및 .env 설정
- [ ] 템플릿 조건 설정 (카테고리 매칭)
- [ ] 테스트 글 발행
- [ ] WordPress에서 Elementor로 편집 가능 확인
- [ ] 모바일 반응형 확인
- [ ] SEO 점수 확인 (Rank Math)
- [ ] 로딩 속도 확인 (PageSpeed Insights)

---

## 지원

문제가 있으면 다음을 확인하세요:
1. `elementor_helper.py` 로그
2. WordPress 디버그 로그
3. Browser 콘솔 (F12)

---

**축하합니다! 🎉**
이제 자동화된 Elementor 통합이 완료되었습니다.
가시성과 SEO를 모두 만족하는 멋진 블로그를 운영하세요!
