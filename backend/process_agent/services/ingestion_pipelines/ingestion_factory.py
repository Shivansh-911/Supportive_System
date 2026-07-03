from core.models.constants.source_type import SourceType
from process_agent.services.ingestion_pipelines.base_ingestion import BaseIngestion
from process_agent.services.ingestion_pipelines.freshdesk_helpdocs_ingestion import FreshdeskHelpdocsIngestion

_REGISTRY: dict[str, type[BaseIngestion]] = {
    SourceType.FRESHDESK_ARTICLE: FreshdeskHelpdocsIngestion,
}
# Right now no chaching is happening, in production there will be caching so that we dont have to create the factories everytime it is called 
# _INSTANCES: dict[str, BaseIngestion] = {}

def build_ingestion(source_type: str) -> BaseIngestion:

    # if source_type in _INSTANCES:
    #   return _INSTANCES[source_type]

    cls = _REGISTRY.get(source_type)
    if cls is None:
        raise ValueError(f"No ingestion pipeline registered for source_type={source_type!r}")
    
    # _INSTANCES[source_type] = cls.create()
    #   return _INSTANCES[source_type]
   
    return cls.create()
