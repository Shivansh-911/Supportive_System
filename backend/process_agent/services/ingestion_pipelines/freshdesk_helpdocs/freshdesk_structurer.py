from bs4 import BeautifulSoup, NavigableString, Tag
from core.services.utils.logger import get_logger

logger = get_logger(__name__)

_HEADING_TAGS   = ['h1', 'h2', 'h3', 'h4']
_STRATEGY_AWARE = 'heading_aware'
_STRATEGY_RECUR = 'recursive'


class FreshdeskStructurer:

    def structure(self, cleaned_html: str) -> tuple[dict, str]:
        soup = BeautifulSoup(cleaned_html, 'lxml')
        sections = []
        current_heading: str | None = None
        current_body: list[str] = []

        root = soup.body if soup.body else soup

        for el in root.children:
            if isinstance(el, NavigableString):
                text = el.strip()
                if text:
                    current_body.append(str(el))
            elif isinstance(el, Tag):
                if self._is_heading(el):
                    if current_body:
                        sections.append(self._build_section(current_heading, current_body))
                    elif current_heading is not None:
                        sections.append(self._build_section(current_heading, []))
                    current_heading = el.get_text(" ", strip=True)
                    current_body = []
                else:
                    current_body.append(str(el))

        if current_body:
            sections.append(self._build_section(current_heading, current_body))

        has_headings = any(s['heading_text'] is not None for s in sections)
        chunk_strategy = _STRATEGY_AWARE if has_headings else _STRATEGY_RECUR

        structured_json = {'sections': sections, 'has_headings': has_headings}
        logger.info("freshdesk_structurer completed | sections=%d has_headings=%s strategy=%s",
                    len(sections), has_headings, chunk_strategy)
        return structured_json, chunk_strategy

    def _build_section(self, heading: str | None, body_parts: list[str]) -> dict:
        body_html = ''.join(body_parts)
        body_text = BeautifulSoup(body_html, 'lxml').get_text(separator=' ', strip=True)
        return {
            'heading_text': heading if heading else None,
            'body_html':    body_html,
            'body_text':    body_text,
        }

    def _is_heading(self, el: Tag) -> bool:
        if el.name in _HEADING_TAGS:
            return True
        if el.name == "p" and self._contains_bold_heading(el):
            return True
        return False

    def _contains_bold_heading(self, el: Tag) -> bool:
        text = el.get_text(" ", strip=True)

        if not text:
            return False

        if len(text) > 120:
            return False

        bold_tags = el.find_all(["strong", "b"])

        if not bold_tags:
            return False

        bold_text = " ".join(
            tag.get_text(" ", strip=True)
            for tag in bold_tags
        ).strip()

        return bold_text == text