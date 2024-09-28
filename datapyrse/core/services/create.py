import logging
from logging import Logger
from uuid import UUID
import requests
from requests import Response
from datapyrse.core.models.entity import Entity
from datapyrse.core.utils.dataverse import (
    parse_entity_to_web_api_body,
)


def create(
    service_client,
    entity: Entity,
    logger: Logger = logging.getLogger(__name__),
    **kwargs,
) -> Entity:
    """
    Creates an entity in Dataverse.

    This method constructs and sends a POST request to the Dataverse Web API to
    create the provided entity. It retrieves metadata about the entity, prepares
    the request body, and handles the response, extracting the created entity's ID.

    Args:
        service_client (ServiceClient): The service client used to authenticate
            and send the request.
        entity (Entity): The entity to be created in Dataverse.
        logger (Logger, optional): A logger instance for logging debug and
            error messages. Defaults to None.
        **kwargs: Optional parameters for the request, such as:
            - SuppressDuplicateDetection (bool): Expect error if duplicate record found.
            - BypassCustomPluginExecution (bool): Bypass plug-in logic if caller has prvBypassCustomPlugins privilege.
            - tag (string): Add a shared variable to the plugin execution context.
            - SuppressCallbackRegistrationExpanderJob (bool): Surpress the triggering of a Power Automate.

    Returns:
        Entity: The entity instance with its `entity_id` populated upon successful creation.

    Raises:
        Exception: Raised if the service client is not ready, if the entity is
            invalid or lacks a logical name, or if the API request fails for any reason.
    """
    from datapyrse.core.services.service_client import ServiceClient

    if not service_client or not isinstance(service_client, ServiceClient):
        logger.error("Service client is required and must be of type ServiceClient")
        raise Exception("Service client is required and must be of type ServiceClient")

    logger = service_client._prepare_request(logger, entity)

    logger.debug("Creating entity")
    if not service_client.metadata.entities:
        logger.error("Metadata entities not found")
        raise Exception("Metadata entities not found")

    entity_plural_name: str | None = next(
        (
            data.logical_collection_name
            for data in service_client.metadata.entities
            if data.logical_name == entity.entity_logical_name
        ),
        None,
    )
    if not entity_plural_name:
        logger.error("Entity collection name not found")
        logger.error(f"Entity logical name: {entity.entity_logical_name}")
        logger.error(f"Entities: {service_client.metadata.entities}")
        raise Exception("Entity collection name not found")
    logger.debug(f"Entity plural name: {entity_plural_name}")

    parsed_entity_data: dict = parse_entity_to_web_api_body(
        entity,
        service_client,
        logger,
        entity_logical_collection_name=entity_plural_name,
    )

    endpoint: str = f"api/data/v9.2/{entity_plural_name}"

    headers: dict = service_client._get_request_headers(**kwargs)

    if kwargs and kwargs.get("tag") is not None:
        tag: str = str(kwargs["tag"])
        endpoint += f"?tag={tag}"

    response: Response = requests.post(
        f"{service_client.resource_url}/{endpoint}",
        headers=headers,
        json=parsed_entity_data,
    )

    if not response.ok:
        logger.error(f"Failed to create entity: {response.text}")
        raise Exception(f"Failed to create entity: {response.text}")
    if "OData-EntityId" not in response.headers:
        logger.error("Entity ID not found in response")
        raise Exception("Entity ID not found in response")
    uri: str = response.headers["OData-EntityId"]
    logger.debug(f"Entity created {uri}")
    if not uri:
        logger.error("Entity URI not found in response")
        raise Exception("Entity URI not found in response")

    entity_id: str = uri.split("(")[1].split(")")[0]
    if not entity_id:
        logger.error(f"Entity ID not parsed from URI: {uri}")
        raise Exception("Entity ID not parsed from URI")
    logger.debug(f"Entity ID: {entity_id}")

    guid: UUID
    try:
        guid = UUID(entity_id)
    except ValueError:
        logger.error(f"Entity ID is not a valid GUID: {entity_id}")
        raise Exception("Entity ID is not a valid GUID")

    entity.entity_id = guid
    logger.debug("Entity created")
    return entity
