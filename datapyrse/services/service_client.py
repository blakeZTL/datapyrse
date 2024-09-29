"""
A module for interacting with Dataverse using the Web API

"""

from enum import StrEnum
import logging
from logging import Logger
import time
from typing import Any, List, Optional
from uuid import UUID


from msal import PublicClientApplication  # type: ignore
from requests import PreparedRequest, Session
import requests
from requests import Request, Response


from datapyrse.models.column_set import ColumnSet
from datapyrse.models.entity_metadata import OrgMetadata
from datapyrse.models.query_expression import QueryExpression
from datapyrse.services.create import CreateResponse
from datapyrse.models.entity import Entity
from datapyrse.services.dataverse_request import DataverseRequest
from datapyrse.services.create import get_create_request
from datapyrse.services.delete import DeleteResponse, get_delete_request
from datapyrse.services.retrieve import RetrieveResponse, get_retrieve_request
from datapyrse.services.retrieve_multiple import (
    RetrieveMultipleResponse,
    get_retrieve_multiple_request,
)
from datapyrse.utils.dataverse import DEFAULT_HEADERS


class Prompt(StrEnum):
    """
    Enum for the prompt parameter in the OAuth 2.0 authorization request.

    The prompt parameter can be used to control the authentication flow of the
    user. The possible values are:
    - none: No user interaction is required.
    - select_account: The user is prompted to select an account.
    - consent: The user is prompted to consent to the requested permissions.
    - login: The user is prompted to log in.

    Reference:
    https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#request-an-authorization-code

    """

    NONE = "none"
    SELECT_ACCOUNT = "select_account"
    CONSENT = "consent"
    LOGIN = "login"


