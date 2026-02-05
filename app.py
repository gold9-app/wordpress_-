"""
WordPress 글 자동 발행 - PWA 웹 서버
"""

import json
import mimetypes
import os
import re
import sys
import webbrowser
import threading
from pathlib import Path

import requests as http_requests
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).parent
load_dotenv(SCRIPT_DIR / ".env")

WP_URL = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")

PUBLISH_DIR = SCRIPT_DIR / "publish"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
HTML_EXTS = {".html", ".htm"}

with open(SCRIPT_DIR / "config.json", encoding="utf-8") as f:
    CONFIG = json.load(f)

app = Flask(__name__, static_folder="static")


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


def find_files(folder, extensions):
    return [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in extensions]


def inject_external_link(html_content):
    instagram_url = CONFIG.get("author_instagram", "")
    if not instagram_url or "instagram.com" in html_content:
        return html_content
    link_html = (
        f'<p>더 많은 건강 정보는 '
        f'<a href="{instagram_url}" target="_blank">응석 김 인스타그램</a>'
        f'에서 확인하세요.</p>'
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


def build_seo_fields(title, html_content, meta):
    focus_keyword = meta.get("focus_keyword", "") or extract_focus_keyword(title)
    plain_text = strip_html(html_content)

    seo_title = meta.get("seo_title", "")
    if not seo_title:
        if focus_keyword.lower() in title.lower():
            seo_title = f"{title} - {CONFIG['site_name']}"
        else:
            seo_title = f"{title} | {focus_keyword} - {CONFIG['site_name']}"

    description = meta.get("description", "")
    if not description:
        desc_text = plain_text[:300].replace("\n", " ").strip()
        last_period = desc_text[:140].rfind(".")
        description = desc_text[:last_period + 1] if last_period > 50 else desc_text[:140]
        if focus_keyword.lower() not in description.lower():
            description = f"{focus_keyword} - {description}"
    if len(description) > 155:
        description = description[:152] + "..."

    slug = meta.get("slug", make_slug(focus_keyword))
    tags = meta.get("tags", [])

    return {
        "focus_keyword": focus_keyword,
        "description": description,
        "seo_title": seo_title,
        "slug": slug,
        "tags": tags,
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
    ascii_filename = f"image{image_path.suffix}"

    resp = http_requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        headers={
            "Content-Disposition": f'attachment; filename="{ascii_filename}"',
            "Content-Type": mime_type,
        },
        data=image_path.read_bytes(), timeout=60,
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


@app.route("/api/folders")
def api_folders():
    if not PUBLISH_DIR.exists():
        PUBLISH_DIR.mkdir()
        return jsonify([])

    folders = sorted([f for f in PUBLISH_DIR.iterdir() if f.is_dir()])
    result = []
    for folder in folders:
        html_files = find_files(folder, HTML_EXTS)
        image_files = find_files(folder, IMAGE_EXTS)
        has_meta = (folder / "meta.json").exists()

        errors = []
        if len(html_files) == 0:
            errors.append("HTML 파일 없음")
        elif len(html_files) > 1:
            errors.append(f"HTML {len(html_files)}개")
        if len(image_files) == 0:
            errors.append("이미지 없음")
        elif len(image_files) > 1:
            errors.append(f"이미지 {len(image_files)}개")

        title = folder.name
        focus_keyword = extract_focus_keyword(title)

        result.append({
            "name": folder.name,
            "valid": len(errors) == 0,
            "errors": errors,
            "html": html_files[0].name if html_files else None,
            "image": image_files[0].name if image_files else None,
            "has_meta": has_meta,
            "focus_keyword": focus_keyword,
        })
    return jsonify(result)


@app.route("/api/publish", methods=["POST"])
def api_publish():
    data = request.json
    folder_name = data.get("folder")
    status = data.get("status", "draft")

    folder = PUBLISH_DIR / folder_name
    if not folder.exists():
        return jsonify({"ok": False, "error": "폴더를 찾을 수 없습니다."}), 404

    html_files = find_files(folder, HTML_EXTS)
    image_files = find_files(folder, IMAGE_EXTS)
    if not html_files or not image_files:
        return jsonify({"ok": False, "error": "HTML 또는 이미지 파일이 없습니다."}), 400

    title = folder.name
    html_content = html_files[0].read_text(encoding="utf-8")

    meta_path = folder / "meta.json"
    meta = {}
    if meta_path.exists():
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

    seo = build_seo_fields(title, html_content, meta)
    focus_keyword = seo["focus_keyword"]

    # 이미지 업로드
    media_id, image_url = upload_image(image_files[0], alt_text=focus_keyword)
    if media_id == -1:
        return jsonify({"ok": False, "error": "이미지 업로드 실패"}), 500

    # 콘텐츠 최적화
    html_content = ensure_focus_keyword_in_content(html_content, focus_keyword)
    html_content = ensure_focus_keyword_in_subheading(html_content, focus_keyword)
    if image_url:
        html_content = inject_focus_keyword_image(html_content, focus_keyword, image_url)
    html_content = inject_external_link(html_content)
    wp_content = f"<!-- wp:html -->\n{html_content}\n<!-- /wp:html -->"

    # 태그
    tag_ids = get_or_create_tags(seo["tags"]) if seo["tags"] else []

    # 글 발행
    post_data = {
        "title": title,
        "content": wp_content,
        "status": status,
        "slug": seo["slug"],
        "featured_media": media_id,
        "categories": [CONFIG["category_id"]],
        "author": CONFIG["author_id"],
    }
    if tag_ids:
        post_data["tags"] = tag_ids

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

    return jsonify({
        "ok": True,
        "post_id": post_id,
        "url": result["link"],
        "seo": seo,
    })


if __name__ == "__main__":
    port = 5000
    print(f"\n  워드프레스 자동 발행 서버 시작")
    print(f"  http://localhost:{port}\n")
    threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    app.run(host="127.0.0.1", port=port, debug=False)
