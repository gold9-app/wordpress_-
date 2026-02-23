# 🚀 배포 체크리스트

빠른 참조용 체크리스트입니다.

---

## ✅ 초기 설정 (한 번만)

### GitHub
- [ ] 원본 저장소: `gold9-app/wordpress_-`
- [ ] 배포 저장소: `thenext0202/wordpress_-` (Fork)

### Railway 프로젝트
- [ ] Settings → Source
  - [ ] Repository: `thenext0202/wordpress_-`
  - [ ] Branch: `main`
  - [ ] Auto Deploy: **On** (파란색)

### Railway 환경 변수 (RAW Editor)
```env
WP_URL=https://blog.meditial.co.kr
WP_USERNAME=mincompanyad
WP_APP_PASSWORD=RzRh mJOi Q8kY 9hpR sarb rOD4
APP_PASSWORD=test1234
USE_ELEMENTOR=true
ELEMENTOR_METHOD=simple
CLAUDE_API_KEY=sk-ant-api03-xxxxx...
```

---

## 📝 코드 수정 후 배포

### 1. 로컬 → GitHub (gold9-app)
```bash
git add .
git commit -m "변경 내용"
git push
```

### 2. GitHub Sync Fork
```
https://github.com/thenext0202/wordpress_-
→ [Sync fork] 클릭
→ [Update branch] 클릭
```

### 3. Railway 확인
```
Deployments 탭
→ 🟡 Building... (2-3분)
→ 🟢 Success!
```

---

## 🌐 웹 UI 사용

### 접속
```
Railway URL (예: https://xxx.up.railway.app)
로그인: test1234
```

### AI 글 생성
1. [ ] "AI로 생성" 클릭
2. [ ] 주제 입력
3. [ ] 생성 대기 (30초~1분)
4. [ ] 미리보기 확인 (자동 열림)
5. [ ] 제목 확인 (자동 입력)

### 발행
1. [ ] 이미지 업로드
2. [ ] 작성자/카테고리 선택
3. [ ] 발행하기 클릭
4. [ ] WordPress 확인
5. [ ] Elementor 디자인 확인

---

## 🐛 문제 해결

### 배포 안 됨
- [ ] Sync Fork 했나?
- [ ] Railway Auto Deploy On?
- [ ] Deployments 탭 확인

### 작성자/카테고리 안 보임
- [ ] WP_URL 슬래시(/) 없는지 확인
- [ ] WP_APP_PASSWORD 공백 포함 확인
- [ ] WordPress 앱 비밀번호 재발급

### AI 생성 안 됨
- [ ] CLAUDE_API_KEY 설정 확인
- [ ] Claude 크레딧 잔액 확인

### Elementor 안 나옴
- [ ] USE_ELEMENTOR=true
- [ ] ELEMENTOR_METHOD=simple
- [ ] 재배포

---

## 📊 정상 작동 확인

- [ ] Railway Deployments → Success
- [ ] 웹 UI 접속 가능
- [ ] 로그인 가능
- [ ] 작성자/카테고리 로딩됨
- [ ] AI 생성 작동
- [ ] 미리보기 작동
- [ ] 제목 자동 입력
- [ ] 발행 성공
- [ ] WordPress에서 Elementor 디자인 보임

---

## 🔑 중요 정보

### Railway URL
```
https://web-production-xxxx.up.railway.app
```

### WordPress
```
https://blog.meditial.co.kr
```

### GitHub
```
원본: https://github.com/gold9-app/wordpress_-
배포: https://github.com/thenext0202/wordpress_-
```

---

**마지막 확인:**
- 모든 체크박스 ✅
- 배포 시간: 2-4분
- 글 작성: 약 2분
