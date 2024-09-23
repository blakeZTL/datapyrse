import logging
from typing import List
from core import ServiceClient
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
