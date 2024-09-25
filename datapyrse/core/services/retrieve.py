import logging
import uuid
from typing import List
from datapyrse.core.services.service_client import ServiceClient
import requests
from datapyrse.core.models.entity import Entity
from datapyrse.core.utils.dataverse import (
    transform_column_set,
)


def retrieve(
    service_client: ServiceClient,
    entity_logical_name: str,
    entity_id: uuid.UUID,
    column_set: List[str],
    logger: logging.Logger = None,
) -> Entity:
    if not service_client.IsReady:
        raise Exception("Service client is not ready")

    if not entity_logical_name:
        raise Exception("Entity plural name is required")

    if not entity_id:
        raise Exception("Entity ID is required")

    if not column_set:
        raise Exception("Column set is required")

    if not logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.WARNING)

    entity_plural_name = next(
        (
            data.logical_collection_name
            for data in service_client.metadata.entities
            if data.logical_name == entity_logical_name
        ),
        None,
    )
    if not entity_plural_name:
        raise Exception("Entity collection name not found")

    select: str = None
    if isinstance(column_set, list):
        parsed_column_set: List[str] = transform_column_set(
            service_client, entity_logical_name, column_set
        )
        if not parsed_column_set:
            raise Exception("Failed to transform column set")
        select = ",".join(parsed_column_set)

    logger.debug("Retrieving entity")
    endpoint = f"api/data/v9.2/{entity_plural_name}({str(entity_id)})"
    headers = {
        "Authorization": f"Bearer {service_client.get_access_token()}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Prefer": "odata.include-annotations=*",
    }
    url: str = f"{service_client.resource_url}/{endpoint}"
    if select:
        url = f"{url}?$select={select}"

    response = requests.get(
        url,
        headers=headers,
    )
    response.raise_for_status()
    entity = Entity(
        entity_id=entity_id,
        entity_logical_name=entity_logical_name,
        attributes=response.json(),
        logger=logger,
    )
    return entity
