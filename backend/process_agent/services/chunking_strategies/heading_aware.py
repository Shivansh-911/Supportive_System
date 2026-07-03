import tiktoken
from langchain_text_splitters import MarkdownHeaderTextSplitter

from process_agent.services.chunking_strategies.recursive import RecursiveChunker
from constants import (
    CHUNK_MIN_TOKENS,
    CHUNK_SINGLE_MAX_TOKENS,
    CHUNK_TOKENIZER_ENCODING,
)
from core.services.utils.logger import get_logger

logger = get_logger(__name__)


HEADERS_TO_SPLIT_ON = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
    ("####", "h4"),
    ("#####", "h5"),
    ("######", "h6"),
]


class HeadingAwareChunker:

    STRATEGY = "heading_aware"

    def __init__(self) -> None:
        self._encoder = tiktoken.get_encoding(CHUNK_TOKENIZER_ENCODING)
        self._splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=HEADERS_TO_SPLIT_ON,
            strip_headers=False,
        )
        self._fallback = RecursiveChunker()

    def heading_aware(self, markdown: str) -> list[tuple[str, int, str]]:
        if not markdown or not markdown.strip():
            return []

        stripped = markdown.strip()
        total_tokens = self._count_tokens(markdown)
        if total_tokens < CHUNK_SINGLE_MAX_TOKENS:
            return [(stripped, self._count_tokens(stripped), self.STRATEGY)]

        sections = [
            doc.page_content.strip()                                    # doc is a langchain document object
            for doc in self._splitter.split_text(markdown)
            if doc.page_content and doc.page_content.strip()
        ]
        if len(sections) <= 1:
            logger.warning("heading_aware: no headings found in markdown above %d tokens", CHUNK_SINGLE_MAX_TOKENS)
            return self._fallback.recursive(stripped)

        return self._merge_small_sections(sections)

    def _count_tokens(self, text: str) -> int:
        return len(self._encoder.encode(text))

    def _merge_small_sections(self, sections: list[str]) -> list[tuple[str, int, str]]:
        merged: list[tuple[str, int, str]] = []
        buffer: str | None = None
        buffer_tokens = 0

        for section in sections:
            buffer = section if buffer is None else f"{buffer}\n\n{section}"
            buffer_tokens = self._count_tokens(buffer)
            if buffer_tokens >= CHUNK_MIN_TOKENS:
                merged.append((buffer, buffer_tokens, self.STRATEGY))
                buffer = None
                buffer_tokens = 0

        if buffer is not None:
            if merged:
                last_text, _, _ = merged[-1]
                combined = f"{last_text}\n\n{buffer}"
                merged[-1] = (combined, self._count_tokens(combined), self.STRATEGY)
            else:
                merged.append((buffer, buffer_tokens, self.STRATEGY))

        return merged



