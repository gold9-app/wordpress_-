"""
Elementor 통합 - 프로급 자동 디자인 생성
무료 Elementor 버전에서도 작동하는 멋진 레이아웃 자동 생성
"""

import json
import re
import uuid


def generate_id():
    """고유 ID 생성"""
    return str(uuid.uuid4())[:8]


def create_pro_elementor_layout(
    title: str,
    html_content: str,
    image_url: str = "",
    author_name: str = "항노화 김응석 박사",
    instagram_url: str = "https://www.instagram.com/medi_eungsuk/",
    post_date: str = "",
) -> str:
    """
    프로급 Elementor 레이아웃 자동 생성

    구조:
    1. 헤더 섹션 (그라디언트 배경 + 제목 + 메타 정보)
    2. 본문 섹션 (HTML 콘텐츠)
    3. CTA 섹션 (저자 소개 + 인스타그램)
    """

    # HTML 정리
    clean_html = re.sub(r"<!-- wp:html -->", "", html_content)
    clean_html = re.sub(r"<!-- /wp:html -->", "", clean_html)
    clean_html = clean_html.strip()

    elementor_data = [
        # ═══════════════════════════════════════════
        # 섹션 1: 헤더 (그라디언트 배경)
        # ═══════════════════════════════════════════
        {
            "id": generate_id(),
            "elType": "section",
            "settings": {
                "background_background": "gradient",
                "background_color": "#1a73e8",
                "background_color_b": "#0d47a1",
                "background_gradient_angle": {"unit": "deg", "size": 135},
                "background_gradient_type": "linear",
                "padding": {
                    "unit": "px",
                    "top": "80",
                    "right": "20",
                    "bottom": "80",
                    "left": "20",
                    "isLinked": False,
                },
                # 모바일 반응형
                "padding_mobile": {
                    "unit": "px",
                    "top": "50",
                    "right": "16",
                    "bottom": "50",
                    "left": "16",
                    "isLinked": False,
                },
            },
            "elements": [
                {
                    "id": generate_id(),
                    "elType": "column",
                    "settings": {
                        "_column_size": 100,
                        "_inline_size": None,
                    },
                    "elements": [
                        # 제목
                        {
                            "id": generate_id(),
                            "elType": "widget",
                            "widgetType": "heading",
                            "settings": {
                                "title": title,
                                "header_size": "h1",
                                "align": "center",
                                "align_mobile": "center",
                                "title_color": "#FFFFFF",
                                "typography_typography": "custom",
                                "typography_font_family": "Noto Sans KR",
                                "typography_font_size": {"unit": "px", "size": 36},
                                "typography_font_size_mobile": {"unit": "px", "size": 24},
                                "typography_font_weight": "700",
                                "typography_line_height": {"unit": "em", "size": 1.3},
                            },
                        },
                        # 날짜/저자 정보
                        {
                            "id": generate_id(),
                            "elType": "widget",
                            "widgetType": "text-editor",
                            "settings": {
                                "editor": f'<p style="text-align: center; color: rgba(255,255,255,0.85); font-size: 14px; margin-top: 12px;">'
                                f'작성자: {author_name} | {post_date or "최근"}</p>',
                                "align": "center",
                            },
                        },
                    ],
                }
            ],
        },
        # ═══════════════════════════════════════════
        # 섹션 2: 본문 콘텐츠
        # ═══════════════════════════════════════════
        {
            "id": generate_id(),
            "elType": "section",
            "settings": {
                "layout": "boxed",
                "content_width": {"unit": "px", "size": 800},
                "gap": "default",
                "background_background": "classic",
                "background_color": "#FFFFFF",
                "padding": {
                    "unit": "px",
                    "top": "60",
                    "right": "40",
                    "bottom": "60",
                    "left": "40",
                    "isLinked": False,
                },
                "padding_mobile": {
                    "unit": "px",
                    "top": "40",
                    "right": "20",
                    "bottom": "40",
                    "left": "20",
                    "isLinked": False,
                },
                "margin": {
                    "unit": "px",
                    "top": "0",
                    "right": "0",
                    "bottom": "0",
                    "left": "0",
                },
            },
            "elements": [
                {
                    "id": generate_id(),
                    "elType": "column",
                    "settings": {"_column_size": 100},
                    "elements": [
                        # HTML 콘텐츠
                        {
                            "id": generate_id(),
                            "elType": "widget",
                            "widgetType": "html",
                            "settings": {
                                "html": f"""
<style>
/* 본문 스타일링 */
.article-content {{
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    color: #333333;
    line-height: 1.8;
}}

.article-content h2 {{
    font-size: 24px;
    font-weight: 700;
    color: #1a73e8;
    margin-top: 40px;
    margin-bottom: 16px;
    line-height: 1.4;
}}

.article-content h3 {{
    font-size: 20px;
    font-weight: 600;
    color: #333333;
    margin-top: 30px;
    margin-bottom: 14px;
}}

.article-content p {{
    font-size: 16px;
    margin-bottom: 16px;
    line-height: 1.8;
}}

.article-content ul, .article-content ol {{
    margin-left: 20px;
    margin-bottom: 20px;
}}

.article-content li {{
    margin-bottom: 8px;
}}

.article-content img {{
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin: 20px 0;
}}

.article-content a {{
    color: #1a73e8;
    text-decoration: none;
    border-bottom: 1px solid #1a73e8;
}}

.article-content a:hover {{
    color: #0d47a1;
    border-bottom-color: #0d47a1;
}}

/* 모바일 반응형 */
@media (max-width: 768px) {{
    .article-content h2 {{
        font-size: 20px;
        margin-top: 30px;
    }}
    .article-content h3 {{
        font-size: 18px;
        margin-top: 24px;
    }}
    .article-content p {{
        font-size: 15px;
    }}
}}
</style>

<div class="article-content">
{clean_html}
</div>
                                """,
                            },
                        }
                    ],
                }
            ],
        },
        # ═══════════════════════════════════════════
        # 섹션 3: CTA (Call To Action)
        # ═══════════════════════════════════════════
        {
            "id": generate_id(),
            "elType": "section",
            "settings": {
                "layout": "boxed",
                "content_width": {"unit": "px", "size": 800},
                "background_background": "classic",
                "background_color": "#f5f7fa",
                "padding": {
                    "unit": "px",
                    "top": "60",
                    "right": "40",
                    "bottom": "60",
                    "left": "40",
                    "isLinked": False,
                },
                "padding_mobile": {
                    "unit": "px",
                    "top": "40",
                    "right": "20",
                    "bottom": "40",
                    "left": "20",
                    "isLinked": False,
                },
            },
            "elements": [
                {
                    "id": generate_id(),
                    "elType": "column",
                    "settings": {"_column_size": 100},
                    "elements": [
                        # 저자 소개 박스
                        {
                            "id": generate_id(),
                            "elType": "widget",
                            "widgetType": "icon-box",
                            "settings": {
                                "selected_icon": {"value": "fas fa-user-md", "library": "fa-solid"},
                                "icon_color": "#1a73e8",
                                "icon_size": {"unit": "px", "size": 48},
                                "title_text": author_name,
                                "description_text": "대한줄기세포치료학회 회장<br>국제미용항노화학회 회장<br>대한비만건강학회 고문",
                                "title_color": "#333333",
                                "description_color": "#666666",
                                "content_vertical_alignment": "top",
                                "title_size": "large",
                                "box_background_color": "#FFFFFF",
                                "box_padding": {
                                    "unit": "px",
                                    "top": "30",
                                    "right": "30",
                                    "bottom": "30",
                                    "left": "30",
                                },
                                "box_border_radius": {"unit": "px", "size": 12},
                                "box_box_shadow_box_shadow_type": "yes",
                                "box_box_shadow_box_shadow": {
                                    "horizontal": 0,
                                    "vertical": 2,
                                    "blur": 12,
                                    "spread": 0,
                                    "color": "rgba(0,0,0,0.08)",
                                },
                            },
                        },
                        # 스페이서
                        {
                            "id": generate_id(),
                            "elType": "widget",
                            "widgetType": "spacer",
                            "settings": {
                                "space": {"unit": "px", "size": 30},
                                "space_mobile": {"unit": "px", "size": 20},
                            },
                        },
                        # 인스타그램 버튼
                        {
                            "id": generate_id(),
                            "elType": "widget",
                            "widgetType": "button",
                            "settings": {
                                "text": "더 많은 건강 정보 보기 →",
                                "link": {"url": instagram_url, "is_external": True, "nofollow": False},
                                "align": "center",
                                "size": "lg",
                                "button_background_color": "#E1306C",
                                "button_background_hover_color": "#C13584",
                                "button_text_color": "#FFFFFF",
                                "typography_typography": "custom",
                                "typography_font_family": "Noto Sans KR",
                                "typography_font_size": {"unit": "px", "size": 16},
                                "typography_font_weight": "600",
                                "border_radius": {"unit": "px", "size": 50},
                                "button_padding": {
                                    "unit": "px",
                                    "top": "16",
                                    "right": "40",
                                    "bottom": "16",
                                    "left": "40",
                                },
                                "hover_animation": "grow",
                            },
                        },
                    ],
                }
            ],
        },
    ]

    return json.dumps(elementor_data)