class ServiceClient:
    """
    A client for interacting with Dataverse using the Web API.

    This class provides methods for creating, retrieving, updating, and deleting
    entities in Dataverse using the Web API. It uses the MSAL library for
    authentication and requests for sending HTTP requests.

    Args:
        tenant_id (str): The Azure AD tenant ID.
        resource_url (str): The resource URL for the Dataverse instance.
        client_id (str): The client ID for the application. Defaults to the
            default client ID for Dataverse applications.
        scope (List[str]): The scope for the authentication request. Defaults to
            the default scope for Dataverse applications.
        prompt (Prompt): The prompt parameter for the authentication request.
            Defaults to Prompt.NONE.
        logger (Logger): The logger instance for logging debug, info, and error
            messages. Defaults to a logger named after the current module.

    Attributes:
        client_id (str): The client ID for the application.
        tenant_id (str): The Azure AD tenant ID.
        resource_url (str): The resource URL for the Dataverse instance.
        authority_url (str): The authority URL for the authentication request.
        scope (List[str]): The scope for the authentication request.
        prompt (Prompt): The prompt parameter for the authentication request.
        token_expiry (float): The expiry time for the access token.
        is_ready (bool): A flag indicating if the client is ready to make requests.
        logger (Logger): The logger instance for logging debug, info, and error
            messages.

    """

    def __init__(
        self,
        tenant_id: str,
        resource_url: str,
        client_id: str = "51f81489-12ee-4a9e-aaae-a2591f45987d",
        scope: Optional[List[str]] = None,
        prompt: Prompt = Prompt.NONE,
        logger: Logger = logging.getLogger(__name__),
    ) -> None:
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.resource_url = resource_url
        self.authority_url = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = scope or [f"{resource_url}/.default"]
        self.prompt = prompt
        self._msal_app = PublicClientApplication(
            client_id=self.client_id, authority=self.authority_url
        )
        self._access_token: str | None = None
        self.token_expiry: float | None = None
        self.is_ready = False
        self.logger = logger
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.logger.level)

            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)
        self.__post_init__()

    def __post_init__(self):
        self._acquire_token()
        self.metadata = self._get_metadata()
        if self._access_token and self.token_expiry and time.time() > self.token_expiry:
            self.is_ready = True
        if not self.metadata:
            self.logger.error("Failed to get metadata")
            raise ValueError("Failed to get metadata")

    def __repr__(self) -> str:
        return (
            f"ServiceClient(tenant_id={self.tenant_id}, "
            + f"resource_url={self.resource_url}, "
            + f"client_id={self.client_id}, "
            + f"scope={self.scope}, "
            + f"is_ready={self.is_ready}, "
            + f"token_expiry={self.token_expiry})"
        )

    def _get_metadata(self) -> OrgMetadata:
        self.logger.debug("Getting metadata")

        endpoint: str = (
            "api/data/v9.2/EntityDefinitions?"
            + "$expand=Attributes($select="
            + "LogicalName,AttributeType,SchemaName)"
        )

        headers: dict[str, str] = DEFAULT_HEADERS
        headers["Authorization"] = f"Bearer {self._get_access_token()}"
        response = requests.get(
            f"{self.resource_url}/{endpoint}", headers=headers, timeout=60
        )
        response.raise_for_status()
        response_json = response.json()
        if not response_json or not response_json["value"]:
            self.logger.error("No metadata found")
            raise ValueError("No metadata found")

        org_metadata: OrgMetadata = OrgMetadata.from_json(response_json)
        if not org_metadata.entities:
            self.logger.warning("No entity metadata found")
        else:
            self.logger.debug("Metadata fetched: %s", len(org_metadata.entities))
        return org_metadata

    def _acquire_token(self) -> None:
        self.is_ready = False
        self.logger.debug("Acquiring token")
        self.logger.debug("Acquiring interactive token")
        result: Any = self._msal_app.acquire_token_interactive(  # type: ignore
            scopes=self.scope, prompt=self.prompt.value
        )
        if "access_token" in result:
            self.token = result
            self._access_token = str(self.token["access_token"])
            if "expires_in" in self.token and isinstance(
                self.token["expires_in"], float
            ):
                self.token_expiry = time.time() + float(self.token["expires_in"])
            self.is_ready = True
        else:
            raise ValueError(
                f"Failed to acquire token: {result.get('error')}, {result.get('error_description')}"
            )

    def _execute(self, request: Request):
        self.logger.debug(__name__)
        if not request:
            msg = "Request is required and must be an instance of requests.Request"
            self.logger.error(msg)
            raise ValueError(msg)
        self.logger.debug(request.method)
        self.logger.debug(request.url)
        self.logger.debug(request.headers)
        self.logger.debug(request.json)
        request.headers["Authorization"] = f"Bearer {self._get_access_token()}"
        session: Session = Session()
        prepared_request: PreparedRequest = session.prepare_request(request)
        response: Response = session.send(prepared_request)
        self.logger.debug(response)
        self.logger.debug(response.headers)
        self.logger.debug(response.text)
        return response

    def _get_access_token(self) -> str:
        self.is_ready = False
        if not self._access_token or (
            self.token_expiry and time.time() > self.token_expiry
        ):
            self.logger.warning("Acquiring new token")
            self._acquire_token()
        self.is_ready = True
        if not self._access_token:
            raise ValueError("Failed to get access token")
        return self._access_token

    def create(
        self,
        entity: Entity,
        logger: Optional[Logger] = None,
        suppress_duplicate_detection: bool = False,
        bypass_custom_plugin_execution: bool = False,
        suppress_power_automate_triggers: bool = False,
        tag: Optional[str] = None,
    ) -> CreateResponse:
        """
        Creates a new entity in Dataverse using the Web API.

        This function allows creating a new entity in Dataverse based on the provided
        entity information. It sends a POST request to the Dataverse Web API to create
        the entity and returns the response.

        Args:
            entity (Entity): The entity instance to create.
            logger (Logger, optional): A logger instance for logging debug, info,
                and error messages. Defaults to a logger named after the current module.
            suppress_duplicate_detection (bool, optional): Bypass duplicate detection
                logic if caller has prvBypassCustomPlugins privilege. Defaults to False.
            bypass_custom_plugin_execution (bool, optional): Bypass plug-in logic if
                caller has prvBypassCustomPlugins privilege. Defaults to False.
            suppress_power_automate_triggers (bool, optional): Suppress the triggering
                of a Power Automate. Defaults to False.
            tag (str, optional): Add a shared variable to the plugin execution context.
                Defaults to None.

        Returns:
            CreateResponse: The response from the create request.

        Raises:
            ValueError: If entity is not provided.

        Example:
            >>> from datapyrse import Entity, ServiceClient
            >>>
            >>> entity = Entity(entity_logical_name="account", attributes={"name": "Test Account"})
            >>> service_client = ServiceClient(tenant_id="...", resource_url="...")
            >>> create_response = service_client.create(entity=entity)
        """

        if not logger:
            logger = self.logger

        dataverse_request: DataverseRequest = DataverseRequest(
            base_url=self.resource_url,
            org_metadata=self.metadata,
            entity=entity,
            tag=tag,
            suppress_duplicate_detection=suppress_duplicate_detection,
            bypass_custom_plugin_execution=bypass_custom_plugin_execution,
            suppress_callback_registration_expander_job=suppress_power_automate_triggers,
            logger=logger,
        )
        request: Request = get_create_request(
            dataverse_request=dataverse_request,
            logger=logger,
        )

        response: Response = self._execute(request=request)
        create_response: CreateResponse = CreateResponse(
            response=response, entity=entity, logger=logger
        )
        return create_response

    def retrieve(
        self,
        entity_logical_name: str,
        entity_id: UUID | str,
        column_set: ColumnSet,
        logger: Logger = logging.getLogger(__name__),
    ) -> RetrieveResponse:
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

        Example:
            >>> from datapyrse import ServiceClient
            >>> from datapyse.query import ColumnSet
            >>>
            >>> service_client = ServiceClient(tenant_id="...", resource_url="...")
            >>> entity = service_client.retrieve(
            ...     entity_logical_name="account",
            ...     entity_id="...",
            ...     column_set=ColumnSet(["name", "ownerid"])
            ... )
        """

        if not entity_logical_name:
            msg = "Entity logical name is required"
            logger.error(msg)
            raise ValueError(msg)
        if not entity_id:
            msg = "Entity ID is required"
            logger.error(msg)
            raise ValueError(msg)
        if not column_set:
            msg = "Column set is required"
            logger.error(msg)
            raise ValueError(msg)

        entity: Entity = Entity(
            entity_logical_name=entity_logical_name,
        )
        if isinstance(entity_id, str):
            try:
                entity_id = UUID(entity_id)
            except ValueError as exc:
                msg = "Entity ID must be a valid UUID"
                logger.error(msg)
                raise ValueError(msg) from exc
        else:
            entity.entity_id = entity_id

        dataverse_request: DataverseRequest = DataverseRequest(
            base_url=self.resource_url,
            org_metadata=self.metadata,
            entity=entity,
            logger=logger,
        )

        request: Request = get_retrieve_request(
            dataverse_request=dataverse_request,
            column_set=column_set,
            logger=logger,
        )

        response: Response = self._execute(request=request)
        retrieve_response: RetrieveResponse = RetrieveResponse(
            response=response, entity=entity, logger=logger
        )
        return retrieve_response

    def retrieve_multiple(
        self, query: QueryExpression, logger: Logger = logging.getLogger(__name__)
    ) -> RetrieveMultipleResponse:
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
            EntityCollection: A collection of entities matching the query embedded in the response.

        Raises:
            Exception: Raised if the service client is not ready, the query is invalid,
                or the API request fails.

        Example:
            >>> from datapyrse import ServiceClient
            >>> from datapyse.query import QueryExpression
            >>>
            >>> query = QueryExpression(
            ...     entity_name= "account",
            ...     column_set= ColumnSet(["name"])
            ...     criteria= FilterExpression(
            ...         conditions=[
            ...             ConditionExpression(
            ...                 attribute_name="name",
            ...                 operator=ConditionOperator.EQUAL,
            ...                 value="Test",
            ...             )
            ...         ]
            ...     )
            ... )
            >>> service_client = ServiceClient(tenant_id="...", resource_url="...")
            >>> retrieve_multiple_response = service_client.retrieve_multiple(query=query)
        """

        if not query:
            msg = "Query is required"
            logger.error(msg)
            raise ValueError(msg)

        entity_logical_name: str = query.entity_name
        if not entity_logical_name:
            msg = "Entity logical name not found in query"
            logger.error(msg)
            raise ValueError(msg)

        dataverse_request: DataverseRequest = DataverseRequest(
            base_url=self.resource_url,
            org_metadata=self.metadata,
            entity=Entity(entity_logical_name=entity_logical_name),
            logger=logger,
        )

        request: Request = get_retrieve_multiple_request(
            dataverse_request=dataverse_request,
            query=query,
            logger=logger,
        )

        response: Response = self._execute(request=request)
        retrieve_response: RetrieveMultipleResponse = RetrieveMultipleResponse(
            response=response, entity_logical_name=entity_logical_name, logger=logger
        )

        return retrieve_response

    def delete(
        self,
        entity_logical_name: str,
        entity_id: UUID | str,
        logger: Logger = logging.getLogger(__name__),
    ) -> DeleteResponse:
        """
        Deletes an entity from Dataverse using the Web API.

        This function allows deleting an entity in Dataverse based on the provided entity
        information. It accepts an entity logical name and unique identifier (entity_id)
        to identify the entity to delete. The request is authenticated through the
        ServiceClient and returns the response.

        Args:
            entity_logical_name (str): The logical name of the entity in Dataverse.
            entity_id (uuid.UUID | str): The unique identifier of the entity to delete.
            logger (logging.Logger, optional): A logger instance for logging debug,
                info, and error messages. Defaults to None.

        Returns:
            DeleteResponse: The response from the delete request.

        Raises:
            ValueError: If entity logical name or ID is missing.

        Example:
            >>> from datapyrse import ServiceClient
            >>>
            >>> service_client = ServiceClient(tenant_id="...", resource_url="...")
            >>> delete_response = service_client.delete(
            ...     entity_logical_name="account",
            ...     entity_id="..."
            ... )
        """

        if not entity_logical_name:
            msg = "Entity logical name is required"
            logger.error(msg)
            raise ValueError(msg)
        if not entity_id:
            msg = "Entity ID is required"
            logger.error(msg)
            raise ValueError(msg)
        entity: Entity = Entity(entity_logical_name=entity_logical_name)
        if isinstance(entity_id, str):
            try:
                entity_id = UUID(entity_id)
            except ValueError as exc:
                msg = "Entity ID must be a valid UUID"
                logger.error(msg)
                raise ValueError(msg) from exc
        else:
            entity.entity_id = entity_id
        dataverse_request: DataverseRequest = DataverseRequest(
            base_url=self.resource_url,
            org_metadata=self.metadata,
            entity=entity,
            logger=logger,
        )
        request: Request = get_delete_request(
            dataverse_request=dataverse_request,
            logger=logger,
        )
        response: Response = self._execute(request=request)
        delete_response: DeleteResponse = DeleteResponse(
            response=response, logger=logger
        )
        return delete_response

    # def retrieve(
    #     self,
    #     entity_logical_name: str,
    #     entity_id: UUID,
    #     column_set: ColumnSet,
    #     logger: Logger = logging.getLogger(__name__),
    # ) -> Entity:
    #     """
    #     Retrieves an entity from Dataverse by its logical name and ID.

    #     This function sends a GET request to the Dataverse Web API to fetch an entity
    #     based on its logical name and unique identifier (entity_id). It allows selecting
    #     specific columns (fields) to be retrieved via the column_set parameter.

    #     Args:
    #         service_client (ServiceClient): The service client used to authenticate
    #             and send the request.
    #         entity_logical_name (str): The logical name of the entity in Dataverse.
    #         entity_id (uuid.UUID): The unique identifier of the entity to retrieve.
    #         column_set (ColumnSet): A list of attribute names (columns) to be retrieved
    #             from the entity.
    #         logger (logging.Logger, optional): A logger instance for logging debug
    #             and error messages. Defaults to None.

    #     Returns:
    #         Entity: The retrieved entity with its attributes populated.

    #     Raises:
    #         Exception: Raised if the service client is not ready, if the entity logical
    #             name or ID is missing, if the column set transformation fails, or if
    #             the entity cannot be found.
    #     """

    #     logger = self._prepare_request(logger)

    #     if not entity_logical_name:
    #         raise Exception("Entity plural name is required")

    #     if not entity_id:
    #         raise Exception("Entity ID is required")

    #     if not column_set:
    #         raise Exception("Column set is required")

    #     if not self.metadata.entities:
    #         raise Exception("Metadata entities not found")
    #     entity_plural_name: str | None = next(
    #         (
    #             data.logical_collection_name
    #             for data in self.metadata.entities
    #             if data.logical_name == entity_logical_name
    #         ),
    #         None,
    #     )
    #     if not entity_plural_name:
    #         raise Exception("Entity collection name not found")

    #     select: str | None = None
    #     if isinstance(column_set, list):
    #         parsed_column_set: List[str] = transform_column_set(
    #             self, entity_logical_name, column_set
    #         )
    #         if not parsed_column_set:
    #             raise Exception("Failed to transform column set")
    #         select = ",".join(parsed_column_set)

    #     logger.debug("Retrieving entity")
    #     endpoint: str = f"api/data/v9.2/{entity_plural_name}({str(entity_id)})"
    #     headers: dict = self._get_request_headers()
    #     url: str = f"{self.resource_url}/{endpoint}"
    #     if select:
    #         url = f"{url}?$select={select}"

    #     response: Response = requests.get(
    #         url,
    #         headers=headers,
    #     )
    #     response.raise_for_status()
    #     entity: Entity = Entity(
    #         entity_id=entity_id,
    #         entity_logical_name=entity_logical_name,
    #         attributes=response.json(),
    #         logger=logger,
    #     )
    #     return entity

    # def retrieve_multiple(
    #     self,
    #     query: QueryExpression,
    #     logger: Logger = logging.getLogger(__name__),
    # ):
    #     """
    #     Retrieves multiple entities from Dataverse using a query expression.

    #     This function sends a GET request to the Dataverse Web API to retrieve multiple
    #     entities that match the given query expression. It uses the FetchXML generated
    #     from the query to perform the retrieval.

    #     Args:
    #         service_client (ServiceClient): The service client used to authenticate
    #             and send the request.
    #         query (QueryExpression): The query expression that defines the filtering
    #             and selection of entities to retrieve.
    #         logger (logging.Logger, optional): A logger instance for logging debug
    #             and error messages. Defaults to None.

    #     Returns:
    #         EntityCollection: A collection of entities matching the query.

    #     Raises:
    #         Exception: Raised if the service client is not ready, the query is invalid,
    #             or the API request fails.
    #     """

    #     logger = self._prepare_request(logger)

    #     if not query:
    #         raise Exception("Query is required")
    #     else:
    #         if not isinstance(query, QueryExpression):
    #             raise Exception("Query must be a QueryExpression")

    #     entity_logical_name: str = query.entity_name
    #     if not entity_logical_name:
    #         raise ValueError("Entity logical name not found in query")

    #     if not self.metadata.entities:
    #         raise Exception("Metadata entities not found")

    #     entity_plural_name: str | None = next(
    #         (
    #             data.logical_collection_name
    #             for data in self.metadata.entities
    #             if data.logical_name == entity_logical_name
    #         ),
    #         None,
    #     )
    #     if not entity_plural_name:
    #         raise Exception("Entity collection name not found")

    #     logger.debug("Retrieving entities")
    #     endpoint: str = f"api/data/v9.2/{entity_plural_name}"
    #     headers: dict = self._get_request_headers()

    #     fetch_xml: str = query.to_fetchxml()
    #     if fetch_xml:
    #         endpoint += f"?fetchXml={fetch_xml}"
    #     else:
    #         raise Exception("Failed to parse query expression")

    #     url: str = f"{self.resource_url}/{endpoint}"

    #     response: requests.Response
    #     try:
    #         response = requests.get(
    #             url,
    #             headers=headers,
    #         )
    #         response.raise_for_status()
    #     except requests.exceptions.RequestException as e:
    #         print(fetch_xml)
    #         logger.error(f"Failed to retrieve entities: {e}")
    #         raise Exception("Failed to retrieve entities")
    #     if not response.json().get("value"):
    #         return EntityCollection(
    #             entity_logical_name=entity_logical_name, entities=[]
    #         )

    #     entities: EntityCollection = EntityCollection(
    #         entity_logical_name=entity_logical_name
    #     )
    #     logger.debug(f"Entity logical name: {entity_logical_name}")
    #     logger.debug(f"Retrieved {len(response.json().get('value'))} entities")
    #     logger.debug(f"Entities: {response.json().get('value')}")
    #     for entity_data in response.json().get("value"):
    #         entity: Entity = Entity(
    #             entity_logical_name=entity_logical_name,
    #             attributes=entity_data,
    #             logger=logger,
    #         )
    #         entities.add_entity(entity)

    #     return entities

    # def delete_entity(
    #     self,
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

    #     if not logger:
    #         logger = self._prepare_request()
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
    #     if not self.metadata.entities:
    #         logger.error("Metadata entities not found")
    #         raise ValueError("Metadata entities not found")

    #     entity_metadata: EntityMetadata | None = next(
    #         (
    #             entity_meta
    #             for entity_meta in self.metadata.entities
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
    #         f"{self.resource_url}/api/data/v9.2/{entity_plural_name}({entity_id})"
    #     )
    #     headers: dict = self._get_request_headers(**kwargs)
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

    # def _get_request_headers(self, **kwargs) -> dict:
    #     headers = {
    #         "Authorization": f"Bearer {self._get_access_token()}",
    #         "OData-MaxVersion": "4.0",
    #         "OData-Version": "4.0",
    #         "Accept": "application/json",
    #         "Content-Type": "application/json; charset=utf-8",
    #         "Prefer": "odata.include-annotations=*",
    #     }
    #     if kwargs:
    #         if kwargs.get("SuppressDuplicateDetection") is not None:
    #             value: str = str(kwargs["SuppressDuplicateDetection"]).lower()
    #             headers["MSCRM.SuppressDuplicateDetection"] = (
    #                 value if value in ["true", "false"] else "false"
    #             )
    #         if kwargs.get("BypassCustomPluginExecution") is not None:
    #             value: str = str(kwargs["BypassCustomPluginExecution"]).lower()
    #             headers["MSCRM.BypassCustomPluginExecution"] = (
    #                 value if value in ["true", "false"] else "false"
    #             )
    #         if kwargs.get("SuppressCallbackRegistrationExpanderJob") is not None:
    #             value: str = str(
    #                 kwargs["SuppressCallbackRegistrationExpanderJob"]
    #             ).lower()
    #             headers["MSCRM.SuppressCallbackRegistrationExpanderJob"] = (
    #                 value if value in ["true", "false"] else "false"
    #             )
    #     return headers

    # def _prepare_request(self, logger: Logger | None, entity: Entity | None = None):
    #     """
    #     Prepares for making a service call by ensuring the client is ready,
    #     and validating input parameters like entity and logger.
    #     """
    #     if not logger:
    #         logger = self.logger

    #     if not self.is_ready:
    #         logger.error("Service client is not ready")
    #         raise Exception("Service client is not ready")

    #     if not self.metadata.entities:
    #         logger.error("Metadata entities not found")
    #         raise Exception("Metadata entities not found")

    #     if entity:
    #         if not isinstance(entity, Entity):
    #             logger.error("Entity is not of type Entity")
    #             raise Exception("Entity is not of type Entity")
    #         if not entity.entity_logical_name:
    #             logger.error("Entity logical name is required")
    #             raise Exception("Entity logical name is required")
    #         if not entity.entity_id:
    #             logger.error("Entity ID is required")
    #             raise Exception("Entity ID is required")

    #     return logger
