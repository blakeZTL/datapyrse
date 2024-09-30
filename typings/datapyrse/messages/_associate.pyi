from dataclasses import dataclass
from datapyrse._entity_metadata import EntityMetadata as EntityMetadata, ManyToManyRelationshipMetadata as ManyToManyRelationshipMetadata, ManyToOneRelationshipMetadata as ManyToOneRelationshipMetadata, OneToManyRelationshipMetadata as OneToManyRelationshipMetadata, OrgMetadata as OrgMetadata
from datapyrse._entity_reference import EntityReference as EntityReference
from datapyrse.messages._dataverse_request import DataverseRequest as DataverseRequest
from datapyrse.messages._methods import Method as Method
from datapyrse.utils._dataverse import get_entity_collection_name_by_logical_name as get_entity_collection_name_by_logical_name
from logging import Logger
from requests import Request

def get_associate_request(dataverse_request: DataverseRequest, associate_request: AssociateRequest, logger: Logger = ...) -> Request: ...

@dataclass
class AssociateRequest:
    primary_record: EntityReference
    related_records: list[EntityReference]
    org_metadata: OrgMetadata
    relationship_name: str | None = ...
    def __post_init__(self) -> None: ...
    def __init__(self, primary_record, related_records, org_metadata, relationship_name=...) -> None: ...
