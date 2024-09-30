"""
A module for utility functions related to Dataverse
"""

import logging
from logging import Logger
from typing import Any, List


from datapyrse._entity_metadata import EntityMetadata, OrgMetadata
from datapyrse.query._column_set import ColumnSet
from datapyrse._entity import Entity
from datapyrse._entity_reference import EntityReference
from datapyrse.query._option_set import OptionSet

DEFAULT_HEADERS: dict[str, str] = {
    "OData-MaxVersion": "4.0",
    "OData-Version": "4.0",
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Prefer": "odata.include-annotations=*",
}


def get_entity_collection_name_by_logical_name(
    org_metadata: OrgMetadata,
    logical_name: str,
    logger: Logger = logging.getLogger(__name__),
) -> str | None:
    """
    Retrieves the collection name for an entity based on the logical name.

    Args:
        org_metadata (OrgMetadata): The metadata for the organization.
        logical_name (str): The logical name of the entity.
        logger (Logger): The logger to use for logging.

    Returns:
        str: The collection name for the entity.
        None: If no metadata found for the entity.

    Raises:
        ValueError: If the logical name is not provided.
        ValueError: If the organization metadata is not provided.
        ValueError: If the organization metadata entities are not provided.
    """

    if not logical_name:
        msg = "Logical name is required"
        logger.error(msg)
        raise ValueError(msg)

    if not org_metadata:
        msg = "org_metadata required"
        logger.error(msg)
        raise ValueError(msg)
    if not org_metadata.entities:
        logger.warning(
            "Entities not found on OrgMetadata. Returning collection name of None"
        )
        return None
    entity_metadata: EntityMetadata | None = next(
        (
            metadata
            for metadata in org_metadata.entities
            if metadata.logical_name == logical_name
        ),
        None,
    )
    if not entity_metadata:
        logger.warning(
            "No matching metadata found for %s. Returning collection name of None",
            logical_name,
        )
        return None
    logger.debug("Returning %s.", entity_metadata.logical_collection_name)
    return entity_metadata.logical_collection_name


