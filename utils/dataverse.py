import logging
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
