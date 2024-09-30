"""
A module for retrieving multiple entities from Dataverse
"""

from dataclasses import dataclass, field
from logging import Logger, getLogger

from requests import Request, Response

from datapyrse._entity import Entity
from datapyrse._entity_collection import EntityCollection
from datapyrse.messages._methods import Method
from datapyrse.query._query_expression import QueryExpression
from datapyrse.messages._dataverse_request import DataverseRequest


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
        entities (EntityCollection): EntityCollection object to populate with entities
            - Populated with an empty list of entities by default
            - Entities are added to the collection during parsing
        logger (Logger): Logger object for logging

    Raises:
        ValueError: If Response or entity_logical_name is not provided
    """

    response: Response
    entity_logical_name: str
    entities: EntityCollection = field(default_factory=EntityCollection, init=False)
    logger: Logger = field(default_factory=lambda: getLogger(__name__))

    def __post_init__(self):
        self.logger.debug(
            f"Initializing RetrieveMultipleResponse for {self.entity_logical_name}"
        )
        if not self.response:
            msg = "Response required and must be an instance of requests.Response"
            self.logger.error(msg)
            raise ValueError(msg)
        if not self.entity_logical_name:
            msg = "entity_logical_name required and must be a string"
            self.logger.error(msg)
            raise ValueError(msg)
        self.entities.entity_logical_name = self.entity_logical_name
        self.logger.debug("EntityCollection initialized")
        self._parse_response()

    def _parse_response(self) -> None:
        self.logger.debug("Parsing response")
        self.response.raise_for_status()
        response_json = self.response.json()
        if not response_json.get("value") or not isinstance(
            response_json.get("value"), list
        ):
            self.logger.debug("No entities found in response")
            return
        for entity_data in response_json.get("value"):
            self.logger.debug(f"Parsing entity data: {entity_data}")
            entity: Entity = Entity(
                entity_logical_name=self.entity_logical_name,
                attributes=entity_data,
                logger=self.logger,
            )
            self.entities.add_entity(entity)
        self.logger.debug(
            "Entity collection (%s) parsed successfully",
            len(self.entities.entities or []),
        )
