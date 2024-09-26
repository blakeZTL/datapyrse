import requests
from datapyrse.core.models.entity import Entity
from datapyrse.core.models.entity_reference import EntityReference
from uuid import UUID
from logging import Logger
from datapyrse.core.services.service_client import ServiceClient


def delete_entity(
    service_client: ServiceClient, logger: Logger = None, **kwargs
) -> bool:
    entity_id: str = None
    entity_name: str = None

    if not logger:
        import logging

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.WARN)
    if not service_client or not service_client.IsReady:
        logger.error("ServiceClient is not ready")
        raise ValueError("ServiceClient is not ready")
    if not kwargs:
        logger.error("At least one argument is required")
        raise ValueError("At least one argument is required")
    logger.debug(f"Deleting entity with args: {kwargs}")
    if "entity" in kwargs:
        entity = kwargs["entity"]
        if isinstance(entity, Entity):
            if entity.entity_id is None:
                logger.error("entity_id is required")
                raise ValueError("entity_id is required")
            if entity.entity_logical_name is None:
                logger.error("entity_name is required")
                raise ValueError("entity_name is required")
            entity_id = str(entity.entity_id)
            entity_name = entity.entity_logical_name
        else:
            logger.error("entity must be of type Entity")
            raise ValueError("entity must be of type Entity")
    if "entity_reference" in kwargs:
        entity_reference = kwargs["entity_reference"]
        if isinstance(entity_reference, EntityReference):
            entity_id = entity_reference.entity_id
            entity_name = entity_reference.entity_logical_name
        else:
            logger.error("entity_reference must be of type EntityReference")
            raise ValueError("entity_reference must be of type EntityReference")
    if "entity_name" in kwargs and "entity_id" in kwargs:
        entity_id = kwargs["entity_id"]
        entity_name = kwargs["entity_name"]
        if not isinstance(entity_id, UUID) and not isinstance(entity_id, str):
            logger.error("entity_id must be of type UUID or str")
            raise ValueError("entity_id must be of type UUID or str")
        else:
            entity_id = str(entity_id)
        if not isinstance(entity_name, str):
            logger.error("entity_name must be of type str")
            raise ValueError("entity_name must be of type str")
    if "entity_name" in kwargs and "entity_id" not in kwargs:
        logger.error("entity_id is required")
        raise ValueError("entity_id is required")
    if "entity_id" in kwargs and "entity_name" not in kwargs:
        logger.error("entity_name is required")
        raise ValueError("entity_name is required")

    # delete entity
    entity_metadata = next(
        (
            entity
            for entity in service_client.metadata.entities
            if entity.logical_name == entity_name
        ),
        None,
    )
    if not entity_metadata:
        logger.error(f"Entity {entity_name} not found in metadata")
        raise ValueError(f"Entity {entity_name} not found in metadata")
    entity_plural_name = entity_metadata.logical_collection_name
    if not entity_plural_name:
        logger.error(f"Entity {entity_name} does not have a plural name")
        raise ValueError(f"Entity {entity_name} does not have a plural name")

    url: str = (
        f"{service_client.resource_url}/api/data/v9.2/{entity_plural_name}({entity_id})"
    )
    headers = {
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Prefer": "return=representation;odata.metadata=none",
        "Authorization": f"Bearer {service_client.get_access_token()}",
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    if response.ok:
        logger.info(f"Entity {entity_name} with id {entity_id} deleted")
        return True
    logger.error(f"Failed to delete entity {entity_name} with id {entity_id}")
    return False
