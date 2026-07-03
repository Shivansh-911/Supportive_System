from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage


_SYSTEM = (
    "You are a Freshdesk help-doc indexing assistant. "
    "Given a full help article and a specific chunk from it, write 1-2 short sentences "
    "that situate the chunk within the article. Be concise and factual. No preamble. "
    "Note: in the chunk, every image URL has been replaced with a placeholder of the form "
    "[Img N] (e.g. [Img 1], [Img 2]). The same images appear inline in the full article as "
    "raw markdown image links — treat the placeholders and the raw image links as referring "
    "to the same images. Do not mention or describe these placeholders in your output."
)


class FreshdeskContextRetrieval:

    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm

    def retrieve(self, doc_title: str, doc_text: str, chunk: str) -> str:
        response = self._llm.invoke([
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=self._build_prompt(doc_title, doc_text, chunk)),
        ])
        return response.content.strip()

    def _build_prompt(self, doc_title: str, doc_text: str, chunk: str) -> str:
        return (
            f"Article title: {doc_title}\n\n"
            f"Full article:\n{doc_text}\n\n"
            f"Chunk to contextualize:\n{chunk}"
        )
