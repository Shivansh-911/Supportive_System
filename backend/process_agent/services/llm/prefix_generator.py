from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

_SYSTEM = (
    "You are a document indexing assistant. "
    "Given a full document and a specific chunk, write 1-2 sentences that situate "
    "the chunk within the document. Be concise and factual. No preamble."
)


class PrefixGenerator:
    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm

    def generate(self, doc_title: str, doc_text: str, chunk_content: str) -> str:
        response = self._llm.invoke([
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=self._build_prompt(doc_title, doc_text, chunk_content)),
        ])
        return response.content.strip()

    async def agenerate(self, doc_title: str, doc_text: str, chunk_content: str) -> str:
        response = await self._llm.ainvoke([
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=self._build_prompt(doc_title, doc_text, chunk_content)),
        ])
        return response.content.strip()

    def _build_prompt(self, doc_title: str, doc_text: str, chunk_content: str) -> str:
        return (
            f"Document title: {doc_title}\n\n"
            f"Full document:\n{doc_text}\n\n"
            f"Chunk to contextualize:\n{chunk_content}"
        )