def transform_column_set(
    entity_metadata: EntityMetadata, column_set: ColumnSet
) -> List[str]:
    """
    Transforms the column set based on the metadata for the given entity.
    If a column is a lookup or other non-primitive type, transforms it accordingly.

    Args:
        entity_metadata (EntityMetadata): The metadata for the entity.
        entity_name (str): The logical name of the entity.
        column_set (List[str]): The list of columns to transform.

    Returns:
        List[str]: The transformed column set.

    Raises:
        Exception: If the entity metadata is not found, if the entity metadata attributes are not found,
            or if the column set is not found.
    """
    if not entity_metadata:
        raise ValueError("Entity metadata is required")
    if not entity_metadata.attributes:
        raise ValueError("Entity metadata attributes not found")
    if not column_set or not isinstance(column_set.columns, list):
        raise ValueError("Column set is required")
    if not column_set.columns:
        raise ValueError("Column set columns not found")
    transformed_column_set: List[str] = []
    for column in column_set.columns:
        # Find the attribute metadata for the column
        attribute_metadata = next(
            (
                attr
                for attr in entity_metadata.attributes
                if attr.logical_name == column
            ),
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
            if attribute_metadata.attribute_type in ["Lookup", "Owner"]:
                # If it's a lookup, append _value to the column name
                transformed_column_set.append(f"_{column}_value")
            elif attribute_metadata.attribute_type in basic_attribute_types:
                # If it's a state, append _value to the column name
                transformed_column_set.append(column)
            else:
                transformed_column_set.append(column)
        else:
            raise ValueError(f"Attribute metadata not found for column: {column}")

    return transformed_column_set


def get_entity_metadata(
    entity_logical_name: str,
    org_metadata: OrgMetadata,
    logger: Logger = logging.getLogger(__name__),
) -> EntityMetadata:
    """
    Retrieves the metadata for a specific entity from Organization Metadata.

    Args:
        entity_logical_name (str): The logical name of the entity.
        org_metadata (OrgMetadata): The metadata for the organization.
        logger (logging.Logger): The logger to use for logging.

    Returns:
        EntityMetadata: The metadata for the entity.

    Raises:
        Exception: If the entity metadata is not found.
    """
    if not org_metadata:
        msg = "Organization metadata is required"
        logger.error(msg)
        raise ValueError(msg)
    if not org_metadata.entities:
        msg = "Organization metadata entities not found"
        logger.error(msg)
        raise ValueError(msg)
    entity_metadata = next(
        (
            data
            for data in org_metadata.entities
            if entity_logical_name == data.logical_name
        ),
        None,
    )
    if not entity_metadata:
        msg = f"Entity metadata not found for entity: {entity_logical_name}"
        logger.error(msg)
        raise ValueError(msg)

    return entity_metadata


def parse_entity_to_web_api_body(
    entity: Entity,
    org_metadata: OrgMetadata,
    logger: Logger = logging.getLogger(__name__),
) -> dict[str, Any] | None:
    """
    Parses an entity object to a Web API body.

    Args:
        entity (Entity): The entity object to parse.
        org_metadata (OrgMetadata): The metadata for the organization.
        logger (Logger): The logger to use for logging.

    Returns:
        dict: The parsed Web API body.

    Raises:
        ValueError: If the entity is not provided.
        ValueError: If the entity has no attributes.
        ValueError: If the organization metadata is not provided.
        ValueError: If the entity metadata is not found.
        ValueError: If the entity metadata attributes are not found.
        ValueError: If the attribute metadata is not found for a column.
    """

    logger.debug(parse_entity_to_web_api_body.__name__)
    if not entity:
        msg = "Entity of type datapyrse.Entity is required"
        logger.error(msg)
        raise ValueError(msg)
    if not entity.attributes:
        msg = "Entity has no attributes to parse"
        logger.warning(msg)
        return None
    if not org_metadata:
        msg = "Organization Metadata required."
        logger.error(msg)
        raise ValueError(msg)

    entity_metadata: EntityMetadata = get_entity_metadata(
        entity.entity_logical_name, org_metadata, logger
    )

    if not entity_metadata:
        raise ValueError("Entity metadata not found")

    if not entity_metadata.attributes:
        raise ValueError("Entity metadata attributes not found")

    logger.debug("Metadata fetched: %s", len(entity_metadata.attributes))

    api_body: dict[str, Any] = {}
    for attr in entity.attributes:
        logger.debug(attr)
        value = entity.attributes[attr]
        if isinstance(value, EntityReference):
            logger.debug("%s is EntityReference", attr)
            # Find the attribute metadata for the column
            attribute_metadata = next(
                (
                    data
                    for data in entity_metadata.attributes
                    if attr == data.logical_name
                ),
                None,
            )
            if (
                not attribute_metadata
                or not attribute_metadata.attribute_type == "Lookup"
            ):
                msg = f"Attribute metadata not found for column: {attr}"
                logger.error(msg)
                logger.error("Attribute metadata: %s", attribute_metadata)
                raise ValueError(msg)

            logger.debug("%s is Lookup", attr)
            binding_to: str | None = None
            if org_metadata.entities:
                binding_to = next(
                    (
                        data.logical_collection_name
                        for data in org_metadata.entities
                        if data.logical_name == value.entity_logical_name
                    ),
                    None,
                )

            if not binding_to:
                raise ValueError(
                    f"Entity collection name not found for entity: {value.entity_logical_name}"
                )
            logger.debug("Binding to %s", binding_to)
            api_body[f"{attribute_metadata.schema_name}@odata.bind"] = (
                f"/{binding_to}({str(value.entity_id)})"
            )

        elif isinstance(value, OptionSet):
            logger.debug("%s is OptionSet", attr)
            api_body[attr] = value.value
        else:
            api_body[attr] = value

    return api_body
