from langchain_anthropic import ChatAnthropic

from core.services.adapters.llm.base import BaseLLMProvider


class Provider(BaseLLMProvider):
    def build(self, model_id: str) -> ChatAnthropic:
        return ChatAnthropic(model=model_id)
