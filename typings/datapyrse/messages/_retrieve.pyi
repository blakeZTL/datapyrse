from dataclasses import dataclass
from datapyrse._entity import Entity as Entity
from datapyrse._entity_metadata import EntityMetadata as EntityMetadata
from datapyrse.messages._dataverse_request import DataverseRequest as DataverseRequest
from datapyrse.messages._methods import Method as Method
from datapyrse.query._column_set import ColumnSet as ColumnSet
from datapyrse.utils._dataverse import transform_column_set as transform_column_set
from logging import Logger
from requests import Request, Response as Response

def get_retrieve_request(dataverse_request: DataverseRequest, column_set: ColumnSet, logger: Logger = ...) -> Request: ...

@dataclass
class RetrieveResponse:
    response: Response
    entity: Entity
    logger: Logger = ...
    def __post_init__(self) -> None: ...
    def __init__(self, response, entity, logger=...) -> None: ...
