import logging

import requests

from datapyrse.core.models.entity import Entity
from datapyrse.core.models.entity_collection import EntityCollection
from datapyrse.core.models.query_expression import QueryExpression
from datapyrse.core.services.service_client import ServiceClient


def retrieve_multiple(
        service_client: ServiceClient,
        query: QueryExpression,
        logger: logging.Logger = None,
):
    """
    Retrieves multiple entities from Dataverse using a query expression.

    This function sends a GET request to the Dataverse Web API to retrieve multiple
    entities that match the given query expression. It uses the FetchXML generated
    from the query to perform the retrieval.

    Args:
        service_client (ServiceClient): The service client used to authenticate
            and send the request.
        query (QueryExpression): The query expression that defines the filtering
            and selection of entities to retrieve.
        logger (logging.Logger, optional): A logger instance for logging debug
            and error messages. Defaults to None.

    Returns:
        EntityCollection: A collection of entities matching the query.

    Raises:
        Exception: Raised if the service client is not ready, the query is invalid,
            or the API request fails.
    """
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

    entity_logical_name: str = query.entity_name
    if not entity_logical_name:
        raise ValueError("Entity logical name not found in query")

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

    logger.debug("Retrieving entities")
    endpoint: str = f"api/data/v9.2/{entity_plural_name}"
    headers: dict = {
        "Authorization": f"Bearer {service_client.get_access_token()}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Prefer": "odata.include-annotations=*",
    }

    fetch_xml: str = query.to_fetchxml()
    if fetch_xml:
        endpoint += f"?fetchXml={fetch_xml}"
    else:
        raise Exception("Failed to parse query expression")

    url: str = f"{service_client.resource_url}/{endpoint}"

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

    entities: EntityCollection = EntityCollection(entity_logical_name=entity_logical_name)
    logger.debug(f"Entity logical name: {entity_logical_name}")
    logger.debug(f"Retrieved {len(response.json().get('value'))} entities")
    logger.debug(f"Entities: {response.json().get('value')}")
    for entity_data in response.json().get("value"):
        entity: Entity = Entity(
            entity_logical_name=entity_logical_name,
            attributes=entity_data,
            logger=logger,
        )
        entities.add_entity(entity)

    return entities
