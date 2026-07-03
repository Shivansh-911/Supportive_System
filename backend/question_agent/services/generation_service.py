import re
import uuid

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from core.services.utils.logger import get_logger
from question_agent.services.prompts.system_prompt_answer_generation import SYSTEM
from question_agent.states.chunk_hit import ChunkHit

logger = get_logger(__name__)


_IMAGE_MARKER_PATTERN = re.compile(r"\[Img (\d+)(:[^\]]*)?\]")


class GenerationResult(BaseModel):
    answer: str = Field(
        description=(
            "Your answer to the user's question, formatted in Markdown. "
            "Preserve any [Img N:C] (or [Img N: alt text:C]) markers from the source "
            "chunks inline at the matching step in your answer, verbatim including the trailing :C suffix."
        )
    )
    cited_chunk_indices: list[int] = Field(
        default_factory=list,
        description=(
            "1-based indices of the chunks whose content was used to construct the answer. "
            "Only include chunks you genuinely drew from."
        ),
    )


class GenerationService:
    """Generates a grounded answer from retrieved chunks.

    Image markers from each chunk are tagged with the chunk's UUID before the
    LLM call so that per-document image indices stay unambiguous when chunks
    from multiple documents share the same number.
    """

    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm

    def generate(self, question: str, chunks: list[ChunkHit], last_qa_pair: dict | None = None) -> tuple[str, list[ChunkHit]]:

        structured_llm = self._llm.with_structured_output(GenerationResult)

        system_message = SystemMessage(content=SYSTEM)
        user_message = HumanMessage(content=self.build_user_prompt(question, chunks, last_qa_pair))

        result: GenerationResult = structured_llm.invoke([system_message, user_message])

        answer = result.answer.strip()
        cited_chunks = self.resolve_cited_chunks(result.cited_chunk_indices, chunks)
        return answer, cited_chunks



    def build_user_prompt(self, question: str, chunks: list[ChunkHit], last_qa_pair: dict | None = None) -> str:
        tagged_chunk_contents = self.tag_image_markers_with_chunk_ids(chunks)
        chunks_prompt_block = self.format_chunks_for_prompt(tagged_chunk_contents)
        if last_qa_pair:
            history_block = f"Previous Q&A:\nQ: {last_qa_pair['question']}\nA: {last_qa_pair['answer']}\n\n"
        else:
            history_block = ""
        return f"{history_block}Question:\n{question}\n\nChunks:\n{chunks_prompt_block}"

        

    def tag_image_markers_with_chunk_ids(self, chunks: list[ChunkHit]) -> list[str]:
        tagged_contents: list[str] = []
        for chunk_index, chunk in enumerate(chunks, start=1):
            tagged = self.embed_chunk_id_in_image_markers(chunk.content, chunk.chunk_id)
            tagged_contents.append(tagged)
        return tagged_contents

    def embed_chunk_id_in_image_markers(self, content: str, chunk_id: uuid) -> str:
        parts: list[str] = []
        cursor = 0
        for match in _IMAGE_MARKER_PATTERN.finditer(content):
            parts.append(content[cursor:match.start()])
            parts.append(self.build_tagged_marker(match, chunk_id))
            cursor = match.end()
        parts.append(content[cursor:])
        return "".join(parts)                                                                               # Join all formatted parts items into a single string 

    def build_tagged_marker(self, match: re.Match, chunk_id: uuid) -> str:
        image_number = match.group(1)
        alt_text_segment = match.group(2) or ""
        return f"[Img {image_number}{alt_text_segment}:{chunk_id}]"

    def format_chunks_for_prompt(self, contents: list[str]) -> str:
        blocks: list[str] = []
        for chunk_index, content in enumerate(contents, start=1):
            blocks.append(f"[chunk_{chunk_index}]\n{content}")
        return "\n\n".join(blocks)                                                                          # Join all formatted block items into a single string separated by blank lines

    def resolve_cited_chunks(self,cited_indices: list[int],chunks: list[ChunkHit]) -> list[ChunkHit]:
        resolved_chunks: list[ChunkHit] = []
        seen_chunks: set[int] = set()

        for index in cited_indices:
            if index in seen_chunks:
                continue
            if not 1 <= index <= len(chunks):                                                               # When the llm cites chunks then it uses 1 based numbering as told, then we have to check if it did not cite an index that is more than the total no of chunks 
                logger.warning("QUESTION AGENT => invalid citation index %d (total chunks=%d), skipping", index, len(chunks))
                continue
            seen_chunks.add(index)
            resolved_chunks.append(chunks[index - 1])                                                       # the llm cites 1 based indexes from the chunks list which is 0 based

        return resolved_chunks
