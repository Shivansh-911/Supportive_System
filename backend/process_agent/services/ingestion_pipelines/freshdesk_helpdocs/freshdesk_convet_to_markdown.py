import re

import html2text

from core.services.utils.logger import get_logger

logger = get_logger(__name__)


_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+\S", re.MULTILINE)


class FreshdeskConvertToMarkdown:

    def toMarkdown(self, cleaned_html: str) -> tuple[str, bool]:
        converter = html2text.HTML2Text()
        converter.body_width = 0
        converter.ignore_links = False
        # converter.ignore_images = True

        markdown = converter.handle(cleaned_html).strip()
        has_headings = bool(_HEADING_RE.search(markdown))

        return markdown, has_headings
