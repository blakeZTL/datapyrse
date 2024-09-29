"""
A module for retrieving entities from Dataverse
"""

from dataclasses import dataclass, field
from logging import Logger, getLogger
from typing import List, Optional

from requests import Request, Response

from datapyrse.models.column_set import ColumnSet
from datapyrse.models.entity import Entity
from datapyrse.models.entity_metadata import EntityMetadata
from datapyrse.models.methods import Method
from datapyrse.services.dataverse_request import DataverseRequest
from datapyrse.utils.dataverse import (
    transform_column_set,
)


def get_retrieve_request(
    dataverse_request: DataverseRequest,
    column_set: ColumnSet,
    logger: Logger = getLogger(__name__),
) -> Request:
    """
    Prepare a retrieve request for Dataverse

    Args:
        dataverse_request (DataverseRequest): DataverseRequest object
        logger (Logger): Logger object for logging

    Returns:
        Request: Request object for the retrieve request

    Raises:
        ValueError: If DataverseRequest is not provided
    """
    logger.debug(__name__)
    if not dataverse_request:
        msg = "DataverseRequest required and must be an instance of datapyrse.DataverseRequest"
        logger.error(msg)
        raise ValueError(msg)
    if not column_set:
        msg = "ColumnSet required and must be an instance of datapyrse.ColumnSet"
        logger.error(msg)
        raise ValueError(msg)
    entity: Entity = dataverse_request.entity
    if not dataverse_request.org_metadata.entities:
        msg = "Entities not found on OrgMetadata"
        logger.error(msg)
        raise ValueError(msg)
    entity_metadata: Optional[EntityMetadata] = next(
        (
            metadata
            for metadata in dataverse_request.org_metadata.entities
            if metadata.logical_name == entity.entity_logical_name
        ),
        None,
    )
    if not entity_metadata:
        msg = f"No matching metadata found for {entity.entity_logical_name}"
        logger.error(msg)
        raise ValueError(msg)
    select: Optional[str] = None
    if isinstance(column_set, list):
        parsed_column_set: List[str] = transform_column_set(
            entity_metadata=entity_metadata,
            column_set=column_set,
        )
        select = ",".join(parsed_column_set)

    request: Request = Request(
        method=Method.GET.value,
        url=dataverse_request.endpoint,
        headers=dataverse_request.headers,
    )
    if select:
        if "?" in request.url:
            request.url = f"{request.url}&$select={select}"
        else:
            request.url = f"{request.url}?$select={select}"
    return request


@dataclass
class RetrieveResponse:
    """
    Parse the response from a retrieve request to extract the entity

    Args:
        response (Response): Response object from the retrieve request
        entity (Entity): Entity object retrieved
        logger (Logger): Logger object for logging

    Raises:
        ValueError: If response or entity is not provided
        ValueError: If entity is not parsed from response
    """

    response: Response
    entity: Entity
    logger: Logger = field(default_factory=lambda: getLogger(__name__))

    def __post_init__(
        self,
    ):
        self.logger.debug(__name__)
        if not self.response:
            msg = "Response required and must be an instance of requests.Response"
            self.logger.error(msg)
            raise ValueError(msg)
        if not self.entity:
            msg = "Entity required and must be an instance of datapyrse.Entity"
            self.logger.error(msg)
            raise ValueError(msg)
        if not self.response.json():
            msg = "Entity not found in response"
            self.logger.error(msg)
            raise ValueError(msg)
        self.logger.debug("Response json %s", self.response.json())
        parsed_entity: Entity = Entity(
            entity_id=self.entity.entity_id,
            entity_logical_name=self.entity.entity_logical_name,
            attributes=self.response.json(),
            logger=self.logger,
        )
        self.logger.debug(parsed_entity)
        self.entity = parsed_entity
