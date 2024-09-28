import logging
from logging import Logger
import uuid
from typing import List

import requests
from requests import Response

from datapyrse.core.models.column_set import ColumnSet
from datapyrse.core.models.entity import Entity
from datapyrse.core.utils.dataverse import (
    transform_column_set,
)


def retrieve(
    service_client,
    entity_logical_name: str,
    entity_id: uuid.UUID,
    column_set: ColumnSet,
    logger: Logger = logging.getLogger(__name__),
) -> Entity:
    """
    Retrieves an entity from Dataverse by its logical name and ID.

    This function sends a GET request to the Dataverse Web API to fetch an entity
    based on its logical name and unique identifier (entity_id). It allows selecting
    specific columns (fields) to be retrieved via the column_set parameter.

    Args:
        service_client (ServiceClient): The service client used to authenticate
            and send the request.
        entity_logical_name (str): The logical name of the entity in Dataverse.
        entity_id (uuid.UUID): The unique identifier of the entity to retrieve.
        column_set (ColumnSet): A list of attribute names (columns) to be retrieved
            from the entity.
        logger (logging.Logger, optional): A logger instance for logging debug
            and error messages. Defaults to None.

    Returns:
        Entity: The retrieved entity with its attributes populated.

    Raises:
        Exception: Raised if the service client is not ready, if the entity logical
            name or ID is missing, if the column set transformation fails, or if
            the entity cannot be found.
    """

    from datapyrse.core.services.service_client import ServiceClient

    if not service_client or not isinstance(service_client, ServiceClient):
        raise Exception("Service client is required and must be of type ServiceClient")

    logger = service_client._prepare_request(logger)

    if not entity_logical_name:
        raise Exception("Entity plural name is required")

    if not entity_id:
        raise Exception("Entity ID is required")

    if not column_set:
        raise Exception("Column set is required")

    if not service_client.metadata.entities:
        raise Exception("Metadata entities not found")
    entity_plural_name: str | None = next(
        (
            data.logical_collection_name
            for data in service_client.metadata.entities
            if data.logical_name == entity_logical_name
        ),
        None,
    )
    if not entity_plural_name:
        raise Exception("Entity collection name not found")

    select: str | None = None
    if isinstance(column_set, list):
        parsed_column_set: List[str] = transform_column_set(
            service_client, entity_logical_name, column_set
        )
        if not parsed_column_set:
            raise Exception("Failed to transform column set")
        select = ",".join(parsed_column_set)

    logger.debug("Retrieving entity")
    endpoint: str = f"api/data/v9.2/{entity_plural_name}({str(entity_id)})"
    headers: dict = service_client._get_request_headers()
    url: str = f"{service_client.resource_url}/{endpoint}"
    if select:
        url = f"{url}?$select={select}"

    response: Response = requests.get(
        url,
        headers=headers,
    )
    response.raise_for_status()
    entity: Entity = Entity(
        entity_id=entity_id,
        entity_logical_name=entity_logical_name,
        attributes=response.json(),
        logger=logger,
    )
    return entity
