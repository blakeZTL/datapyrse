import logging
from typing import List
from core import ServiceClient
import requests

from utils.dataverse import get_entity_collection_name_by_logical_name


def retrieve(
    service_client: ServiceClient,
    entity_name: str,
    entity_id: str,
    column_set: List[str],
) -> dict:
    if not service_client.IsReady:
        raise Exception("Service client is not ready")

    if not entity_name:
        raise Exception("Entity plural name is required")

    if not entity_id:
        raise Exception("Entity ID is required")

    if not column_set:
        raise Exception("Column set is required")

    entity_plural_name = get_entity_collection_name_by_logical_name(
        service_client, entity_name
    )
    if not entity_plural_name:
        raise Exception("Entity collection name not found")

    logging.debug("Retrieving entity")
    endpoint = f"api/data/v9.2/{entity_plural_name}({entity_id})"
    headers = {
        "Authorization": f"Bearer {service_client.get_access_token()}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }
    select = ",".join(column_set)
    response = requests.get(
        f"{service_client.resource_url}/{endpoint}?$select={select}",
        headers=headers,
    )
    response.raise_for_status()
    return response.json()


def retrieve_multiple(
    service_client: ServiceClient,
    entity_plural_name: str,
    column_set: List[str],
) -> dict:
    if not service_client.IsReady:
        raise Exception("Service client is not ready")

    if not entity_plural_name:
        raise Exception("Entity plural name is required")

    if not column_set:
        raise Exception("Column set is required")

    logging.debug("Retrieving entities")
    endpoint = f"api/data/v9.2/{entity_plural_name}"
    headers = {
        "Authorization": f"Bearer {service_client.get_access_token()}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }
    select = ",".join(column_set)
    response = requests.get(
        f"{service_client.resource_url}/{endpoint}?$select={select}",
        headers=headers,
    )
    response.raise_for_status()
    return response.json()
