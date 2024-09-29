"""
A module for sending requests to Dataverse
"""

from dataclasses import dataclass, field
from logging import Logger, getLogger
from typing import Optional

from datapyrse.models.entity import Entity
from datapyrse.models.entity_metadata import OrgMetadata
from datapyrse.utils.dataverse import (
    get_entity_collection_name_by_logical_name,
    DEFAULT_HEADERS,
)


@dataclass
class DataverseRequest:
    """
    Prepare a request for Dataverse

    Args:
        base_url (str): Base URL of the Dataverse instance
        org_metadata (OrgMetadata): Organization Metadata
        entity (Entity): Entity object
        tag (str): Optional tag for the request
        suppress_duplicate_detection (bool): Suppress Duplicate Detection
        bypass_custom_plugin_execution (bool): Bypass Custom Plugin Execution
        suppress_callback_registration_expander_job (bool): Suppress Callback Registration Expander Job
        logger (Logger): Logger object for logging
    """

    base_url: str
    org_metadata: OrgMetadata
    entity: Entity
    tag: Optional[str] = None
    suppress_duplicate_detection: bool = False
    bypass_custom_plugin_execution: bool = False
    suppress_callback_registration_expander_job: bool = False
    logger: Logger = field(default_factory=lambda: getLogger(__name__))

    def __post_init__(self):
        if not self.base_url:
            msg = "Base URL of type str required to parse request"
            self.logger.error(msg)
            raise ValueError(msg)
        self.base_url = (
            self.base_url if not self.base_url.endswith("/") else self.base_url[:-1]
        )

        if not self.org_metadata:
            msg = "Organization Metadata of type OrgMetadata required to parse request"
            self.logger.error(msg)
            raise ValueError(msg)

        if not self.entity:
            msg = "Entity of type Entity or str required to parse request"
            self.logger.error(msg)
            raise ValueError(msg)
        if not self.entity.entity_logical_name:
            msg = "Logical Name required for the entity of the request"
            self.logger.error(msg)
            raise ValueError(msg)
        self.endpoint: str = self._prepare_endpoint()
        self.headers: dict[str, str] = self._prepare_headers()

    def _prepare_endpoint(self) -> str:
        logical_collection_name: Optional[str] = (
            get_entity_collection_name_by_logical_name(
                org_metadata=self.org_metadata,
                logical_name=self.entity.entity_logical_name,
                logger=self.logger,
            )
        )
        if not logical_collection_name:
            msg = f"Collection Name not found in metadata for {self.entity.entity_logical_name}."
            self.logger.error(msg)
            raise ValueError(msg)
        endpoint: str = f"{self.base_url}/api/data/v9.2/{logical_collection_name}"
        if self.entity.entity_id:
            endpoint += f"({self.entity.entity_id})"
        if self.tag:
            endpoint += f"?tag={self.tag}"
        return endpoint

    def _prepare_headers(self) -> dict[str, str]:
        headers: dict[str, str] = DEFAULT_HEADERS
        if self.suppress_duplicate_detection:
            headers["MSCRM.SuppressDuplicateDetection"] = "true"

        if self.bypass_custom_plugin_execution:
            headers["MSCRM.BypassCustomPluginExecution"] = "true"

        if self.suppress_callback_registration_expander_job:
            headers["MSCRM.SuppressCallBackRegistrationExpanderJob"] = "true"

        return headers
