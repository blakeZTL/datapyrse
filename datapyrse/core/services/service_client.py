import logging
from logging import Logger
import time
from typing import List
from uuid import UUID

import msal
from requests import Response
import requests

from datapyrse.core.models.column_set import ColumnSet
from datapyrse.core.models.entity import Entity
from datapyrse.core.models.entity_collection import EntityCollection
from datapyrse.core.models.entity_metadata import EntityMetadata, OrgMetadata
from datapyrse.core.models.entity_reference import EntityReference
from datapyrse.core.models.query_expression import QueryExpression
from datapyrse.core.utils.dataverse import (
    parse_entity_to_web_api_body,
    transform_column_set,
)


class ServiceClient:

    def __init__(
        self,
        tenant_id: str,
        resource_url: str,
        client_id: str = "51f81489-12ee-4a9e-aaae-a2591f45987d",
        scope=None,
        prompt=None,
        logger: Logger = logging.getLogger(__name__),
    ) -> None:
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.resource_url = resource_url
        self.authority_url = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = scope or [f"{resource_url}/.default"]
        self.prompt = prompt
        self.msal_app = msal.PublicClientApplication(
            client_id=self.client_id, authority=self.authority_url
        )
        self.access_token: str | None = None
        self.token_expiry: float | None = None
        self.IsReady = False
        self.logger = logger

    def __post_init__(self):
        if not self.logger:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.WARNING)
        self._acquire_token()
        self.metadata = self._get_metadata()
        if self.access_token and self.token_expiry and time.time() > self.token_expiry:
            self.IsReady = True
        if not self.metadata:
            self.logger.error("Failed to get metadata")
            raise ValueError("Failed to get metadata")

    def _get_metadata(self) -> OrgMetadata:
        from datapyrse.core.utils.dataverse import get_metadata

        self.logger.debug("Getting metadata")
        return get_metadata(self, self.logger)

    def _acquire_token(self) -> None:
        self.IsReady = False
        self.logger.debug("Acquiring token")
        self.logger.debug("Acquiring interactive token")
        result = self.msal_app.acquire_token_interactive(
            scopes=self.scope, prompt=self.prompt
        )
        if "access_token" in result:
            self.token = result
            self.access_token = str(self.token["access_token"])
            if "expires_in" in self.token and isinstance(
                self.token["expires_in"], float
            ):
                self.token_expiry = time.time() + float(self.token["expires_in"])
            self.IsReady = True
        else:
            raise Exception(
                f"Failed to acquire token: {result.get('error')}, {result.get('error_description')}"
            )

    def get_access_token(self) -> str:
        self.IsReady = False
        self.logger.debug("Getting access token")
        if not self.access_token or (
            self.token_expiry and time.time() > self.token_expiry
        ):
            self.logger.debug("Acquiring new token")
            self._acquire_token()
        self.logger.debug("Returning access token")
        self.IsReady = True
        if not self.access_token:
            raise ValueError("Failed to get access token")
        return self.access_token

    def create(
        self,
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

        logger = self._prepare_request(logger, entity)

        logger.debug("Creating entity")
        if not self.metadata.entities:
            logger.error("Metadata entities not found")
            raise Exception("Metadata entities not found")

        entity_plural_name: str | None = next(
            (
                data.logical_collection_name
                for data in self.metadata.entities
                if data.logical_name == entity.entity_logical_name
            ),
            None,
        )
        if not entity_plural_name:
            logger.error("Entity collection name not found")
            logger.error(f"Entity logical name: {entity.entity_logical_name}")
            logger.error(f"Entities: {self.metadata.entities}")
            raise Exception("Entity collection name not found")
        logger.debug(f"Entity plural name: {entity_plural_name}")

        parsed_entity_data: dict = parse_entity_to_web_api_body(
            entity,
            self,
            logger,
            entity_logical_collection_name=entity_plural_name,
        )

        endpoint: str = f"api/data/v9.2/{entity_plural_name}"

        headers: dict = self._get_request_headers(**kwargs)

        if kwargs and kwargs.get("tag") is not None:
            tag: str = str(kwargs["tag"])
            endpoint += f"?tag={tag}"

        response: Response = requests.post(
            f"{self.resource_url}/{endpoint}",
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

    def retrieve(
        self,
        entity_logical_name: str,
        entity_id: UUID,
        column_set: ColumnSet,
        logger: Logger = logging.getLogger(__name__),
    ) -> Entity:
        """
        Retrieves an entity from Dataverse by its logical name and ID.

        This function sends a GET request to the Dataverse Web API to fetch an entity
        based on its logical name and unique identifier (entity_id). It allows selecting
        specific columns (fields) to be retrieved via the column_set parameter.

        Args:
            service_client (ServiceClient): The service client used to authenticate
                and send the request.
            entity_logical_name (str): The logical name of the entity in Dataverse.
            entity_id (uuid.UUID): The unique identifier of the entity to retrieve.
            column_set (ColumnSet): A list of attribute names (columns) to be retrieved
                from the entity.
            logger (logging.Logger, optional): A logger instance for logging debug
                and error messages. Defaults to None.

        Returns:
            Entity: The retrieved entity with its attributes populated.

        Raises:
            Exception: Raised if the service client is not ready, if the entity logical
                name or ID is missing, if the column set transformation fails, or if
                the entity cannot be found.
        """

        logger = self._prepare_request(logger)

        if not entity_logical_name:
            raise Exception("Entity plural name is required")

        if not entity_id:
            raise Exception("Entity ID is required")

        if not column_set:
            raise Exception("Column set is required")

        if not self.metadata.entities:
            raise Exception("Metadata entities not found")
        entity_plural_name: str | None = next(
            (
                data.logical_collection_name
                for data in self.metadata.entities
                if data.logical_name == entity_logical_name
            ),
            None,
        )
        if not entity_plural_name:
            raise Exception("Entity collection name not found")

        select: str | None = None
        if isinstance(column_set, list):
            parsed_column_set: List[str] = transform_column_set(
                self, entity_logical_name, column_set
            )
            if not parsed_column_set:
                raise Exception("Failed to transform column set")
            select = ",".join(parsed_column_set)

        logger.debug("Retrieving entity")
        endpoint: str = f"api/data/v9.2/{entity_plural_name}({str(entity_id)})"
        headers: dict = self._get_request_headers()
        url: str = f"{self.resource_url}/{endpoint}"
        if select:
            url = f"{url}?$select={select}"

        response: Response = requests.get(
            url,
            headers=headers,
        )
        response.raise_for_status()
        entity: Entity = Entity(
            entity_id=entity_id,
            entity_logical_name=entity_logical_name,
            attributes=response.json(),
            logger=logger,
        )
        return entity

    def retrieve_multiple(
        self,
        query: QueryExpression,
        logger: Logger = logging.getLogger(__name__),
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

        logger = self._prepare_request(logger)

        if not query:
            raise Exception("Query is required")
        else:
            if not isinstance(query, QueryExpression):
                raise Exception("Query must be a QueryExpression")

        entity_logical_name: str = query.entity_name
        if not entity_logical_name:
            raise ValueError("Entity logical name not found in query")

        if not self.metadata.entities:
            raise Exception("Metadata entities not found")

        entity_plural_name: str | None = next(
            (
                data.logical_collection_name
                for data in self.metadata.entities
                if data.logical_name == entity_logical_name
            ),
            None,
        )
        if not entity_plural_name:
            raise Exception("Entity collection name not found")

        logger.debug("Retrieving entities")
        endpoint: str = f"api/data/v9.2/{entity_plural_name}"
        headers: dict = self._get_request_headers()

        fetch_xml: str = query.to_fetchxml()
        if fetch_xml:
            endpoint += f"?fetchXml={fetch_xml}"
        else:
            raise Exception("Failed to parse query expression")

        url: str = f"{self.resource_url}/{endpoint}"

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
            return EntityCollection(
                entity_logical_name=entity_logical_name, entities=[]
            )

        entities: EntityCollection = EntityCollection(
            entity_logical_name=entity_logical_name
        )
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

    def delete_entity(
        self,
        logger: Logger = logging.getLogger(__name__),
        **kwargs,
    ) -> bool:
        """
        Deletes an entity from Dataverse using the Web API.

        This function allows deleting an entity in Dataverse based on provided entity
        information. It accepts an `Entity`, `EntityReference`, or the combination of
        `entity_name` and `entity_id`. The request is authenticated through the
        `ServiceClient`, and it optionally allows bypassing custom plugin executions.

        Args:
            service_client (ServiceClient): The service client used to authenticate
                and send the request.
            logger (Logger, optional): A logger instance for logging debug, info,
                and error messages. Defaults to a logger named after the current module.
            **kwargs: Assortment of keyword arguments used to specify the entity to delete
                and optional arguments to augment to request:
                - entity (Entity): The entity instance to delete.
                - entity_reference (EntityReference): Reference to the entity to delete.
                - entity_name (str): Logical name of the entity.
                - entity_id (UUID or str): ID of the entity to delete.
                - BypassCustomPluginExecution (bool): Bypass plug-in logic if caller has prvBypassCustomPlugins privilege.
                - SuppressCallbackRegistrationExpanderJob (bool): Surpress the triggering of a Power Automate.
                - tag (str): Add a shared variable to the plugin execution context.

        Returns:
            bool: True if the entity was successfully deleted, False otherwise.

        Raises:
            ValueError: If required parameters like `service_client`, `entity_id`, or
                        `entity_name` are missing or invalid, or if the service client
                        is not ready.
        """
        entity_id: str | None = None
        entity_name: str | None = None

        if not logger:
            logger = self._prepare_request()
        if not kwargs:
            logger.error("At least one argument is required")
            raise ValueError("At least one argument is required")
        logger.debug(f"Deleting entity with args: {kwargs}")
        if "entity" in kwargs:
            entity: Entity = kwargs["entity"]
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
                entity_id = str(entity_reference.entity_id)
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

        if not entity_name:
            raise ValueError("entity_name never set")
        if not entity_id:
            raise ValueError("entity_id never set")

        # delete entity
        if not self.metadata.entities:
            logger.error("Metadata entities not found")
            raise ValueError("Metadata entities not found")

        entity_metadata: EntityMetadata | None = next(
            (
                entity_meta
                for entity_meta in self.metadata.entities
                if entity_meta.logical_name == entity_name
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
            f"{self.resource_url}/api/data/v9.2/{entity_plural_name}({entity_id})"
        )
        headers: dict = self._get_request_headers(**kwargs)
        if kwargs.get("tag") is not None:
            tag: str = str(kwargs["tag"])
            url += f"?tag={tag}"

        response: Response = requests.delete(url, headers=headers)
        response.raise_for_status()
        if response.ok:
            logger.info(f"Entity {entity_name} with id {entity_id} deleted")
            return True
        logger.error(f"Failed to delete entity {entity_name} with id {entity_id}")
        return False

    def _get_request_headers(self, **kwargs) -> dict:
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Prefer": "odata.include-annotations=*",
        }
        if kwargs:
            if kwargs.get("SuppressDuplicateDetection") is not None:
                value: str = str(kwargs["SuppressDuplicateDetection"]).lower()
                headers["MSCRM.SuppressDuplicateDetection"] = (
                    value if value in ["true", "false"] else "false"
                )
            if kwargs.get("BypassCustomPluginExecution") is not None:
                value: str = str(kwargs["BypassCustomPluginExecution"]).lower()
                headers["MSCRM.BypassCustomPluginExecution"] = (
                    value if value in ["true", "false"] else "false"
                )
            if kwargs.get("SuppressCallbackRegistrationExpanderJob") is not None:
                value: str = str(
                    kwargs["SuppressCallbackRegistrationExpanderJob"]
                ).lower()
                headers["MSCRM.SuppressCallbackRegistrationExpanderJob"] = (
                    value if value in ["true", "false"] else "false"
                )
        return headers

    def _prepare_request(self, logger: Logger | None, entity: Entity | None = None):
        """
        Prepares for making a service call by ensuring the client is ready,
        and validating input parameters like entity and logger.
        """
        if not logger:
            logger = self.logger

        if not self.IsReady:
            logger.error("Service client is not ready")
            raise Exception("Service client is not ready")

        if not self.metadata.entities:
            logger.error("Metadata entities not found")
            raise Exception("Metadata entities not found")

        if entity:
            if not isinstance(entity, Entity):
                logger.error("Entity is not of type Entity")
                raise Exception("Entity is not of type Entity")
            if not entity.entity_logical_name:
                logger.error("Entity logical name is required")
                raise Exception("Entity logical name is required")
            if not entity.entity_id:
                logger.error("Entity ID is required")
                raise Exception("Entity ID is required")

        return logger
