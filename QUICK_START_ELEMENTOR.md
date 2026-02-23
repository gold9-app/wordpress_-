# ⚡ Elementor 빠른 시작 (5분)

## 1단계: 환경 변수 설정

`.env` 파일에 다음 라인 추가:

```env
# 기존 설정은 유지...

# Elementor 활성화 (간단 모드)
USE_ELEMENTOR=true
ELEMENTOR_METHOD=simple
```

## 2단계: 즉시 테스트

### 웹 UI 사용
```bash
python app.py
```

브라우저에서 접속 → 글 발행 → 자동으로 Elementor 활성화됨!

### CLI 사용
```bash
python post.py
```

`publish` 폴더의 글들이 Elementor로 발행됩니다.

## 3단계: WordPress 확인

1. WordPress 관리자 접속
2. 발행된 글 클릭
3. **"Elementor로 편집"** 버튼 확인 ✅
4. 클릭하면 Elementor 편집기 열림!

---

## 더 나은 디자인을 원한다면?

### 방법 A: WordPress에서 수동 편집
1. Elementor 편집기 열기
2. 헤더 섹션 추가
3. 스타일 커스터마이징
4. 저장!

### 방법 B: 템플릿 사용 (추천)
`ELEMENTOR_SETUP.md` 파일의 "방법 2: Template" 섹션 참고

---

## 결과 비교

### Before (HTML만)
```
┌────────────────┐
│ 제목            │
│                │
│ 텍스트 콘텐츠    │
│ 텍스트 콘텐츠    │
│ 텍스트 콘텐츠    │
└────────────────┘
```
❌ 심플하지만 밋밋함

### After (Elementor)
```
┌────────────────┐
│ 🎨 헤더 섹션    │
│ (그라디언트 배경)│
│ 제목 + 이미지   │
└────────────────┘
┌────────────────┐
│ 📝 본문 섹션    │
│ 스타일 적용     │
│ 여백 최적화     │
└────────────────┘
┌────────────────┐
│ 📢 CTA 섹션     │
│ 버튼 + 링크     │
└────────────────┘
```
✅ 전문적이고 가시성 좋음!

---

## 문제 해결

### Elementor 버튼이 안 보여요
→ WordPress에서 Elementor 플러그인 설치 확인

### SEO 점수가 걱정돼요
→ 걱정 마세요! Rank Math는 Elementor와 완벽 호환됩니다.
→ 콘텐츠는 그대로 유지되므로 SEO에 영향 없음

### 속도가 느려질까요?
→ Simple 모드는 속도 영향 거의 없음
→ 나중에 Elementor Pro의 최적화 기능 활용 가능

---

**완료! 🎉 이제 자동으로 Elementor가 활성화된 글이 발행됩니다.**
