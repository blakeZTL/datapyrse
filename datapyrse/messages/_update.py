from dataclasses import dataclass
from logging import Logger, getLogger

from requests import Request, Response

from datapyrse._entity import Entity
from datapyrse.messages._methods import Method
from datapyrse.messages._dataverse_request import DataverseRequest
from datapyrse.utils._dataverse import parse_entity_to_web_api_body


def get_update_request(
    dataverse_request: DataverseRequest, logger: Logger = getLogger(__name__)
) -> Request:
    """
    Prepare an update request for Dataverse

    Args:
        dataverse_request (DataverseRequest): DataverseRequest object
        logger (Logger): Logger object for logging

    Returns:
        Request: Request object for the update request

    Raises:
        ValueError: If DataverseRequest is not provided
    """
    if not dataverse_request:
        msg = "No dataverse request provided"
        logger.error(msg)
        raise ValueError(msg)

    return Request(
        method=Method.PATCH.value,
        url=dataverse_request.endpoint,
        headers=dataverse_request.headers,
        json=parse_entity_to_web_api_body(
            entity=dataverse_request.entity,
            org_metadata=dataverse_request.org_metadata,
            logger=logger,
        ),
    )


@dataclass
class UpdateResponse:
    """
    Parse the response from an update request to extract the entity ID

    Args:
        response (Response): Response object from the update request
        entity (Entity): Entity object updated
        logger (Logger): Logger object for logging

    Raises:
        ValueError: If response is not provided
    """

    response: Response
    entity: Entity
    logger: Logger = getLogger(__name__)

    def __post_init__(self):
        if not self.response:
            msg = "No response provided"
            self.logger.error(msg)
            raise ValueError(msg)
