"""
A module for retrieving multiple entities from Dataverse
"""

from dataclasses import dataclass, field
from logging import Logger, getLogger

from requests import Request, Response

from datapyrse.models.entity import Entity
from datapyrse.models.entity_collection import EntityCollection
from datapyrse.models.methods import Method
from datapyrse.models.query_expression import QueryExpression
from datapyrse.services.dataverse_request import DataverseRequest


def get_retrieve_multiple_request(
    dataverse_request: DataverseRequest,
    query: QueryExpression,
    logger: Logger = getLogger(__name__),
) -> Request:
    """
    Prepare a retrieve multiple request for Dataverse

    Args:
        dataverse_request (DataverseRequest): DataverseRequest object
        query (QueryExpression): QueryExpression object
        logger (Logger): Logger object for logging

    Returns:
        Request: Request object for the retrieve multiple request

    Raises:
        ValueError: If DataverseRequest is not provided
    """
    if not dataverse_request:
        msg = "DataverseRequest required and must be an instance of datapyrse.DataverseRequest"
        logger.error(msg)
        raise ValueError(msg)
    if not query:
        msg = "QueryExpression required and must be an instance of datapyrse.QueryExpression"
        logger.error(msg)
        raise ValueError(msg)
    fetch_xml: str = query.fetch_xml
    if not fetch_xml:
        msg = "Failed to parse query expression"
        logger.error(msg)
        raise ValueError(msg)
    request: Request = Request(
        method=Method.GET.value,
        headers=dataverse_request.headers,
    )
    if "?" in dataverse_request.endpoint:
        dataverse_request.endpoint += f"&fetchXml={fetch_xml}"
    else:
        dataverse_request.endpoint += f"?fetchXml={fetch_xml}"

    request.url = dataverse_request.endpoint

    return request


@dataclass
class RetrieveMultipleResponse:
    """
    Parse the response from a retrieve multiple request to extract entities

    Args:
        response (Response): Response object from the retrieve multiple request
        entity_logical_name (str): Logical name of the entity
        logger (Logger): Logger object for logging

    Raises:
        ValueError: If Response or entity_logical_name is not provided
    """

    response: Response
    entity_logical_name: str
    logger: Logger = field(default_factory=lambda: getLogger(__name__))

    def __post_init__(self):
        if not self.response:
            msg = "Response required and must be an instance of requests.Response"
            self.logger.error(msg)
            raise ValueError(msg)
        if not self.entity_logical_name:
            msg = "entity_logical_name required and must be a string"
            self.logger.error(msg)
            raise ValueError(msg)
        self.entity_collection: EntityCollection = EntityCollection(
            entity_logical_name=self.entity_logical_name
        )
        self._parse_response()

    def _parse_response(self) -> None:
        self.response.raise_for_status()
        if not self.response.json().get("value") or not isinstance(
            self.response.json().get("value"), list
        ):
            return
        for entity_data in self.response.json().get("value"):
            entity: Entity = Entity(
                entity_logical_name=self.entity_logical_name,
                attributes=entity_data,
                logger=self.logger,
            )
            self.entity_collection.add_entity(entity)
