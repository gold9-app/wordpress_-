"""
WordPress 글 자동 발행 스크립트 (Rank Math SEO 최적화)
사용법: publish 폴더 안에 글별 폴더를 만들고, 각 폴더에 HTML + 이미지 + meta.json을 넣은 뒤 실행
"""

import io
import json
import mimetypes
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")

import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).parent
load_dotenv(SCRIPT_DIR / ".env")

WP_URL = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")

PUBLISH_DIR = SCRIPT_DIR / "publish"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
HTML_EXTS = {".html", ".htm"}

# 전역 설정 로드
with open(SCRIPT_DIR / "config.json", encoding="utf-8") as f:
    CONFIG = json.load(f)


def check_config():
    missing = []
    if not WP_URL:
        missing.append("WP_URL")
    if not WP_USERNAME:
        missing.append("WP_USERNAME")
    if not WP_APP_PASSWORD:
        missing.append("WP_APP_PASSWORD")
    if missing:
        print(f"[오류] .env 파일에 다음 값이 없습니다: {', '.join(missing)}")
        sys.exit(1)


def find_files(folder: Path, extensions: set):
    return [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in extensions]


def strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html).strip()


def make_slug(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s가-힣-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def load_meta(folder: Path) -> dict:
    meta_path = folder / "meta.json"
    if meta_path.exists():
        with open(meta_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def wrap_wp_html_block(html_content: str) -> str:
    """HTML을 WordPress 사용자 정의 HTML 블록으로 감싸기"""
    return f"<!-- wp:html -->\n{html_content}\n<!-- /wp:html -->"


def inject_focus_keyword_image(html_content: str, focus_keyword: str, image_url: str) -> str:
    """콘텐츠 내 포커스 키워드를 alt 텍스트로 가진 이미지를 첫 번째 태그 뒤에 삽입"""
    img_tag = f'<img src="{image_url}" alt="{focus_keyword}" style="width:100%; height:auto;" />'

    # 첫 번째 닫는 태그 뒤에 이미지 삽입
    match = re.search(r"(</[^>]+>)", html_content)
    if match:
        pos = match.end()
        return html_content[:pos] + "\n" + img_tag + "\n" + html_content[pos:]
    return img_tag + "\n" + html_content


def inject_external_link(html_content: str) -> str:
    """콘텐츠 끝에 작성자 인스타그램 dofollow 링크 삽입"""
    instagram_url = CONFIG.get("author_instagram", "")
    if not instagram_url:
        return html_content
    # 이미 인스타그램 링크가 있으면 스킵
    if "instagram.com" in html_content:
        return html_content
    link_html = (
        f'<p>더 많은 건강 정보는 '
        f'<a href="{instagram_url}" target="_blank">응석 김 인스타그램</a>'
        f'에서 확인하세요.</p>'
    )
    return html_content + "\n" + link_html


def ensure_focus_keyword_in_content(html_content: str, focus_keyword: str) -> str:
    """콘텐츠 시작 부분에 포커스 키워드가 없으면 추가"""
    plain_start = strip_html(html_content[:500])
    if focus_keyword.lower() in plain_start.lower():
        return html_content

    # 첫 번째 태그 앞에 포커스 키워드 포함 문단 추가
    keyword_intro = f"<p>{focus_keyword}에 대해 알아보겠습니다.</p>\n"
    return keyword_intro + html_content


def ensure_focus_keyword_in_subheading(html_content: str, focus_keyword: str) -> str:
    """h2/h3 부제목 중 하나 이상에 포커스 키워드가 포함되도록 보장"""
    # 이미 부제목에 포커스 키워드가 있는지 확인
    subheading_pattern = re.compile(r"<h[23][^>]*>(.*?)</h[23]>", re.IGNORECASE | re.DOTALL)
    subheadings = subheading_pattern.findall(html_content)

    for sh in subheadings:
        if focus_keyword.lower() in strip_html(sh).lower():
            return html_content

    # 첫 번째 h2에 포커스 키워드 추가
    def add_keyword_to_first_h2(match):
        tag = match.group(0)
        inner = match.group(1)
        return tag.replace(inner, f"{focus_keyword} - {inner}", 1)

    result, count = re.subn(
        r"<h2[^>]*>(.*?)</h2>",
        add_keyword_to_first_h2,
        html_content,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return result if count > 0 else html_content


def extract_focus_keyword(title: str) -> str:
    """제목에서 핵심 주제어만 추출 (예: '계란에 대해 잘못 알려진 6가지 상식' → '계란')"""
    keyword = title

    # 숫자+가지 패턴 제거 (예: "6가지", "10가지")
    keyword = re.sub(r"\d+\s*가지", "", keyword)

    # 제거할 표현들 (긴 것부터 매칭)
    remove_patterns = [
        # 구문
        "에 대해 잘못 알려진", "에 대해 알려진", "에 대해 알아야 할",
        "꼭 알아야 할", "알아야 할", "꼭 알아야할", "반드시 알아야 할",
        "에 대해", "에 대한", "에서의", "에서", "으로의", "으로", "를 위한", "을 위한",
        "하는 방법", "하는 법", "하는법", "알아보기", "알아보자",
        # 일반 서술 명사
        "상식", "방법", "효과", "원인", "증상", "종류", "차이", "차이점",
        "비교", "추천", "정리", "총정리", "리뷰", "후기",
        "장점", "단점", "장단점", "주의사항", "부작용", "특징",
        "가이드", "완벽 가이드", "핵심 정리",
        "진실", "오해", "팩트", "팩트체크", "궁금증",
        # 수식어
        "잘못 알려진", "잘못알려진", "최신", "최고의", "효과적인",
        "올바른", "정확한", "꼭 필요한", "반드시", "꼭",
    ]
    for p in remove_patterns:
        keyword = keyword.replace(p, "")

    # 남은 공백/특수문자 정리
    keyword = re.sub(r"[|,\-~:?!]", "", keyword)
    keyword = re.sub(r"\s+", " ", keyword).strip()

    return keyword if keyword else title


def build_seo_fields(title: str, html_content: str, meta: dict) -> dict:
    """Rank Math SEO 필드 생성 - 모든 점수 항목 반영"""
    focus_keyword = meta.get("focus_keyword", "")
    if not focus_keyword:
        focus_keyword = extract_focus_keyword(title)

    plain_text = strip_html(html_content)

    # 1) SEO 제목에 포커스 키워드 포함
    seo_title = meta.get("seo_title", "")
    if not seo_title:
        seo_title = f"{title} | {focus_keyword} - {CONFIG['site_name']}"
        # 제목에 이미 키워드가 포함되어 있으면 중복 방지
        if focus_keyword.lower() in title.lower():
            seo_title = f"{title} - {CONFIG['site_name']}"

    # 2) 메타 디스크립션에 포커스 키워드 포함
    description = meta.get("description", "")
    if not description:
        desc_text = plain_text[:300].replace("\n", " ").strip()
        last_period = desc_text[:140].rfind(".")
        if last_period > 50:
            description = desc_text[:last_period + 1]
        else:
            description = desc_text[:140]
        # 디스크립션에 키워드가 없으면 앞에 추가
        if focus_keyword.lower() not in description.lower():
            description = f"{focus_keyword} - {description}"
    # 155자 제한
    if len(description) > 155:
        description = description[:152] + "..."

    # 3) URL 슬러그에 포커스 키워드 포함
    slug = meta.get("slug", make_slug(focus_keyword))

    # 태그
    tags = meta.get("tags", [])

    return {
        "focus_keyword": focus_keyword,
        "description": description,
        "seo_title": seo_title,
        "slug": slug,
        "tags": tags,
    }


def get_or_create_tags(tag_names: list) -> list:
    tag_ids = []
    for name in tag_names:
        resp = requests.get(
            f"{WP_URL}/wp-json/wp/v2/tags",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            params={"search": name},
            timeout=10,
        )
        if resp.status_code == 200 and resp.json():
            for tag in resp.json():
                if tag["name"].lower() == name.lower():
                    tag_ids.append(tag["id"])
                    break
            else:
                resp2 = requests.post(
                    f"{WP_URL}/wp-json/wp/v2/tags",
                    auth=(WP_USERNAME, WP_APP_PASSWORD),
                    json={"name": name},
                    timeout=10,
                )
                if resp2.status_code in (200, 201):
                    tag_ids.append(resp2.json()["id"])
        else:
            resp2 = requests.post(
                f"{WP_URL}/wp-json/wp/v2/tags",
                auth=(WP_USERNAME, WP_APP_PASSWORD),
                json={"name": name},
                timeout=10,
            )
            if resp2.status_code in (200, 201):
                tag_ids.append(resp2.json()["id"])
    return tag_ids


def upload_image(image_path: Path, alt_text: str = "") -> tuple:
    """이미지 업로드 후 (media_id, image_url) 반환. alt_text로 대체 텍스트 설정"""
    mime_type = mimetypes.guess_type(str(image_path))[0] or "image/jpeg"
    filename = image_path.name
    ascii_filename = f"image{image_path.suffix}"

    print(f"  이미지 업로드 중... ({filename})")

    resp = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        headers={
            "Content-Disposition": f'attachment; filename="{ascii_filename}"',
            "Content-Type": mime_type,
        },
        data=image_path.read_bytes(),
        timeout=60,
    )

    if resp.status_code not in (200, 201):
        print(f"[오류] 이미지 업로드 실패 (HTTP {resp.status_code})")
        print(f"  응답: {resp.text[:300]}")
        return -1, ""

    media_data = resp.json()
    media_id = media_data["id"]
    image_url = media_data.get("source_url", "")
    print(f"  이미지 업로드 완료 (media ID: {media_id})")

    # alt 텍스트(포커스 키워드) 설정
    if alt_text:
        requests.post(
            f"{WP_URL}/wp-json/wp/v2/media/{media_id}",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json={"alt_text": alt_text},
            timeout=10,
        )
        print(f"  이미지 alt 텍스트 설정: {alt_text}")

    return media_id, image_url


def validate_folder(folder: Path):
    html_files = find_files(folder, HTML_EXTS)
    image_files = find_files(folder, IMAGE_EXTS)

    errors = []
    if len(html_files) == 0:
        errors.append("HTML 파일 없음")
    elif len(html_files) > 1:
        errors.append(f"HTML 파일 {len(html_files)}개 (1개만)")
    if len(image_files) == 0:
        errors.append("이미지 파일 없음")
    elif len(image_files) > 1:
        errors.append(f"이미지 파일 {len(image_files)}개 (1개만)")

    if errors:
        return None, None, errors
    return html_files[0], image_files[0], []


def publish_one(folder: Path, title: str, status: str):
    html_file, image_file, errors = validate_folder(folder)
    if errors:
        print(f"  [건너뜀] {folder.name}: {', '.join(errors)}")
        return False

    html_content = html_file.read_text(encoding="utf-8")
    meta = load_meta(folder)
    seo = build_seo_fields(title, html_content, meta)

    focus_keyword = seo["focus_keyword"]

    # --- Rank Math 점수 최적화 ---

    # 1) 이미지 업로드 (alt 텍스트 = 포커스 키워드)
    media_id, image_url = upload_image(image_file, alt_text=focus_keyword)
    if media_id == -1:
        return False

    # 2) 콘텐츠 시작 부분에 포커스 키워드 보장
    html_content = ensure_focus_keyword_in_content(html_content, focus_keyword)

    # 3) 부제목(h2/h3)에 포커스 키워드 보장
    html_content = ensure_focus_keyword_in_subheading(html_content, focus_keyword)

    # 4) 포커스 키워드를 alt로 가진 이미지를 콘텐츠에 삽입
    if image_url:
        html_content = inject_focus_keyword_image(html_content, focus_keyword, image_url)

    # 5) 외부 dofollow 링크 삽입 (인스타그램)
    html_content = inject_external_link(html_content)

    # 6) WordPress HTML 블록으로 감싸기
    wp_content = wrap_wp_html_block(html_content)

    print(f"  Focus Keyword: {focus_keyword}")
    print(f"  SEO 제목: {seo['seo_title']}")
    print(f"  슬러그: {seo['slug']}")
    print(f"  디스크립션: {seo['description'][:60]}...")
    if seo["tags"]:
        print(f"  태그: {', '.join(seo['tags'])}")

    # 태그 처리
    tag_ids = get_or_create_tags(seo["tags"]) if seo["tags"] else []

    # 글 발행
    print("  글 발행 중...")
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

    resp = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        json=post_data,
        timeout=30,
    )

    if resp.status_code not in (200, 201):
        print(f"  [오류] 글 발행 실패 (HTTP {resp.status_code})")
        print(f"  응답: {resp.text[:500]}")
        return False

    result = resp.json()
    post_id = result["id"]
    print(f"  글 생성 완료 (ID: {post_id})")

    # --- Rank Math 메타 설정 (전용 API) ---
    print("  Rank Math SEO 설정 중...")
    rm_meta = {
        "rank_math_title": seo["seo_title"],
        "rank_math_description": seo["description"],
        "rank_math_focus_keyword": seo["focus_keyword"],
        "rank_math_robots": "index,follow",
    }
    rm_resp = requests.post(
        f"{WP_URL}/wp-json/rankmath/v1/updateMeta",
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        json={
            "objectType": "post",
            "objectID": post_id,
            "meta": rm_meta,
        },
        timeout=15,
    )
    if rm_resp.status_code == 200:
        print("  Rank Math 메타 설정 완료")
    else:
        print(f"  [경고] Rank Math 메타 설정 실패 (HTTP {rm_resp.status_code})")
        print(f"  응답: {rm_resp.text[:300]}")

    # --- Rank Math 스키마 설정 (전용 API) ---
    print("  Rank Math 스키마 설정 중...")
    schema_data = {
        "objectType": "post",
        "objectID": post_id,
        "schemas": {
            "new-1": {
                "@type": "Article",
                "metadata": {
                    "title": "Article",
                    "type": "template",
                    "isPrimary": True,
                },
                "headline": "%seo_title%",
                "description": "%seo_description%",
                "datePublished": "%date(Y-m-dTH:i:sP)%",
                "dateModified": "%modified(Y-m-dTH:i:sP)%",
                "author": {
                    "@type": "Person",
                    "name": "%name%"
                },
            }
        },
    }
    schema_resp = requests.post(
        f"{WP_URL}/wp-json/rankmath/v1/updateSchemas",
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        json=schema_data,
        timeout=15,
    )
    if schema_resp.status_code == 200:
        print("  Rank Math 스키마 설정 완료")
    else:
        print(f"  [경고] Rank Math 스키마 설정 실패 (HTTP {schema_resp.status_code})")
        print(f"  응답: {schema_resp.text[:300]}")

    print(f"  발행 완료! -> {result['link']}")
    return True


def main():
    check_config()

    if not PUBLISH_DIR.exists():
        PUBLISH_DIR.mkdir()
        print(f"[안내] publish 폴더를 생성했습니다: {PUBLISH_DIR}")
        print("  글별 폴더를 만들고 HTML + 이미지 + meta.json을 넣은 뒤 다시 실행하세요.")
        sys.exit(0)

    folders = sorted([f for f in PUBLISH_DIR.iterdir() if f.is_dir()])

    if not folders:
        print("[오류] publish 폴더 안에 글 폴더가 없습니다.")
        print(f"  경로: {PUBLISH_DIR}")
        sys.exit(1)

    # 폴더 목록 표시
    print(f"\n  발견된 글 폴더 ({len(folders)}개):")
    print(f"  {'='*40}")
    valid_folders = []
    for i, folder in enumerate(folders, 1):
        html_file, image_file, errors = validate_folder(folder)
        has_meta = (folder / "meta.json").exists()
        if errors:
            status_mark = f"[X] {', '.join(errors)}"
        else:
            img_mark = image_file.name
            meta_mark = " + meta.json" if has_meta else ""
            status_mark = f"[O] {html_file.name} + {img_mark}{meta_mark}"
            valid_folders.append(folder)
        print(f"  {i}. {folder.name}")
        print(f"     {status_mark}")
    print()

    if not valid_folders:
        print("[오류] 발행 가능한 폴더가 없습니다.")
        sys.exit(1)

    # 선택
    print("  발행할 폴더 번호를 입력하세요.")
    print("  (여러 개: 1,3,5 / 전체: a)")
    choice = input("  선택: ").strip().lower()

    if choice == "a":
        selected = list(range(len(folders)))
    else:
        try:
            selected = [int(x.strip()) - 1 for x in choice.split(",")]
        except ValueError:
            print("[오류] 올바른 번호를 입력해주세요.")
            sys.exit(1)

    status_input = input("  바로 발행할까요? (Y/n): ").strip().lower()
    status = "draft" if status_input == "n" else "publish"

    print(f"\n{'='*50}")
    success = 0
    fail = 0

    for idx in selected:
        if idx < 0 or idx >= len(folders):
            print(f"  [건너뜀] {idx+1}번: 없는 번호")
            fail += 1
            continue

        folder = folders[idx]
        title = folder.name
        print(f"\n>> [{idx+1}] {title}")

        if publish_one(folder, title, status):
            success += 1
        else:
            fail += 1

    print(f"\n{'='*50}")
    print(f"  완료: 성공 {success}개 / 실패 {fail}개")


if __name__ == "__main__":
    main()
