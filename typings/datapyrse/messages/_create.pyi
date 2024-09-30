from dataclasses import dataclass
from datapyrse._entity import Entity as Entity
from datapyrse.messages._dataverse_request import DataverseRequest as DataverseRequest
from datapyrse.messages._methods import Method as Method
from datapyrse.utils._dataverse import parse_entity_to_web_api_body as parse_entity_to_web_api_body
from logging import Logger
from requests import Request, Response as Response

def get_create_request(dataverse_request: DataverseRequest, logger: Logger = ...) -> Request: ...

@dataclass
class CreateResponse:
    response: Response
    entity: Entity
    logger: Logger = ...
    def __post_init__(self) -> None: ...
    def __init__(self, response, entity, logger=...) -> None: ...
