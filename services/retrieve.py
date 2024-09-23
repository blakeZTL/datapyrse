import logging
import uuid
from typing import List
from core import ServiceClient
import requests
from models.entity import Entity
from utils.dataverse import (
    get_entity_collection_name_by_logical_name,
    transform_column_set,
)


def retrieve(
    service_client: ServiceClient,
    entity_logical_name: str,
    entity_id: uuid.UUID,
    column_set: List[str],
) -> Entity:
    if not service_client.IsReady:
        raise Exception("Service client is not ready")

    if not entity_logical_name:
        raise Exception("Entity plural name is required")

    if not entity_id:
        raise Exception("Entity ID is required")

    if not column_set:
        raise Exception("Column set is required")

    entity_plural_name = get_entity_collection_name_by_logical_name(
        service_client, entity_logical_name
    )
    if not entity_plural_name:
        raise Exception("Entity collection name not found")

    parsed_column_set = transform_column_set(
        service_client, entity_logical_name, column_set
    )
    if not parsed_column_set:
        raise Exception("Failed to transform column set")

    select = ",".join(parsed_column_set)

    logging.debug("Retrieving entity")
    endpoint = f"api/data/v9.2/{entity_plural_name}({str(entity_id)})"
    headers = {
        "Authorization": f"Bearer {service_client.get_access_token()}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Prefer": "odata.include-annotations=*",
    }
    response = requests.get(
        f"{service_client.resource_url}/{endpoint}?$select={select}",
        headers=headers,
    )
    response.raise_for_status()
    entity = Entity(
        entity_id=entity_id,
        entity_logical_name=entity_logical_name,
        attributes=response.json(),
    )
    return entity
