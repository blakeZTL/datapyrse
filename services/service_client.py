import logging
import time
from typing import List
import msal

from models.query_expression import QueryExpression


class ServiceClient:

    def __init__(
        self,
        tenant_id: str,
        resource_url: str,
        client_id: str = None,
        scope=None,
        prompt=None,
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
        self.token = self.acquire_token()

    def __post_init__(self):
        logging.basicConfig(level=logging.DEBUG)
        if self.access_token and self.token_expiry and time.time() > self.token_expiry:
            self.IsReady = True

    def acquire_token(self) -> None:
        self.IsReady = False
        logging.debug("Acquiring token")
        result = None
        logging.debug("Acquiring interactive token")
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
        logging.debug("Getting access token")
        if not self.access_token or (
            self.token_expiry and time.time() > self.token_expiry
        ):
            logging.debug("Acquiring new token")
            self.acquire_token()
        logging.debug("Returning access token")
        self.IsReady = True
        return self.access_token

    def retrieve(self, entity_logical_name: str, entity_id: str, column_set: List[str]):
        from services.retrieve import retrieve as retrieve_method

        return retrieve_method(self, entity_logical_name, entity_id, column_set)

    def retrieve_multiple(self, query: QueryExpression):
        from services.retrieve_multiple import (
            retrieve_multiple as retrieve_multiple_method,
        )

        return retrieve_multiple_method(self, query)
