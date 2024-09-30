"""
A module for interacting with Dataverse using the Web API
"""

# pylint: disable=unused-import, missing-class-docstring, unused-argument, missing-function-docstring, too-many-arguments
# pyright: reportUnusedImport=false

from enum import StrEnum
from logging import Logger
from typing import Any, List, Optional, Union
from uuid import UUID

from msal import PublicClientApplication  # type: ignore
from requests import PreparedRequest, Session
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
from datapyrse.services.update import UpdateResponse, get_update_request
from datapyrse.utils.dataverse import DEFAULT_HEADERS

class Prompt(StrEnum):
    NONE: str
    SELECT_ACCOUNT: str
    CONSENT: str
    LOGIN: str

class ServiceClient:
    client_id: str
    tenant_id: str
    resource_url: str
    authority_url: str
    scope: List[str]
    prompt: Prompt
    token_expiry: Optional[float]
    is_ready: bool
    logger: Logger

    def __init__(
        self,
        tenant_id: str,
        resource_url: str,
        client_id: str = ...,
        scope: Optional[List[str]] = ...,
        prompt: Prompt = ...,
        logger: Logger = ...,
    ) -> None: ...
    def __post_init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def _get_metadata(self) -> OrgMetadata: ...
    def _acquire_token(self) -> None: ...
    def _execute(self, request: Request) -> Response: ...
    def _get_access_token(self) -> str: ...
    def create(
        self,
        entity: Entity,
        logger: Optional[Logger] = ...,
        suppress_duplicate_detection: bool = ...,
        bypass_custom_plugin_execution: bool = ...,
        suppress_power_automate_triggers: bool = ...,
        tag: Optional[str] = ...,
    ) -> CreateResponse: ...
    def retrieve(
        self,
        entity_logical_name: str,
        entity_id: Union[UUID, str],
        column_set: ColumnSet,
        logger: Logger = ...,
    ) -> RetrieveResponse: ...
    def retrieve_multiple(
        self, query: QueryExpression, logger: Logger = ...
    ) -> RetrieveMultipleResponse: ...
    def update(
        self,
        entity: Entity,
        logger: Logger = ...,
        tag: Optional[str] = ...,
        suppress_duplicate_detection: bool = ...,
        bypass_custom_plugin_execution: bool = ...,
        suppress_power_automate_triggers: bool = ...,
    ) -> UpdateResponse: ...
    def delete(
        self,
        entity_logical_name: str,
        entity_id: Union[UUID, str],
        logger: Logger = ...,
    ) -> DeleteResponse: ...
