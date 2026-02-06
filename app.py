"""
WordPress 글 자동 발행 - PWA 웹 서버 (Render 호스팅용)
"""

import json
import mimetypes
import os
import re
import tempfile
from functools import wraps
from pathlib import Path

import requests as http_requests
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")

SITE_NAME = os.getenv("SITE_NAME", "메디셜 공식 블로그")
CATEGORY_ID = int(os.getenv("CATEGORY_ID", "22"))
AUTHOR_ID = int(os.getenv("AUTHOR_ID", "4"))
AUTHOR_INSTAGRAM = os.getenv("AUTHOR_INSTAGRAM", "https://www.instagram.com/medi_eungsuk/")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

app = Flask(__name__, static_folder="static")


# ─── 인증 ───

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not APP_PASSWORD:
            return f(*args, **kwargs)
        auth = request.headers.get("X-App-Password", "")
        if auth != APP_PASSWORD:
            return jsonify({"ok": False, "error": "비밀번호가 올바르지 않습니다."}), 401
        return f(*args, **kwargs)
    return decorated


# ─── 유틸 함수 ───

def strip_html(html):
    return re.sub(r"<[^>]+>", "", html).strip()


def make_slug(text):
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s가-힣-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def extract_focus_keyword(title):
    keyword = title
    keyword = re.sub(r"\d+\s*가지", "", keyword)
    remove_patterns = [
        "에 대해 잘못 알려진", "에 대해 알려진", "에 대해 알아야 할",
        "꼭 알아야 할", "알아야 할", "꼭 알아야할", "반드시 알아야 할",
        "에 대해", "에 대한", "에서의", "에서", "으로의", "으로", "를 위한", "을 위한",
        "하는 방법", "하는 법", "하는법", "알아보기", "알아보자",
        "상식", "방법", "효과", "원인", "증상", "종류", "차이", "차이점",
        "비교", "추천", "정리", "총정리", "리뷰", "후기",
        "장점", "단점", "장단점", "주의사항", "부작용", "특징",
        "가이드", "완벽 가이드", "핵심 정리",
        "진실", "오해", "팩트", "팩트체크", "궁금증",
        "잘못 알려진", "잘못알려진", "최신", "최고의", "효과적인",
        "올바른", "정확한", "꼭 필요한", "반드시", "꼭",
    ]
    for p in remove_patterns:
        keyword = keyword.replace(p, "")
    keyword = re.sub(r"[|,\-~:?!]", "", keyword)
    keyword = re.sub(r"\s+", " ", keyword).strip()
    return keyword if keyword else title


def inject_external_link(html_content, author_id, custom_link=""):
    """
    작성자가 응석 김(ID=4)이면 인스타그램 링크 자동 삽입,
    다른 작성자는 custom_link가 있으면 삽입
    """
    if author_id == 4:
        # 응석 김: 인스타그램 링크 자동
        if not AUTHOR_INSTAGRAM or "instagram.com" in html_content:
            return html_content
        link_html = (
            f'<p>더 많은 건강 정보는 '
            f'<a href="{AUTHOR_INSTAGRAM}" target="_blank">응석 김 인스타그램</a>'
            f'에서 확인하세요.</p>'
        )
        return html_content + "\n" + link_html
    else:
        # 다른 작성자: custom_link가 있으면 삽입
        if not custom_link:
            return html_content
        link_html = (
            f'<p>더 많은 정보는 '
            f'<a href="{custom_link}" target="_blank">{custom_link}</a>'
            f'에서 확인하세요.</p>'
        )
        return html_content + "\n" + link_html


def inject_internal_link(html_content, internal_link):
    """내부 링크를 글 맨 마지막에 삽입"""
    if not internal_link:
        return html_content
    link_html = (
        f'<p>또 보면 좋은 글: <a href="{internal_link}">{internal_link}</a></p>'
    )
    return html_content + "\n" + link_html


def ensure_focus_keyword_in_content(html_content, focus_keyword):
    plain_start = strip_html(html_content[:500])
    if focus_keyword.lower() in plain_start.lower():
        return html_content
    return f"<p>{focus_keyword}에 대해 알아보겠습니다.</p>\n" + html_content


