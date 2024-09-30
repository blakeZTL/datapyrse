from _typeshed import Incomplete
from datapyrse._entity import Entity as Entity
from datapyrse._entity_metadata import OrgMetadata as OrgMetadata
from datapyrse.messages._create import CreateResponse as CreateResponse, get_create_request as get_create_request
from datapyrse.messages._dataverse_request import DataverseRequest as DataverseRequest
from datapyrse.messages._delete import DeleteResponse as DeleteResponse, get_delete_request as get_delete_request
from datapyrse.messages._retrieve import RetrieveResponse as RetrieveResponse, get_retrieve_request as get_retrieve_request
from datapyrse.messages._retrieve_multiple import RetrieveMultipleResponse as RetrieveMultipleResponse, get_retrieve_multiple_request as get_retrieve_multiple_request
from datapyrse.messages._update import UpdateResponse as UpdateResponse, get_update_request as get_update_request
from datapyrse.query._column_set import ColumnSet as ColumnSet
from datapyrse.query._query_expression import QueryExpression as QueryExpression
from datapyrse.utils._dataverse import DEFAULT_HEADERS as DEFAULT_HEADERS
from enum import StrEnum
from logging import Logger
from requests import PreparedRequest as PreparedRequest, Request as Request, Response as Response
from uuid import UUID

class Prompt(StrEnum):
    NONE = 'none'
    SELECT_ACCOUNT = 'select_account'
    CONSENT = 'consent'
    LOGIN = 'login'

class ServiceClient:
    client_id: Incomplete
    tenant_id: Incomplete
    resource_url: Incomplete
    authority_url: Incomplete
    scope: Incomplete
    prompt: Incomplete
    token_expiry: Incomplete
    is_ready: bool
    logger: Incomplete
    def __init__(self, tenant_id: str, resource_url: str, client_id: str = '51f81489-12ee-4a9e-aaae-a2591f45987d', scope: list[str] | None = None, prompt: Prompt = ..., logger: Logger = ...) -> None: ...
    metadata: Incomplete
    def __post_init__(self) -> None: ...
    def create(self, entity: Entity, logger: Logger | None = None, suppress_duplicate_detection: bool = False, bypass_custom_plugin_execution: bool = False, suppress_power_automate_triggers: bool = False, tag: str | None = None) -> CreateResponse: ...
    def retrieve(self, entity_logical_name: str, entity_id: UUID | str, column_set: ColumnSet, logger: Logger | None = None) -> RetrieveResponse: ...
    def retrieve_multiple(self, query: QueryExpression, logger: Logger | None = None) -> RetrieveMultipleResponse: ...
    def update(self, entity: Entity, logger: Logger = ..., tag: str | None = None, suppress_duplicate_detection: bool = False, bypass_custom_plugin_execution: bool = False, suppress_power_automate_triggers: bool = False) -> UpdateResponse: ...
    def delete(self, entity_logical_name: str, entity_id: UUID | str, logger: Logger = ...) -> DeleteResponse: ...
