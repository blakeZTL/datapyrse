"""A module for deleting entities from Dataverse"""

from dataclasses import dataclass
from logging import Logger
import logging

from requests import Request, Response

from datapyrse.models.methods import Method
from datapyrse.services.dataverse_request import DataverseRequest


def get_delete_request(
    dataverse_request: DataverseRequest,
    logger: Logger = logging.getLogger(__name__),
) -> Request:
    """
    Prepare a delete request for Dataverse

    Args:
        dataverse_request (DataverseRequest): DataverseRequest object
        logger (Logger): Logger object for logging

    Returns:
        Request: Request object for the delete request

    Raises:
        ValueError: If DataverseRequest is not provided
    """

    if not dataverse_request:
        msg = "DataverseRequest required and must be an instance of datapyrse.DataverseRequest"
        logger.error(msg)
        raise ValueError(msg)
    request: Request = Request(
        method=Method.DELETE.value,
        url=dataverse_request.endpoint,
        headers=dataverse_request.headers,
    )
    return request


@dataclass
class DeleteResponse:
    """
    Parse the response from a delete request to determine if the entity was deleted

    Args:
        response (Response): Response object from the delete request
        logger (Logger): Logger object for logging
    """

    response: Response
    logger: Logger = logging.getLogger(__name__)

    def __post_init__(self):
        if not self.response:
            msg = "Response required and must be an instance of requests.Response"
            self.logger.error(msg)
            raise ValueError(msg)

    def was_deleted(self) -> bool:
        """
        Determine if the entity was deleted

        Returns:
            bool: True if the entity was deleted, False otherwise
        """
        if self.response.ok:
            self.logger.info("Entity deleted")
            return True
        self.logger.error("Failed to delete entity")
        return False


# def delete_entity(
#     service_client,
#     logger: Logger = logging.getLogger(__name__),
#     **kwargs,
# ) -> bool:
#     """
#     Deletes an entity from Dataverse using the Web API.

#     This function allows deleting an entity in Dataverse based on provided entity
#     information. It accepts an `Entity`, `EntityReference`, or the combination of
#     `entity_name` and `entity_id`. The request is authenticated through the
#     `ServiceClient`, and it optionally allows bypassing custom plugin executions.

#     Args:
#         service_client (ServiceClient): The service client used to authenticate
#             and send the request.
#         logger (Logger, optional): A logger instance for logging debug, info,
#             and error messages. Defaults to a logger named after the current module.
#         **kwargs: Assortment of keyword arguments used to specify the entity to delete
#             and optional arguments to augment to request:
#             - entity (Entity): The entity instance to delete.
#             - entity_reference (EntityReference): Reference to the entity to delete.
#             - entity_name (str): Logical name of the entity.
#             - entity_id (UUID or str): ID of the entity to delete.
#             - BypassCustomPluginExecution (bool): Bypass plug-in logic if caller has prvBypassCustomPlugins privilege.
#             - SuppressCallbackRegistrationExpanderJob (bool): Surpress the triggering of a Power Automate.
#             - tag (str): Add a shared variable to the plugin execution context.

#     Returns:
#         bool: True if the entity was successfully deleted, False otherwise.

#     Raises:
#         ValueError: If required parameters like `service_client`, `entity_id`, or
#                     `entity_name` are missing or invalid, or if the service client
#                     is not ready.
#     """
#     entity_id: str | None = None
#     entity_name: str | None = None

#     from datapyrse.services.service_client import ServiceClient

#     if not service_client or not isinstance(service_client, ServiceClient):
#         logger.error("ServiceClient is required and must be of type ServiceClient")
#         raise ValueError("ServiceClient is required and must be of type ServiceClient")

#     if not logger:
#         logger = service_client._prepare_request()
#     if not kwargs:
#         logger.error("At least one argument is required")
#         raise ValueError("At least one argument is required")
#     logger.debug(f"Deleting entity with args: {kwargs}")
#     if "entity" in kwargs:
#         entity: Entity = kwargs["entity"]
#         if isinstance(entity, Entity):
#             if entity.entity_id is None:
#                 logger.error("entity_id is required")
#                 raise ValueError("entity_id is required")
#             if entity.entity_logical_name is None:
#                 logger.error("entity_name is required")
#                 raise ValueError("entity_name is required")
#             entity_id = str(entity.entity_id)
#             entity_name = entity.entity_logical_name
#         else:
#             logger.error("entity must be of type Entity")
#             raise ValueError("entity must be of type Entity")
#     if "entity_reference" in kwargs:
#         entity_reference = kwargs["entity_reference"]
#         if isinstance(entity_reference, EntityReference):
#             entity_id = str(entity_reference.entity_id)
#             entity_name = entity_reference.entity_logical_name
#         else:
#             logger.error("entity_reference must be of type EntityReference")
#             raise ValueError("entity_reference must be of type EntityReference")
#     if "entity_name" in kwargs and "entity_id" in kwargs:
#         entity_id = kwargs["entity_id"]
#         entity_name = kwargs["entity_name"]
#         if not isinstance(entity_id, UUID) and not isinstance(entity_id, str):
#             logger.error("entity_id must be of type UUID or str")
#             raise ValueError("entity_id must be of type UUID or str")
#         else:
#             entity_id = str(entity_id)
#         if not isinstance(entity_name, str):
#             logger.error("entity_name must be of type str")
#             raise ValueError("entity_name must be of type str")
#     if "entity_name" in kwargs and "entity_id" not in kwargs:
#         logger.error("entity_id is required")
#         raise ValueError("entity_id is required")
#     if "entity_id" in kwargs and "entity_name" not in kwargs:
#         logger.error("entity_name is required")
#         raise ValueError("entity_name is required")

#     if not entity_name:
#         raise ValueError("entity_name never set")
#     if not entity_id:
#         raise ValueError("entity_id never set")

#     # delete entity
#     if not service_client.metadata.entities:
#         logger.error("Metadata entities not found")
#         raise ValueError("Metadata entities not found")

#     entity_metadata: EntityMetadata | None = next(
#         (
#             entity_meta
#             for entity_meta in service_client.metadata.entities
#             if entity_meta.logical_name == entity_name
#         ),
#         None,
#     )
#     if not entity_metadata:
#         logger.error(f"Entity {entity_name} not found in metadata")
#         raise ValueError(f"Entity {entity_name} not found in metadata")
#     entity_plural_name = entity_metadata.logical_collection_name
#     if not entity_plural_name:
#         logger.error(f"Entity {entity_name} does not have a plural name")
#         raise ValueError(f"Entity {entity_name} does not have a plural name")

#     url: str = (
#         f"{service_client.resource_url}/api/data/v9.2/{entity_plural_name}({entity_id})"
#     )
#     headers: dict = service_client._get_request_headers(**kwargs)
#     if kwargs.get("tag") is not None:
#         tag: str = str(kwargs["tag"])
#         url += f"?tag={tag}"

#     response: Response = requests.delete(url, headers=headers)
#     response.raise_for_status()
#     if response.ok:
#         logger.info(f"Entity {entity_name} with id {entity_id} deleted")
#         return True
#     logger.error(f"Failed to delete entity {entity_name} with id {entity_id}")
#     return False