def ensure_focus_keyword_in_subheading(html_content, focus_keyword):
    pattern = re.compile(r"<h[23][^>]*>(.*?)</h[23]>", re.IGNORECASE | re.DOTALL)
    for sh in pattern.findall(html_content):
        if focus_keyword.lower() in strip_html(sh).lower():
            return html_content

    def add_kw(match):
        return match.group(0).replace(match.group(1), f"{focus_keyword} - {match.group(1)}", 1)

    result, count = re.subn(r"<h2[^>]*>(.*?)</h2>", add_kw, html_content, count=1, flags=re.IGNORECASE | re.DOTALL)
    return result if count > 0 else html_content


def inject_focus_keyword_image(html_content, focus_keyword, image_url):
    img_tag = f'<img src="{image_url}" alt="{focus_keyword}" style="width:100%; height:auto;" />'
    match = re.search(r"(</[^>]+>)", html_content)
    if match:
        pos = match.end()
        return html_content[:pos] + "\n" + img_tag + "\n" + html_content[pos:]
    return img_tag + "\n" + html_content


def build_seo_fields(title, html_content):
    focus_keyword = extract_focus_keyword(title)
    plain_text = strip_html(html_content)

    if focus_keyword.lower() in title.lower():
        seo_title = f"{title} - {SITE_NAME}"
    else:
        seo_title = f"{title} | {focus_keyword} - {SITE_NAME}"

    desc_text = plain_text[:300].replace("\n", " ").strip()
    last_period = desc_text[:140].rfind(".")
    description = desc_text[:last_period + 1] if last_period > 50 else desc_text[:140]
    if focus_keyword.lower() not in description.lower():
        description = f"{focus_keyword} - {description}"
    if len(description) > 155:
        description = description[:152] + "..."

    slug = make_slug(focus_keyword)

    return {
        "focus_keyword": focus_keyword,
        "description": description,
        "seo_title": seo_title,
        "slug": slug,
    }


def get_or_create_tags(tag_names):
    tag_ids = []
    for name in tag_names:
        resp = http_requests.get(
            f"{WP_URL}/wp-json/wp/v2/tags",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            params={"search": name}, timeout=10,
        )
        found = False
        if resp.status_code == 200 and resp.json():
            for tag in resp.json():
                if tag["name"].lower() == name.lower():
                    tag_ids.append(tag["id"])
                    found = True
                    break
        if not found:
            resp2 = http_requests.post(
                f"{WP_URL}/wp-json/wp/v2/tags",
                auth=(WP_USERNAME, WP_APP_PASSWORD),
                json={"name": name}, timeout=10,
            )
            if resp2.status_code in (200, 201):
                tag_ids.append(resp2.json()["id"])
    return tag_ids


def upload_image(image_path, alt_text=""):
    mime_type = mimetypes.guess_type(str(image_path))[0] or "image/jpeg"
    ascii_filename = f"image{Path(image_path).suffix}"

    resp = http_requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        headers={
            "Content-Disposition": f'attachment; filename="{ascii_filename}"',
            "Content-Type": mime_type,
        },
        data=Path(image_path).read_bytes(), timeout=60,
    )
    if resp.status_code not in (200, 201):
        return -1, ""

    data = resp.json()
    media_id = data["id"]
    image_url = data.get("source_url", "")

    if alt_text:
        http_requests.post(
            f"{WP_URL}/wp-json/wp/v2/media/{media_id}",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json={"alt_text": alt_text}, timeout=10,
        )
    return media_id, image_url


# ─── API 엔드포인트 ───

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")


@app.route("/sw.js")
def service_worker():
    return send_from_directory("static", "sw.js")


@app.route("/api/auth", methods=["POST"])
def api_auth():
    if not APP_PASSWORD:
        return jsonify({"ok": True})
    pw = request.json.get("password", "")
    if pw == APP_PASSWORD:
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "비밀번호가 올바르지 않습니다."}), 401


