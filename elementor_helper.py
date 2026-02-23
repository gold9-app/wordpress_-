"""
Elementor 통합 헬퍼 함수들
"""

import json
import re
from html.parser import HTMLParser


def html_to_elementor_text(html_content: str) -> str:
    """
    방법 1: HTML을 Elementor Text Editor 위젯용으로 정리
    - 가장 간단한 방법
    - Elementor의 텍스트 에디터가 HTML을 렌더링할 수 있도록 포맷팅
    """
    # WordPress 블록 코멘트 제거
    html_content = re.sub(r"<!-- wp:html -->", "", html_content)
    html_content = re.sub(r"<!-- /wp:html -->", "", html_content)
    return html_content.strip()


def create_elementor_template_with_content(html_content: str, image_url: str = "") -> str:
    """
    방법 2: Elementor JSON 구조 생성
    - HTML 콘텐츠를 Elementor 위젯으로 변환
    - 기본 템플릿 구조 생성
    """
    elementor_data = [
        # 섹션 1: 헤더 (대표 이미지)
        {
            "id": "header-section",
            "elType": "section",
            "settings": {
                "background_background": "classic",
                "background_image": {"url": image_url} if image_url else {},
                "background_position": "center center",
                "background_size": "cover",
                "padding": {"unit": "px", "top": "100", "right": "0", "bottom": "100", "left": "0"},
            },
            "elements": [],
        },
        # 섹션 2: 콘텐츠
        {
            "id": "content-section",
            "elType": "section",
            "settings": {
                "layout": "boxed",
                "content_width": {"unit": "px", "size": 800},
                "gap": "default",
                "padding": {"unit": "px", "top": "60", "right": "20", "bottom": "60", "left": "20"},
            },
            "elements": [
                {
                    "id": "content-column",
                    "elType": "column",
                    "settings": {"_column_size": 100},
                    "elements": [
                        {
                            "id": "html-widget",
                            "elType": "widget",
                            "widgetType": "html",
                            "settings": {
                                "html": html_to_elementor_text(html_content),
                            },
                        }
                    ],
                }
            ],
        },
    ]

    return json.dumps(elementor_data)


class HTMLToElementorParser(HTMLParser):
    """
    방법 3: HTML을 완전히 Elementor 위젯으로 변환 (고급)
    - h1, h2, p, ul, ol 등을 각각의 Elementor 위젯으로 변환
    - 가장 깔끔하지만 복잡함
    """

    def __init__(self):
        super().__init__()
        self.elements = []
        self.current_column = None
        self.text_buffer = ""
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag

    def handle_endtag(self, tag):
        if self.text_buffer.strip():
            widget = self._create_widget(tag, self.text_buffer.strip())
            if widget:
                self.elements.append(widget)
        self.text_buffer = ""
        self.current_tag = None

    def handle_data(self, data):
        self.text_buffer += data

    def _create_widget(self, tag, content):
        """태그에 따라 적절한 Elementor 위젯 생성"""
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            return {
                "elType": "widget",
                "widgetType": "heading",
                "settings": {
                    "title": content,
                    "header_size": tag,
                },
            }
        elif tag == "p":
            return {
                "elType": "widget",
                "widgetType": "text-editor",
                "settings": {
                    "editor": content,
                },
            }
        elif tag == "img":
            return {
                "elType": "widget",
                "widgetType": "image",
                "settings": {
                    "image": {"url": content},
                },
            }
        return None

    def get_elementor_structure(self):
        """최종 Elementor JSON 구조 반환"""
        return [
            {
                "id": "content-section",
                "elType": "section",
                "elements": [
                    {
                        "id": "column",
                        "elType": "column",
                        "settings": {"_column_size": 100},
                        "elements": self.elements,
                    }
                ],
            }
        ]


def html_to_elementor_widgets(html_content: str) -> str:
    """
    HTML을 Elementor 위젯 구조로 완전 변환
    """
    parser = HTMLToElementorParser()
    parser.feed(html_content)
    return json.dumps(parser.get_elementor_structure())


def set_elementor_template(post_id: int, template_id: int, wp_url: str, auth: tuple) -> bool:
    """
    특정 글에 Elementor 템플릿 적용
    """
    import requests

    try:
        # Elementor 템플릿 메타 설정
        resp = requests.post(
            f"{wp_url}/wp-json/wp/v2/posts/{post_id}",
            auth=auth,
            json={
                "meta": {
                    "_elementor_edit_mode": "builder",
                    "_elementor_template_type": "wp-post",
                    "_elementor_version": "3.16.0",
                    "_wp_page_template": f"elementor-{template_id}",
                }
            },
            timeout=15,
        )
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"Elementor 템플릿 설정 실패: {e}")
        return False


def enable_elementor_for_post(
    post_id: int,
    html_content: str,
    wp_url: str,
    auth: tuple,
    method: str = "simple",
    template_id: int = None,
) -> bool:
    """
    글에 Elementor 활성화

    Args:
        post_id: WordPress 글 ID
        html_content: HTML 콘텐츠
        wp_url: WordPress URL
        auth: (username, password) 튜플
        method: 'simple' (HTML 위젯), 'template' (템플릿 사용), 'full' (완전 변환)
        template_id: Elementor 템플릿 ID (method='template'일 때 필요)
    """
    import requests

    try:
        if method == "simple":
            # 방법 1: 간단히 Elementor 활성화 + HTML 위젯
            elementor_data = create_elementor_template_with_content(html_content)
        elif method == "template" and template_id:
            # 방법 2: 기존 템플릿 사용
            return set_elementor_template(post_id, template_id, wp_url, auth)
        elif method == "full":
            # 방법 3: 완전 변환
            elementor_data = html_to_elementor_widgets(html_content)
        else:
            return False

        # Elementor 데이터 저장
        resp = requests.post(
            f"{wp_url}/wp-json/wp/v2/posts/{post_id}",
            auth=auth,
            json={
                "meta": {
                    "_elementor_edit_mode": "builder",
                    "_elementor_data": elementor_data,
                    "_elementor_template_type": "wp-post",
                    "_elementor_version": "3.16.0",
                }
            },
            timeout=15,
        )
        return resp.status_code in (200, 201)

    except Exception as e:
        print(f"Elementor 활성화 실패: {e}")
        return False
