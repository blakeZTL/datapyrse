from dataclasses import dataclass
from datapyrse._entity import Entity as Entity
from datapyrse._entity_metadata import OrgMetadata as OrgMetadata
from datapyrse.utils._dataverse import DEFAULT_HEADERS as DEFAULT_HEADERS, get_entity_collection_name_by_logical_name as get_entity_collection_name_by_logical_name
from logging import Logger

@dataclass
class DataverseRequest:
    base_url: str
    org_metadata: OrgMetadata
    entity: Entity
    tag: str | None = ...
    suppress_duplicate_detection: bool = ...
    bypass_custom_plugin_execution: bool = ...
    suppress_callback_registration_expander_job: bool = ...
    logger: Logger = ...
    endpoint: str = ...
    headers: dict[str, str] = ...
    def __post_init__(self) -> None: ...
    def __init__(self, base_url, org_metadata, entity, tag=..., suppress_duplicate_detection=..., bypass_custom_plugin_execution=..., suppress_callback_registration_expander_job=..., logger=...) -> None: ...
