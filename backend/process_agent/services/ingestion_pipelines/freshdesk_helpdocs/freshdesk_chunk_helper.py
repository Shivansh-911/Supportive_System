import re

import tiktoken

from constants import CHUNK_TOKENIZER_ENCODING


class FreshdeskChunkHelper:

    _IMG_REF_PATTERN = re.compile(r"\[Img (\d+)(?::[^\]]*)?\]")

    def __init__(self) -> None:
        self._encoder = tiktoken.get_encoding(CHUNK_TOKENIZER_ENCODING)

    def build_chunk_image_map(
        self,
        chunk: str,
        document_image_map: dict[int, str],
    ) -> dict[int, str]:
        chunk_image_map: dict[int, str] = {}
        for match in self._IMG_REF_PATTERN.finditer(chunk):
            index = int(match.group(1))
            if index in document_image_map:
                chunk_image_map[index] = document_image_map[index]
        return chunk_image_map

    def build_chunk_metadata(
        self,
        source_metadata: dict,
        source_author:dict,
        image_map: dict[int, str],
    ) -> dict:
        return {
            'category_id': source_metadata.get('category_id'),
            'folder_id':   source_metadata.get('folder_id'),
            'tags':        source_metadata.get('tags', []),
            'modified_at': source_metadata.get('modified_at'),
            'user_id':     source_author.get('user_id'),
            'modified_by': source_author.get('modified_by'),
            'image_map':   image_map,
        }

    def build_searchable_chunk(
        self,
        category_name: str | None,
        folder_name: str | None,
        source_title: str | None,
        context_prefix: str | None,
        replaced_text: str | None,
    ) -> tuple[str, int]:
        searchable_chunk = (
            f"Category: {category_name if category_name else 'None'} | "
            f"Folder: {folder_name if folder_name else 'None'} | "
            f"Title: {source_title if source_title else 'None'} | "
            f"Prefix: {context_prefix if context_prefix else 'None'} | "
            f"{replaced_text if replaced_text else 'None'}"
        )
        token_count = len(self._encoder.encode(searchable_chunk))
        return searchable_chunk, token_count
