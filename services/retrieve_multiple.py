import logging
from typing import List
import requests
from core import ServiceClient
from models.entity import Entity
from models.entity_collection import EntityCollection
from utils.dataverse import (
    get_entity_collection_name_by_logical_name,
    transform_column_set,
)


def retrieve_multiple(
    service_client: ServiceClient,
    entity_logical_name: str,
    column_set: List[str],
) -> EntityCollection:
    if not service_client.IsReady:
        raise Exception("Service client is not ready")

    if not entity_logical_name:
        raise Exception("Entity logical name is required")

    if not column_set:
        raise Exception("Column set is required")

    entity_plural_name = get_entity_collection_name_by_logical_name(
        service_client, entity_logical_name
    )
    if not entity_plural_name:
        raise Exception("Entity collection name not found")

    select: List[str] = []
    try:
        select = transform_column_set(service_client, entity_logical_name, column_set)
    except Exception as e:
        logging.error(f"Failed to transform column set: {e}")
        raise Exception("Failed to transform column set")

    logging.debug("Retrieving entities")
    endpoint = f"api/data/v9.2/{entity_plural_name}"
    headers = {
        "Authorization": f"Bearer {service_client.get_access_token()}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }

    url = f"{service_client.resource_url}/{endpoint}"

    if select:
        url += f"?$select={','.join(select)}"

    response = requests.get(
        url,
        headers=headers,
    )
    response.raise_for_status()
    if not response.json().get("value"):
        return EntityCollection(entity_logical_name=entity_logical_name, entities=[])

    entities = EntityCollection(entity_logical_name=entity_logical_name)

    for entity_data in response.json().get("value"):
        entity = Entity(
            entity_logical_name=entity_logical_name,
            attributes=entity_data,
        )
        entities.add_entity(entity)

    return entities
