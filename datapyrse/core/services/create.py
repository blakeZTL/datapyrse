import logging
from logging import Logger
from uuid import UUID

import requests
from requests import Response

from datapyrse.core.models.entity import Entity
from datapyrse.core.services.service_client import ServiceClient
from datapyrse.core.utils.dataverse import (
    parse_entity_to_web_api_body,
)


class CreateRequest:
    """
    Handles the creation of an entity in Dataverse via the Web API.

    This class provides a static method to create an entity by sending a POST request
    to the Dataverse Web API endpoint. The request is made through an authenticated
    ServiceClient instance.
    """

    @staticmethod
    def create(
        service_client: ServiceClient,
        entity: Entity,
        logger: Logger = logging.getLogger(__name__),
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
            logger (logging.Logger, optional): A logger instance for logging debug and
                error messages. Defaults to None.

        Returns:
            Entity: The entity instance with its `entity_id` populated upon successful creation.

        Raises:
            Exception: Raised if the service client is not ready, if the entity is
                invalid or lacks a logical name, or if the API request fails for any reason.
        """
        if not logger:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.WARNING)

        if not service_client.IsReady:
            logger.error("Service client is not ready")
            raise Exception("Service client is not ready")

        if not entity:
            logger.error("Entity is required")
            raise Exception("Entity is required")
        if not isinstance(entity, Entity):
            logger.error("Entity is not of type Entity")
            raise Exception("Entity is not of type Entity")
        if not entity.entity_logical_name:
            logger.error("Entity logical name is required")
            raise Exception("Entity logical name is required")

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
        headers: dict = {
            "Authorization": f"Bearer {service_client.get_access_token()}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Prefer": "odata.include-annotations=*",
        }

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
