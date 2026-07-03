import hashlib
from pathlib import PurePosixPath
from urllib.parse import urlparse

from markdown_it import MarkdownIt

from constants import CONTENT_HASH_LENGTH


class FreshdeskHelper:

    _IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp",".gif", ".svg", ".avif", ".bmp", ".tiff", ".tif"})

    def _is_image_url(self, url: str) -> bool:
        path = urlparse(url).path
        return PurePosixPath(path).suffix.lower() in self._IMAGE_EXTENSIONS

    def _get_fenced_code_lines(self, document: str) -> set[int]:
        fenced_lines: set[int] = set()
        for token in MarkdownIt().parse(document):
            if token.type == "fence" and token.map:
                fenced_lines.update(range(token.map[0], token.map[1]))
        return fenced_lines

    def _replace_images_in_line(self,line: str,image_map: dict[int, str],index: list[int]) -> str:
        """
        Scan a single line character-by-character.
        Every Markdown image ``![alt](url)`` whose URL resolves to an image
        file is replaced with ``[Img N]`` or ``[Img N: alt]``, and the
        original URL is stored in *image_map* keyed by the assigned index.

        Non-image links and malformed image syntax are left untouched.
        Backslash-escaped characters inside the URL (``\\X → X``) are
        unescaped before storing so the saved URL is always valid.
        """
        output: list[str] = []
        pos = 0
        line_len = len(line)

        while pos < line_len:

            # --- fast path: not the start of an image link ----------------
            if line[pos] != '!' or pos + 1 >= line_len or line[pos + 1] != '[':
                output.append(line[pos])
                pos += 1
                continue

            # --- scan alt text: ![ ... ] ----------------------------------
            alt_start = pos + 2
            alt_end = alt_start
            while alt_end < line_len and line[alt_end] != ']':
                alt_end += 1

            # no closing `]` or the char after it isn't `(`
            if alt_end >= line_len or alt_end + 1 >= line_len or line[alt_end + 1] != '(':
                output.append(line[pos])
                pos += 1
                continue

            alt_text = line[alt_start:alt_end]

            # --- scan URL: ( ... ) with backslash-escape handling ---------
            url_start = alt_end + 2
            url_chars: list[str] = []
            url_pos = url_start

            while url_pos < line_len:
                ch = line[url_pos]
                if ch == '\\' and url_pos + 1 < line_len:   # \X → X (unescape)
                    url_chars.append(line[url_pos + 1])
                    url_pos += 2
                elif ch == ')':
                    break
                else:
                    url_chars.append(ch)
                    url_pos += 1

            # no closing `)`
            if url_pos >= line_len or line[url_pos] != ')':
                output.append(line[pos])
                pos += 1
                continue

            url = ''.join(url_chars)
            end_pos = url_pos + 1   # position just after the closing `)`

            # --- decide: image link or regular link -----------------------
            if not self._is_image_url(url):
                output.append(line[pos:end_pos])
                pos = end_pos
                continue

            index[0] += 1
            image_map[index[0]] = url
            alt = alt_text.strip()
            token = f"[Img {index[0]}: {alt}]" if alt else f"[Img {index[0]}]"
            output.append(token)
            pos = end_pos

        return ''.join(output)

    def replace_image_links(self, document: str) -> tuple[str, dict[int, str]]:
        """
        Replace all Markdown image links in *document* with numbered tokens
        and return the processed document together with a URL map.

        Lines inside fenced code blocks are left completely untouched.

        Returns:
            processed_document: original text with image links replaced.
            image_map: ``{token_index: original_url}`` for every replaced image.
        """
        fenced_lines = self._get_fenced_code_lines(document)
        image_map: dict[int, str] = {}
        index = [0]     # wrapped in a list so the helper method can mutate it

        processed_lines = [
            line
            if line_no in fenced_lines
            else self._replace_images_in_line(line, image_map, index)
            for line_no, line in enumerate(document.splitlines(keepends=True))
        ]
        return ''.join(processed_lines), image_map

    def generate_hash(self, raw_payload: dict) -> str:
        content = raw_payload.get('desc_un_html')
        if not content:
            raise ValueError("Cannot generate content hash: 'desc_un_html' missing or empty in payload.")
        return hashlib.sha256(content.encode()).hexdigest()[:CONTENT_HASH_LENGTH]

    def metadata_creator(self, raw_payload: dict) -> tuple[dict, dict]:
        source_author = {
            'user_id':     raw_payload.get('user_id'),
            'modified_by': raw_payload.get('modified_by'),
        }

        source_metadata = {
            'category_id':   raw_payload.get('category_id'),
            'category_name': raw_payload.get('category_name'),
            'folder_id':     raw_payload.get('folder_id'),
            'folder_name':   raw_payload.get('folder_name'),
            'tags':          raw_payload.get('tags', []),
            'status':        raw_payload.get('status'),
            'art_type':      raw_payload.get('art_type'),
            'position':      raw_payload.get('position'),
            'hits':          raw_payload.get('hits'),
            'thumbs_up':     raw_payload.get('thumbs_up'),
            'thumbs_down':   raw_payload.get('thumbs_down'),
            'modified_at':   raw_payload.get('modified_at'),
            'seo_data':      raw_payload.get('seo_data', {}),
        }

        return source_author, source_metadata
