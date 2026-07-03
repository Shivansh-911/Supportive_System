import re

from bs4 import BeautifulSoup
from core.services.utils.logger import get_logger

logger = get_logger(__name__)


class FreshdeskCleaner:

    def clean(self, html: str) -> tuple[str, str]:
        if not html:
            raise ValueError("Cannot clean: html is missing or empty.")

        soup = BeautifulSoup(html, 'lxml')

        soup = soup.body if soup.body else soup

        # self._drop_tags(soup, ['figure'])
        # print(soup)
        self._strip_data_attrs(soup)
        self._promote_heading_like_paragraphs(soup)
        self._unwrap_tags(soup, ['span', 'font','strong','figure'])
        self._decode_nbsp(soup)
        self._remove_empty_nodes(soup)

        cleaned_html = str(soup)
        cleaned_text = re.sub(r'\s+', ' ', soup.get_text(separator=' ')).strip()
        logger.info("freshdesk_cleaner completed | text_length=%d", len(cleaned_text))
        return cleaned_html, cleaned_text

    def _drop_tags(self, soup: BeautifulSoup, tags: list[str]) -> None:
        for tag in tags:
            for el in soup.find_all(tag):
                el.decompose()

    def _strip_data_attrs(self, soup: BeautifulSoup) -> None:
        for el in soup.find_all(True):
            for attr in list(el.attrs):     #converts el.attrs a dict to a list as we cannot safetly delete keys while navigatiing in a dict
                if attr.startswith('data-') or attr in ('dir', 'style','class'):
                    del el[attr]

    def _unwrap_tags(self, soup: BeautifulSoup, tags: list[str]) -> None:
        for tag in tags:
            for el in soup.find_all(tag):
                el.unwrap()

    def _decode_nbsp(self, soup: BeautifulSoup) -> None:
        for el in soup.find_all(string=True):
            el.replace_with(el.replace('\xa0', ' '))

    def _remove_empty_nodes(self, soup: BeautifulSoup) -> None:
        for el in soup.find_all(True):
            # print(el)
            if el.name == "img":
                continue
            if el.find("img"):
                continue
            if not el.get_text(strip=True):
                el.decompose()

    def _promote_heading_like_paragraphs(self, soup: BeautifulSoup) -> None:
        for p in soup.find_all("p"):
            strong = p.find("strong")

            if not strong:
                continue
            text = p.get_text(" ", strip=True)
            # ignore long paragraphs
            if len(text) > 120:
                continue
            # paragraph should mostly consist of the strong text
            if text != strong.get_text(" ", strip=True):
                continue
            if p.find_parent(["li", "ul", "ol"]):
                continue

            h2 = soup.new_tag("h2")
            h2.string = text
            p.replace_with(h2)