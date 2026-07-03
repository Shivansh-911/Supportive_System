import re

from core.models.chunk import Chunk
from core.services.utils.logger import get_logger

logger = get_logger(__name__)

# Captures (image_number, chunk_uuid) from [Img 2:uuid] or [Img 2: alt:uuid]
_IMG_MARKER = re.compile(
    r"\[Img (\d+)[^\]]*:([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\]"
)




class FinalAnswerService:
    def parse(self, answer: str, cited_chunks: list[dict]) -> dict:
        source_urls, chunk_data = self.fetch_chunk_data(cited_chunks)
        blocks = self.parse_blocks(answer, chunk_data)
        return {"blocks": blocks, "source_urls": source_urls}

    def parse_blocks(self, answer: str, chunk_data: dict[str, dict]) -> list[dict]:
        blocks: list[dict] = []
        cursor = 0
        for match in _IMG_MARKER.finditer(answer):
            text = answer[cursor:match.start()].strip()
            if text:
                blocks.append({"type": "markdown", "content": text})

            img_num = match.group(1)
            chunk_id = match.group(2)
            image_map = chunk_data.get(chunk_id, {}).get("image_map", {})
            img_url = image_map.get(img_num, "")
            if not img_url:
                logger.warning("ORCHESTRATOR AGENT => image marker [Img %s] for [chunk %s] has no URL", img_num, chunk_id)
            blocks.append({"type": "image", "content": img_url})
            cursor = match.end()

        tail = answer[cursor:].strip()
        if tail:
            blocks.append({"type": "markdown", "content": tail})
        return blocks

    def fetch_chunk_data(self, cited_chunks: list[dict]) -> tuple[list[str], dict[str, dict]]:
        source_urls: list[str] = []
        chunk_data: dict[str, dict] = {}
        seen_urls: set[str] = set()

        for chunk in cited_chunks:
            chunk_id = str(chunk["chunk_id"])
            data = Chunk.objects.get_source_url_and_image_map(chunk_id)

            url = data["source_url"]
            if url and url not in seen_urls:
                source_urls.append(url)
                seen_urls.add(url)

            chunk_data[chunk_id] = {"image_map": data["image_map"]}

        return source_urls, chunk_data