@app.route("/api/options")
@require_auth
def api_options():
    """작성자 및 카테고리 목록 조회"""
    try:
        authors_resp = http_requests.get(
            f"{WP_URL}/wp-json/wp/v2/users",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            timeout=10,
        )
        categories_resp = http_requests.get(
            f"{WP_URL}/wp-json/wp/v2/categories",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            params={"per_page": 50},
            timeout=10,
        )

        authors = [{"id": u["id"], "name": u["name"]} for u in authors_resp.json()]
        categories = [{"id": c["id"], "name": c["name"]} for c in categories_resp.json()]

        return jsonify({
            "ok": True,
            "authors": authors,
            "categories": categories,
            "defaults": {
                "author_id": AUTHOR_ID,
                "category_id": CATEGORY_ID,
            }
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


CLAUDE_SYSTEM_PROMPT = """당신은 "항노화 김응석 박사" 명의로 건강 칼럼을 작성하는 전문 의료 콘텐츠 작성자입니다.

## 작성자 정보
- 칼럼 작성자: 항노화 김응석 박사
- 대한줄기세포치료학회 회장
- 국제미용항노화학회 회장
- 대한비만건강학회 고문

## 글 구조 (반드시 이 순서로 작성)

### 1. 훅 (Hook)
- 스크롤을 멈추게 하는 첫 문장
- "이거 모르면 손해"식 궁금증 유발 또는 의외의 사실로 시작
- 예: "커피가 간에 좋다는 거, 진짜일까요?"

### 2. 공감 (Pain Point)
- 독자가 "어, 나 얘기네?" 하는 순간
- 흔히 겪는 증상/상황 묘사
- 잘못 알려진 상식 언급

### 3. 핵심 정보 (Main Content)
- 의사만 알려줄 수 있는 내용
- 소제목 + 본문으로 구성
- 어려운 용어는 쉬운 비유로 설명
- 숫자/데이터는 1~2개만 사용
- 과학적 근거/메커니즘 설명
- 구체적인 정보 (용량, 섭취 방법, 주의사항)
- Q&A 형식으로 흔한 오해 바로잡기

### 4. 실천 팁 (Actionable)
- 오늘 당장 할 수 있는 구체적이고 쉬운 행동 1~2가지

### 5. 의사의 한마디 (Trust Building)
- 진료실에서 느낀 점, 환자분들 사례 (익명)
- 인간적인 면 + 전문가 관점

### 6. 마무리 CTA
- 저장/공유 유도: "도움이 되셨다면 저장해두세요."

### 7. 참고문헌
- 논문 출처 포함 (마지막에 배치)

## HTML 작성 규칙
1. WordPress에 바로 사용 가능한 HTML
2. 화려하지 않고 전문적인 느낌
3. 모바일 최적화 (반응형)
4. 키워드 밀도 약 2% 수준
5. 폰트: Noto Sans KR, Malgun Gothic
6. 깔끔한 여백과 가독성 좋은 줄간격
7. ```html 등 마크다운 없이 순수 HTML만 출력
8. 칼럼에 걸맞는 충분한 길이 (1500-2500자)"""


@app.route("/api/generate-html", methods=["POST"])
@require_auth
def api_generate_html():
    """Claude API로 HTML 생성"""
    if not CLAUDE_API_KEY:
        return jsonify({"ok": False, "error": "Claude API 키가 설정되지 않았습니다."}), 500

    data = request.json
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"ok": False, "error": "요청사항을 입력해주세요."}), 400

    try:
        resp = http_requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": CLAUDE_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 8000,
                "system": CLAUDE_SYSTEM_PROMPT,
                "messages": [
                    {
                        "role": "user",
                        "content": f"다음 주제로 건강 칼럼을 HTML 형식으로 작성해주세요:\n\n{prompt}"
                    }
                ]
            },
            timeout=300,
        )

        if resp.status_code != 200:
            return jsonify({"ok": False, "error": f"Claude API 오류 (HTTP {resp.status_code})"}), 500

        result = resp.json()
        html_content = result["content"][0]["text"]

        # HTML 코드블록 제거 (혹시 있을 경우)
        html_content = html_content.strip()
        if html_content.startswith("```html"):
            html_content = html_content[7:]
        if html_content.startswith("```"):
            html_content = html_content[3:]
        if html_content.endswith("```"):
            html_content = html_content[:-3]
        html_content = html_content.strip()

        return jsonify({"ok": True, "html": html_content})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/publish", methods=["POST"])
