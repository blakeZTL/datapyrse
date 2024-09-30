from datapyrse._entity import Entity as Entity
from datapyrse._entity_metadata import EntityMetadata as EntityMetadata, OrgMetadata as OrgMetadata
from datapyrse._entity_reference import EntityReference as EntityReference
from datapyrse.query._column_set import ColumnSet as ColumnSet
from datapyrse.query._option_set import OptionSet as OptionSet
from logging import Logger
from typing import Any

DEFAULT_HEADERS: dict[str, str]

def get_entity_collection_name_by_logical_name(org_metadata: OrgMetadata, logical_name: str, logger: Logger = ...) -> str | None: ...
def transform_column_set(entity_metadata: EntityMetadata, column_set: ColumnSet) -> list[str]: ...
def get_entity_metadata(entity_logical_name: str, org_metadata: OrgMetadata, logger: Logger = ...) -> EntityMetadata: ...
def parse_entity_to_web_api_body(entity: Entity, org_metadata: OrgMetadata, logger: Logger = ...) -> dict[str, Any] | None: ...
