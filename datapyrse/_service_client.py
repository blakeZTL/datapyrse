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


from datapyrse.messages._associate import get_associate_request
from datapyrse.messages._disassociate import get_disassociate_request
from datapyrse.query._column_set import ColumnSet
from datapyrse._entity_metadata import OrgMetadata
from datapyrse.query._query_expression import QueryExpression
from datapyrse.messages._create import CreateResponse, get_create_request
from datapyrse._entity import Entity
from datapyrse.messages._dataverse_request import DataverseRequest
from datapyrse.messages._delete import DeleteResponse, get_delete_request
from datapyrse.messages._retrieve import RetrieveResponse, get_retrieve_request
from datapyrse.messages._retrieve_multiple import (
    RetrieveMultipleResponse,
    get_retrieve_multiple_request,
)
from datapyrse.messages._update import UpdateResponse, get_update_request
from datapyrse.utils._dataverse import DEFAULT_HEADERS

from datapyrse._entity_reference import EntityReference

from datapyrse._entity_reference_collection import EntityReferenceCollection

from datapyrse.messages._relate import RelateRequest


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
        pre_fetch_relationship_metadata: bool = False,
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
        self.fetch_relationship_metadata = pre_fetch_relationship_metadata
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
        self.metadata = self._get_metadata(
            get_relationships=self.fetch_relationship_metadata
        )
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

    def _get_metadata(self, get_relationships: bool = False) -> OrgMetadata:
        self.logger.debug("Getting metadata")

        endpoint: str = (
            "api/data/v9.2/EntityDefinitions?"
            + "$expand="
            + "Attributes($select="
            + "LogicalName,AttributeType,SchemaName)"
        )
        if get_relationships:
            self.fetch_relationship_metadata = True
            endpoint += (
                ",OneToManyRelationships,ManyToOneRelationships,ManyToManyRelationships"
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
        org_metadata.contains_relationships = get_relationships
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

    def refresh_metadata(self) -> OrgMetadata:
        """
        Refreshes the metadata for the organization.

        This function allows refreshing the metadata for the organization by fetching
        the entity definitions from Dataverse. It sends a GET request to the Dataverse
        Web API to retrieve the metadata and updates the metadata attribute.

        Returns:
            OrgMetadata: The updated organization metadata.
        """
        self.logger.debug("Refreshing metadata")
        if not self.fetch_relationship_metadata:
            self.logger.warning(
                "Relationship metadata not fetched. Fetching metadata to associate records"
            )
            self.metadata = self._get_metadata(get_relationships=True)
            return self.metadata
        self.metadata = self._get_metadata()
        return self.metadata

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
        logger: Optional[Logger] = None,
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
        if not logger:
            logger = self.logger

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
        self, query: QueryExpression, logger: Optional[Logger] = None
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
        if not logger:
            logger = self.logger

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

    def update(
        self,
        entity: Entity,
        logger: Logger = logging.getLogger(__name__),
        tag: Optional[str] = None,
        suppress_duplicate_detection: bool = False,
        bypass_custom_plugin_execution: bool = False,
        suppress_power_automate_triggers: bool = False,
    ) -> UpdateResponse:
        """
        Updates an entity in Dataverse using the Web API.

        This function allows updating an entity in Dataverse based on the provided entity
        information. It sends a POST request to the Dataverse Web API to update the entity
        and returns the response.

        Args:
            entity (Entity): The entity instance to update.
            logger (Logger, optional): A logger instance for logging debug, info,

        Returns:
            UpdateResponse: The response from the update request.

        Raises:
            ValueError: If entity is not provided.

        Example:
            >>> from datapyrse import Entity, ServiceClient
            >>>
            >>> entity = Entity(entity_logical_name="account",entity_id=UUID('UUID') attributes={"name": "Test Account"})
            >>> service_client = ServiceClient(tenant_id="...", resource_url="...")
            >>> update_response = service_client.update(entity=entity)
        """

        if not entity:
            msg = "Entity is required"
            logger.error(msg)
            raise ValueError(msg)

        if not entity.entity_id or not entity.entity_logical_name:
            msg = "Entity ID and logical name are required"
            logger.error(msg)
            raise ValueError(msg)

        dataverse_request: DataverseRequest = DataverseRequest(
            base_url=self.resource_url,
            org_metadata=self.metadata,
            entity=entity,
            logger=logger,
            tag=tag,
            suppress_duplicate_detection=suppress_duplicate_detection,
            bypass_custom_plugin_execution=bypass_custom_plugin_execution,
            suppress_callback_registration_expander_job=suppress_power_automate_triggers,
        )

        request: Request = get_update_request(
            dataverse_request=dataverse_request,
            logger=logger,
        )

        response: Response = self._execute(request=request)
        update_response: UpdateResponse = UpdateResponse(
            response=response, entity=entity, logger=logger
        )

        return update_response

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

    def _parse_relate(
        self,
        target: EntityReference,
        related_entities: EntityReferenceCollection,
        relationship_name: Optional[str] = None,
        logger: Optional[Logger] = None,
    ) -> RelateRequest:
        if not logger:
            logger = self.logger
        if not target:
            msg = "Target entity is required"
            logger.error(msg)
            raise ValueError(msg)
        if not target.entity_logical_name:
            msg = "Target entity logical name is required"
            logger.error(msg)
            raise ValueError(msg)
        if not target.entity_id:
            msg = "Target entity ID is required"
            logger.error(msg)
            raise ValueError(msg)
        if not related_entities:
            msg = "Related entities are required"
            logger.error(msg)
            raise ValueError(msg)
        if not self.metadata.contains_relationships:
            logger.warning(
                "Relationship metadata not fetched. Fetching metadata to associate records"
            )
            new_metadata: OrgMetadata = self._get_metadata(get_relationships=True)
            self.metadata = new_metadata
        relate_request: RelateRequest = RelateRequest(
            primary_record=target,
            related_records=related_entities,
            org_metadata=self.metadata,
            relationship_name=relationship_name,
            logger=logger,
        )
        if not relate_request.relationship_name:
            relate_request.relationship_name, relate_request.relationship_type = (
                relate_request.parse_relationship_name()
            )
            if not relate_request.relationship_name:
                raise ValueError(
                    "Could not determine relationship name, one must be provided"
                )
            if not relate_request.relationship_type:
                raise ValueError(
                    "Could not determine relationship type, one must be provided"
                )
        realtionship = relate_request.validate_relationship_name(logger=logger)
        if not realtionship:
            raise ValueError(
                "Relationship name not found in metadata, please provide a valid relationship name"
            )
        relate_request.relationship_type = realtionship
        return relate_request

    def associate(
        self,
        target: EntityReference,
        related_entities: EntityReferenceCollection,
        relationship_name: Optional[str] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        """
        Associates a target entity with related entities in Dataverse.

        This function allows associating a target entity with related entities in Dataverse
        based on the provided entity references. It sends a POST request to the Dataverse
        Web API to associate the records and returns the response.

        Args:
            target (EntityReference): The target entity reference to associate with related
                entities.
            related_entities (EntityReferenceCollection): The collection of related entity
                references to associate with the target entity.
            relationship_name (str, optional): The name of the relationship between the target
                and related entities. If not provided, the function will attempt to determine
                the relationship name from the metadata. Defaults to None.
            logger (logging.Logger, optional): A logger instance for logging debug, info,
                and error messages. Defaults to None.

        Returns:
            None: The function does not return any value.

        Raises:
            ValueError: If the target entity, entity logical name, or entity ID is missing,
                if the related entities are not provided, or if the relationship name is not
                found in the metadata.

        Example:
            >>> from datapyrse import EntityReference, EntityReferenceCollection, ServiceClient
            >>>
            >>> target = EntityReference(entity_logical_name="account", entity_id="...")
            >>> related_entities = EntityReferenceCollection(
            ...     entity_logical_name="contact",
            ...     entity_references=[
            ...         EntityReference(entity_logical_name="contact", entity_id="..."),
            ...         EntityReference(entity_logical_name="contact", entity_id="..."),
            ...     ],
            ... )
            >>> service_client = ServiceClient(tenant_id="...", resource_url="...")
            >>> service_client.associate(target=target, related_entities=related_entities)
        """
        if not logger:
            logger = self.logger
        associate_request: RelateRequest = self._parse_relate(
            target=target,
            related_entities=related_entities,
            relationship_name=relationship_name,
            logger=logger,
        )
        dataverse_request: DataverseRequest = DataverseRequest(
            base_url=self.resource_url,
            org_metadata=self.metadata,
            entity=Entity(
                entity_logical_name=associate_request.primary_record.entity_logical_name,
                entity_id=associate_request.primary_record.entity_id,
            ),
            logger=logger,
        )
        request: Request = get_associate_request(
            dataverse_request=dataverse_request,
            associate_request=associate_request,
            logger=logger,
        )
        response: Response = self._execute(request=request)
        if response.status_code != 204:
            msg = f"Failed to associate records: {response.text}"
            logger.error(msg)
            raise ValueError(msg)
        logger.info("Records associated successfully")

    def disassociate(
        self,
        target: EntityReference,
        related_entities: EntityReferenceCollection,
        relationship_name: Optional[str] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        """
        Disassociates a target entity from related entities in Dataverse.

        This function allows disassociating a target entity from related entities in Dataverse
        based on the provided entity references. It sends a DELETE request to the Dataverse
        Web API to disassociate the records and returns the response.

        Args:
            target (EntityReference): The target entity reference to disassociate from related
                entities.
            related_entities (EntityReferenceCollection): The collection of related entity
                references to disassociate from the target entity.
            relationship_name (str, optional): The name of the relationship between the target
                and related entities. If not provided, the function will attempt to determine
                the relationship name from the metadata. Defaults to None.
            logger (logging.Logger, optional): A logger instance for logging debug, info,
                and error messages. Defaults to None.

        Returns:
            None: The function does not return any value.

        Raises:
            ValueError: If the target entity, entity logical name, or entity ID is missing,
                if the related entities are not provided, or if the relationship name is not
                found in the metadata.
        """

        if not logger:
            logger = self.logger
        disassociate_request: RelateRequest = self._parse_relate(
            target=target,
            related_entities=related_entities,
            relationship_name=relationship_name,
            logger=logger,
        )
        dataverse_request: DataverseRequest = DataverseRequest(
            base_url=self.resource_url,
            org_metadata=self.metadata,
            entity=Entity(
                entity_logical_name=disassociate_request.primary_record.entity_logical_name,
                entity_id=disassociate_request.primary_record.entity_id,
            ),
            logger=logger,
        )
        disassociate_requests: list[Request] = get_disassociate_request(
            dataverse_request=dataverse_request,
            disassociate_request=disassociate_request,
            logger=logger,
        )
        for req in disassociate_requests:
            response: Response = self._execute(request=req)
            if response.status_code != 204:
                msg = f"Failed to disassociate records: {response.text}"
                logger.error(msg)
                raise ValueError(msg)
        logger.info("Records disassociated successfully")
