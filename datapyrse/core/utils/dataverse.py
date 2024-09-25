import logging
from typing import List
from datapyrse.core.models.entity import Entity
from datapyrse.core.models.entity_metadata import EntityMetadata, EntityMetadataResponse
from datapyrse.core.models.entity_reference import EntityReference
from datapyrse.core.models.option_set import OptionSet
from datapyrse.core.services.service_client import ServiceClient
import requests


def get_entity_collection_name_by_logical_name(
    service_client: ServiceClient, logical_name: str
) -> str | None:
    if not service_client.IsReady:
        raise Exception("Service client is not ready")

    if not logical_name:
        raise Exception("Logical name is required")

    logging.debug("Retrieving entity collection name")
    endpoint = f"api/data/v9.2/entities"
    headers = {
        "Authorization": f"Bearer {service_client.get_access_token()}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }
    select = "$select=logicalcollectionname,logicalname,name"
    filter = f"$filter=logicalname eq '{logical_name}'"
    response = requests.get(
        f"{service_client.resource_url}/{endpoint}?{select}&{filter}",
        headers=headers,
    )
    response.raise_for_status()
    if not response.json()["value"]:
        return None
    else:
        return response.json()["value"][0]["logicalcollectionname"]


def transform_column_set(
    service_client: ServiceClient, entity_name: str, column_set: List[str]
) -> List[str]:
    """
    Transforms the column set based on the metadata for the given entity.
    If a column is a lookup or other non-primitive type, transforms it accordingly.
    """
    # Fetch the entity metadata
    metadata_endpoint = f"{service_client.resource_url}/api/data/v9.2/EntityDefinitions(LogicalName='{entity_name}')/Attributes?$select=LogicalName,AttributeType"
    headers = {
        "Authorization": f"Bearer {service_client.get_access_token()}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(metadata_endpoint, headers=headers)
    response.raise_for_status()
    metadata = response.json()

    # Transform the column set based on the metadata
    transformed_column_set = []
    for column in column_set:
        # Find the attribute metadata for the column
        attribute_metadata = next(
            (attr for attr in metadata["value"] if attr["LogicalName"] == column),
            None,
        )
        basic_attribute_types = [
            "BigInt",
            "DateTime",
            "Decimal",
            "Picklist",
            "State",
            "Status",
        ]
        if attribute_metadata:
            if (
                attribute_metadata["AttributeType"] == "Lookup"
                or attribute_metadata["AttributeType"] == "Owner"
            ):
                # If it's a lookup, append _value to the column name
                transformed_column_set.append(f"_{column}_value")
            elif attribute_metadata["AttributeType"] in basic_attribute_types:
                # If it's a state, append _value to the column name
                transformed_column_set.append(column)
            else:
                transformed_column_set.append(column)
        else:
            raise Exception(f"Attribute metadata not found for column: {column}")

    return transformed_column_set


def get_entity_metadata(
    entity_name: str, service_client: ServiceClient
) -> List[EntityMetadata]:
    """
    Retrieves the metadata for the given entity from the Dataverse service.
    """
    metadata_endpoint = f"{service_client.resource_url}/api/data/v9.2/EntityDefinitions(LogicalName='{entity_name}')/Attributes?$select=LogicalName,AttributeType,SchemaName"
    headers = {
        "Authorization": f"Bearer {service_client.get_access_token()}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(metadata_endpoint, headers=headers)
    response.raise_for_status()
    response_json = response.json()
    return EntityMetadataResponse.from_json(response_json).value


def parse_entity_to_web_api_body(
    entity: Entity, service_client: ServiceClient, logger: logging.Logger
) -> dict:
    """
    Parses an entity object to a dictionary that can be used as the body of a Web API request.
    """
    if not logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.WARNING)

    logger.debug(parse_entity_to_web_api_body.__name__)
    if not service_client.IsReady:
        msg = "Service client is not ready"
        logger.error(msg)
        raise Exception(msg)
    if not entity or not isinstance(entity, Entity):
        msg = "Entity of type datapyrse.core.Entity is required"
        logger.error(msg)
        raise Exception(msg)

    entity_metadata: List[EntityMetadata] = get_entity_metadata(
        entity.entity_logical_name, service_client
    )

    if not entity_metadata:
        raise Exception("Entity metadata not found")

    logger.debug(f"Metadata fetched: {str(entity_metadata.count)}")

    api_body: dict = {}
    for attr in entity.attributes:
        logger.debug(attr)
        value = entity.attributes[attr]
        if isinstance(value, EntityReference):
            logger.debug(f"{attr} is EntityReference")
            # Find the attribute metadata for the column
            attribute_metadata = next(
                (data for data in entity_metadata if attr == data.logical_name),
                None,
            )
            if attribute_metadata and attribute_metadata.attribute_type == "Lookup":
                binding_to: str = get_entity_collection_name_by_logical_name(
                    service_client, value.entity_logical_name
                )
                if not binding_to:
                    raise Exception(
                        f"Entity collection name not found for entity: {value.entity_logical_name}"
                    )
                logger.debug(f"Binding to {binding_to}")
                api_body[f"{attribute_metadata.schema_name}@odata.bind"] = (
                    f"/{binding_to}({str(value.entity_id)})"
                )

            else:
                msg = f"Attribute metadata not found for column: {attr}"
                logger.error(msg)
                logger.error(f"Attribute metadata: {attribute_metadata}")
                raise Exception(msg)
        elif isinstance(value, OptionSet):
            logger.debug(f"{attr} is OptionSet")
            api_body[attr] = value.value
        else:
            api_body[attr] = value

    return api_body
