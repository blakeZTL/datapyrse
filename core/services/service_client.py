import logging
import time
from typing import List
import uuid
import msal
from core.models.query_expression import QueryExpression


class ServiceClient:

    def __init__(
        self,
        tenant_id: str,
        resource_url: str,
        client_id: str = None,
        scope=None,
        prompt=None,
        logger: logging.Logger = None,
    ) -> None:
        self.client_id = client_id or "51f81489-12ee-4a9e-aaae-a2591f45987d"
        self.tenant_id = tenant_id
        self.resource_url = resource_url
        self.authority_url = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = scope or [f"{resource_url}/.default"]
        self.prompt = prompt
        self.msal_app = msal.PublicClientApplication(
            client_id=self.client_id, authority=self.authority_url
        )
        self.access_token = None
        self.token_expiry = None
        self.IsReady = False
        self.logger = logger
        self.token = self.acquire_token()

    def __post_init__(self):
        if not self.logger:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.WARNING)
        if self.access_token and self.token_expiry and time.time() > self.token_expiry:
            self.IsReady = True

    def acquire_token(self) -> None:
        self.IsReady = False
        self.logger.debug("Acquiring token")
        result = None
        self.logger.debug("Acquiring interactive token")
        result = self.msal_app.acquire_token_interactive(
            scopes=self.scope, prompt=self.prompt
        )
        if "access_token" in result:
            self.token = result
            self.access_token = self.token["access_token"]
            self.token_expiry = time.time() + self.token["expires_in"]
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
            self.acquire_token()
        self.logger.debug("Returning access token")
        self.IsReady = True
        return self.access_token

    def retrieve(
        self,
        entity_logical_name: str,
        entity_id: uuid.UUID,
        column_set: List[str],
        logger: logging.Logger = None,
    ):
        from core.services.retrieve import retrieve as retrieve_method

        if not logger:
            logger = self.logger

        return retrieve_method(
            self, entity_logical_name, entity_id, column_set, logger=logger
        )

    def retrieve_multiple(self, query: QueryExpression, logger: logging.Logger = None):
        from core.services.retrieve_multiple import (
            retrieve_multiple as retrieve_multiple_method,
        )

        if not logger:
            logger = self.logger

        return retrieve_multiple_method(service_client=self, query=query, logger=logger)