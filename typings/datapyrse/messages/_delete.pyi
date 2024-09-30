from dataclasses import dataclass
from datapyrse.messages._dataverse_request import DataverseRequest as DataverseRequest
from datapyrse.messages._methods import Method as Method
from logging import Logger
from requests import Request, Response as Response

def get_delete_request(dataverse_request: DataverseRequest, logger: Logger = ...) -> Request: ...

@dataclass
class DeleteResponse:
    response: Response
    logger: Logger = ...
    def __post_init__(self) -> None: ...
    def was_deleted(self) -> bool: ...
    def __init__(self, response, logger=...) -> None: ...