def enable_elementor_pro_layout(
    post_id: int,
    title: str,
    html_content: str,
    image_url: str,
    wp_url: str,
    auth: tuple,
    author_name: str = "항노화 김응석 박사",
    instagram_url: str = "https://www.instagram.com/medi_eungsuk/",
) -> bool:
    """
    프로급 Elementor 레이아웃 적용
    """
    import requests
    from datetime import datetime

    try:
        # 현재 날짜
        post_date = datetime.now().strftime("%Y년 %m월 %d일")

        # Elementor 데이터 생성
        elementor_data = create_pro_elementor_layout(
            title=title,
            html_content=html_content,
            image_url=image_url,
            author_name=author_name,
            instagram_url=instagram_url,
            post_date=post_date,
        )

        # HTML 블록 제거 (Rank Math 분석용)
        clean_content = html_content.replace("<!-- wp:html -->", "").replace("<!-- /wp:html -->", "").strip()

        # Elementor 메타 설정 + post_content 유지 (Rank Math용)
        resp = requests.post(
            f"{wp_url}/wp-json/wp/v2/posts/{post_id}",
            auth=auth,
            json={
                "content": clean_content,  # Rank Math가 분석할 수 있도록 HTML 블록 제거
                "meta": {
                    "_elementor_edit_mode": "builder",
                    "_elementor_data": elementor_data,
                    "_elementor_template_type": "wp-post",
                    "_elementor_version": "3.16.0",
                    "_elementor_page_settings": {
                        "custom_css": "",
                        "page_transition": "none",
                    },
                }
            },
            timeout=20,
        )

        if resp.status_code in (200, 201):
            print(f"  ✅ Elementor 프로급 레이아웃 적용 완료!")
            return True
        else:
            print(f"  ❌ Elementor 적용 실패 (HTTP {resp.status_code})")
            print(f"  응답: {resp.text[:200]}")
            return False

    except Exception as e:
        print(f"  ❌ Elementor 적용 중 오류: {e}")
        return False
