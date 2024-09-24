import logging
from typing import List
import requests
from datapyrse.core.services.service_client import ServiceClient
from datapyrse.core.models.entity import Entity
from datapyrse.core.models.entity_collection import EntityCollection
from datapyrse.core.models.query_expression import QueryExpression
from datapyrse.core.utils.dataverse import (
    get_entity_collection_name_by_logical_name,
)


def retrieve_multiple(
    service_client: ServiceClient,
    query: QueryExpression,
    logger: logging.Logger = None,
):
    if not service_client.IsReady:
        raise Exception("Service client is not ready")

    if not query:
        raise Exception("Query is required")
    else:
        if not isinstance(query, QueryExpression):
            raise Exception("Query must be a QueryExpression")

    if not logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.WARNING)

    entity_logical_name = query.entity_name
    entity_plural_name = get_entity_collection_name_by_logical_name(
        service_client, entity_logical_name
    )
    if not entity_plural_name:
        raise Exception("Entity collection name not found")

    logger.debug("Retrieving entities")
    endpoint = f"api/data/v9.2/{entity_plural_name}"
    headers = {
        "Authorization": f"Bearer {service_client.get_access_token()}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Prefer": "odata.include-annotations=*",
    }

    fetch_xml = query.to_fetchxml()
    if fetch_xml:
        endpoint += f"?fetchXml={fetch_xml}"
    else:
        raise Exception("Failed to parse query expression")

    url = f"{service_client.resource_url}/{endpoint}"

    response: requests.Response
    try:
        response = requests.get(
            url,
            headers=headers,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(fetch_xml)
        logger.error(f"Failed to retrieve entities: {e}")
        raise Exception("Failed to retrieve entities")
    if not response.json().get("value"):
        return EntityCollection(entity_logical_name=entity_logical_name, entities=[])

    entities = EntityCollection(entity_logical_name=entity_logical_name)
    logger.debug(f"Entity logical name: {entity_logical_name}")
    logger.debug(f"Retrieved {len(response.json().get('value'))} entities")
    logger.debug(f"Entities: {response.json().get('value')}")
    for entity_data in response.json().get("value"):
        entity = Entity(
            entity_logical_name=entity_logical_name,
            attributes=entity_data,
            logger=logger,
        )
        entities.add_entity(entity)

    return entities
