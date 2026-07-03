from abc import ABC, abstractmethod

from process_agent.models.sync_event import SyncEvent


class BaseIngestion(ABC):
    @abstractmethod
    def ingest(self, event: SyncEvent) -> None: ...
