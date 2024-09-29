"""
A module for creating entities in Dataverse
"""

from dataclasses import dataclass, field
from logging import Logger, getLogger
from uuid import UUID


from requests import Response, Request


from datapyrse.utils.dataverse import (
    parse_entity_to_web_api_body,
)
from datapyrse.models.entity import Entity
from datapyrse.models.methods import Method
from datapyrse.services.dataverse_request import DataverseRequest


def get_create_request(
    dataverse_request: DataverseRequest,
    logger: Logger = getLogger(__name__),
) -> Request:
    """
    Prepare a create request for Dataverse

    Args:
        dataverse_request (DataverseRequest): DataverseRequest object
        logger (Logger): Logger object for logging

    Returns:
        Request: Request object for the create request

    Raises:
        ValueError: If DataverseRequest is not provided
    """
    logger.debug(__name__)
    if not dataverse_request:
        msg = "DataverseRequest required and must be an instance of datapyrse.DataverseRequest"
        logger.error(msg)
        raise ValueError(msg)
    request: Request = Request(
        method=Method.POST.value,
        url=dataverse_request.endpoint,
        headers=dataverse_request.headers,
        json=parse_entity_to_web_api_body(
            entity=dataverse_request.entity,
            org_metadata=dataverse_request.org_metadata,
            logger=logger,
        ),
    )
    logger.debug(request)
    return request


@dataclass
class CreateResponse:
    """
    Parse the response from a create request to extract the entity ID

    Args:
        response (Response): Response object from the create request
        entity (Entity): Entity object created
        logger (Logger): Logger object for logging

    Raises:
        ValueError: If response or entity is not provided
        ValueError: If entity ID is not found in response
        ValueError: If entity ID is not parsed from response
        ValueError: If entity ID is not a valid GUID
    """

    response: Response
    entity: Entity
    logger: Logger = field(default_factory=lambda: getLogger(__name__))

    def __post_init__(self):
        self.logger.debug(__name__)
        if not self.response:
            msg = "Response required and must be an instance of requests.Response"
            self.logger.error(msg)
            raise ValueError(msg)
        if not self.entity:
            msg = "entity required and must be an instance of datapyrse.Entity"
            self.logger.error(msg)
            raise ValueError(msg)
        self._get_entity_id_from_response()

    def _get_entity_id_from_response(self) -> None:
        self.logger.debug(__name__)
        self.response.raise_for_status()
        if "OData-EntityId" not in self.response.headers:
            msg = "Entity ID not found in response"
            self.logger.error(msg)
            raise ValueError(msg)
        uri: str = self.response.headers["OData-EntityId"]
        self.logger.debug(f"Entity created {uri}")
        if not uri:
            msg = "Entity URI not found in response"
            self.logger.error(msg)
            raise ValueError(msg)
        entity_id: str = uri.split("(")[1].split(")")[0]
        if not entity_id:
            msg = f"Entity ID not parsed from URI: {uri}"
            self.logger.error(msg)
            raise ValueError(msg)
        self.logger.debug(f"Entity ID: {entity_id}")
        try:
            self.entity.entity_id = UUID(entity_id)
        except ValueError as exc:
            msg = f"Entity ID is not a valid GUID: {entity_id}"
            self.logger.error(msg)
            raise ValueError(msg) from exc
