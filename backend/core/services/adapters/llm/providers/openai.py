from langchain_openai import ChatOpenAI

from core.services.adapters.llm.base import BaseLLMProvider


class Provider(BaseLLMProvider):
    def build(self, model_id: str) -> ChatOpenAI:
        return ChatOpenAI(model=model_id)
