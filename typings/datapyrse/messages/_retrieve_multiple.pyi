from dataclasses import dataclass
from datapyrse._entity import Entity as Entity
from datapyrse._entity_collection import EntityCollection as EntityCollection
from datapyrse.messages._dataverse_request import DataverseRequest as DataverseRequest
from datapyrse.messages._methods import Method as Method
from datapyrse.query._query_expression import QueryExpression as QueryExpression
from logging import Logger
from requests import Request, Response as Response

def get_retrieve_multiple_request(dataverse_request: DataverseRequest, query: QueryExpression, logger: Logger = ...) -> Request: ...

@dataclass
class RetrieveMultipleResponse:
    response: Response
    entity_logical_name: str
    entities: EntityCollection = ...
    logger: Logger = ...
    def __post_init__(self) -> None: ...
    def __init__(self, response, entity_logical_name, logger=...) -> None: ...