@require_auth
def api_publish():
    title = request.form.get("title", "").strip()
    status = request.form.get("status", "draft")
    author_id = int(request.form.get("author_id", AUTHOR_ID))
    category_id = int(request.form.get("category_id", CATEGORY_ID))
    external_link = request.form.get("external_link", "").strip()
    internal_link = request.form.get("internal_link", "").strip()
    html_file = request.files.get("html_file")
    image_file = request.files.get("image_file")

    if not title:
        return jsonify({"ok": False, "error": "제목을 입력해주세요."}), 400
    if not html_file:
        return jsonify({"ok": False, "error": "HTML 파일을 업로드해주세요."}), 400
    if not image_file:
        return jsonify({"ok": False, "error": "이미지 파일을 업로드해주세요."}), 400

    # 이미지 확장자 검증
    img_ext = os.path.splitext(image_file.filename)[1].lower()
    if img_ext not in IMAGE_EXTS:
        return jsonify({"ok": False, "error": f"지원하지 않는 이미지 형식입니다: {img_ext}"}), 400

    try:
        html_content = html_file.read().decode("utf-8")
    except UnicodeDecodeError:
        return jsonify({"ok": False, "error": "HTML 파일을 UTF-8로 읽을 수 없습니다."}), 400

    # 임시 파일로 이미지 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=img_ext) as tmp:
        image_file.save(tmp)
        tmp_path = tmp.name

    try:
        seo = build_seo_fields(title, html_content)
        focus_keyword = seo["focus_keyword"]

        # 이미지 업로드
        media_id, image_url = upload_image(tmp_path, alt_text=focus_keyword)
        if media_id == -1:
            return jsonify({"ok": False, "error": "이미지 업로드 실패"}), 500

        # 콘텐츠 최적화
        html_content = ensure_focus_keyword_in_content(html_content, focus_keyword)
        html_content = ensure_focus_keyword_in_subheading(html_content, focus_keyword)
        if image_url:
            html_content = inject_focus_keyword_image(html_content, focus_keyword, image_url)
        html_content = inject_internal_link(html_content, internal_link)
        html_content = inject_external_link(html_content, author_id, external_link)
        wp_content = f"<!-- wp:html -->\n{html_content}\n<!-- /wp:html -->"

        # 글 발행
        post_data = {
            "title": title,
            "content": wp_content,
            "status": status,
            "slug": seo["slug"],
            "featured_media": media_id,
            "categories": [category_id],
            "author": author_id,
        }

        resp = http_requests.post(
            f"{WP_URL}/wp-json/wp/v2/posts",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json=post_data, timeout=30,
        )
        if resp.status_code not in (200, 201):
            return jsonify({"ok": False, "error": f"글 발행 실패 (HTTP {resp.status_code})"}), 500

        result = resp.json()
        post_id = result["id"]

        # Rank Math 메타
        http_requests.post(
            f"{WP_URL}/wp-json/rankmath/v1/updateMeta",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json={
                "objectType": "post", "objectID": post_id,
                "meta": {
                    "rank_math_title": seo["seo_title"],
                    "rank_math_description": seo["description"],
                    "rank_math_focus_keyword": seo["focus_keyword"],
                    "rank_math_robots": "index,follow",
                },
            }, timeout=15,
        )

        # Rank Math 스키마
        http_requests.post(
            f"{WP_URL}/wp-json/rankmath/v1/updateSchemas",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json={
                "objectType": "post", "objectID": post_id,
                "schemas": {
                    "new-1": {
                        "@type": "Article",
                        "metadata": {"title": "Article", "type": "template", "isPrimary": True},
                        "headline": "%seo_title%",
                        "description": "%seo_description%",
                        "datePublished": "%date(Y-m-dTH:i:sP)%",
                        "dateModified": "%modified(Y-m-dTH:i:sP)%",
                        "author": {"@type": "Person", "name": "%name%"},
                    }
                },
            }, timeout=15,
        )

        # 글 재저장하여 Rank Math 점수 재계산 트리거
        http_requests.post(
            f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json={"id": post_id}, timeout=15,
        )

        return jsonify({
            "ok": True,
            "post_id": post_id,
            "url": result["link"],
            "seo": seo,
        })

    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    print(f"\n  워드프레스 자동 발행 서버 시작")
    print(f"  http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
