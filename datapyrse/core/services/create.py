import logging
import uuid
from typing import List
from datapyrse.core.services.service_client import ServiceClient
import requests
from datapyrse.core.models.entity import Entity
from datapyrse.core.utils.dataverse import (
    parse_entity_to_web_api_body,
)


class CreateRequest:
    def create(
        service_client: ServiceClient,
        entity: Entity,
        logger: logging.Logger = None,
    ) -> Entity:
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
        entity_plural_name = next(
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

        endpoint = f"api/data/v9.2/{entity_plural_name}"
        headers = {
            "Authorization": f"Bearer {service_client.get_access_token()}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Prefer": "odata.include-annotations=*",
        }

        response = requests.post(
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
        uri = response.headers["OData-EntityId"]
        logger.debug(f"Entity created {uri}")
        if not uri:
            logger.error("Entity URI not found in response")
            raise Exception("Entity URI not found in response")

        entity_id = uri.split("(")[1].split(")")[0]
        if not entity_id:
            logger.error(f"Entity ID not parsed from URI: {uri}")
            raise Exception("Entity ID not parsed from URI")
        logger.debug(f"Entity ID: {entity_id}")

        guid: uuid.UUID
        try:
            guid = uuid.UUID(entity_id)
        except ValueError:
            logger.error(f"Entity ID is not a valid GUID: {entity_id}")
            raise Exception("Entity ID is not a valid GUID")

        entity.entity_id = guid
        logger.debug("Entity created")
        return entity
