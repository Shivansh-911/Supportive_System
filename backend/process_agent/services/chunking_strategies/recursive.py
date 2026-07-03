import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

from constants import (
    CHUNK_MIN_TOKENS,
    CHUNK_OVERLAP_TOKENS,
    CHUNK_SINGLE_MAX_TOKENS,
    CHUNK_TOKENIZER_ENCODING,
)


SENTENCE_AWARE_SEPARATORS = [
    "\n\n",
    "\n",
    ". ",
    "! ",
    "? ",
    "; ",
    ", ",
    " ",
    "",
]


class RecursiveChunker:

    STRATEGY = "recursive_fallback"

    def __init__(self) -> None:
        self._encoder = tiktoken.get_encoding(CHUNK_TOKENIZER_ENCODING)
        self._splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name=CHUNK_TOKENIZER_ENCODING,
            chunk_size=CHUNK_SINGLE_MAX_TOKENS,
            chunk_overlap=CHUNK_OVERLAP_TOKENS,
            separators=SENTENCE_AWARE_SEPARATORS,
            keep_separator=True,
        )

    def recursive(self, markdown: str) -> list[tuple[str, int, str]]:
        if not markdown or not markdown.strip():
            return []

        stripped = markdown.strip()
        total_tokens = self._count_tokens(markdown)
        if total_tokens < CHUNK_SINGLE_MAX_TOKENS:
            return [(stripped, self._count_tokens(stripped), self.STRATEGY)]

        sections = [
            chunk.strip()
            for chunk in self._splitter.split_text(stripped)
            if chunk and chunk.strip()
        ]
        chunks = [(section, self._count_tokens(section), self.STRATEGY) for section in sections]
        return self._absorb_small_tail(chunks)

    def _count_tokens(self, text: str) -> int:
        return len(self._encoder.encode(text))

    def _absorb_small_tail(self, chunks: list[tuple[str, int, str]]) -> list[tuple[str, int, str]]:
        if len(chunks) < 2:
            return chunks
        last_text, last_tokens, _ = chunks[-1]
        if last_tokens < CHUNK_MIN_TOKENS:
            chunks.pop()
            prev_text, _, prev_strategy = chunks[-1]
            combined = f"{prev_text}\n\n{last_text}"
            chunks[-1] = (combined, self._count_tokens(combined), prev_strategy)
        return chunks
