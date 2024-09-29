from logging import Logger
import uuid
import pytest
from unittest.mock import Mock, patch
from uuid import UUID
from datapyrse.models.entity import Entity
from datapyrse.models.entity_reference import EntityReference
from requests import HTTPError
from datapyrse.services.service_client import ServiceClient
from datapyrse.services.delete import (
    delete_entity,
)
from datapyrse.models.entity_metadata import *


@pytest.fixture
def mock_service_client():
    service_client = Mock(spec=ServiceClient)
    service_client.IsReady = True
    service_client.resource_url = "https://example.com"
    service_client.get_access_token.return_value = "mock_token"
    service_client.metadata = OrgMetadata(
        entities=[
            EntityMetadata(logical_name="account", logical_collection_name="accounts"),
            EntityMetadata(logical_name="contact", logical_collection_name="contacts"),
        ]
    )
    return service_client


@pytest.fixture
def mock_logger():
    return Mock(spec=Logger)


@patch("requests.delete")
def test_delete_entity_success(mock_delete, mock_service_client, mock_logger):
    # Set up
    entity_id = str(UUID("12345678-1234-1234-1234-123456789abc"))
    entity_name = "account"

    # Mock the requests.delete response
    mock_response = Mock()
    mock_response.ok = True
    mock_delete.return_value = mock_response

    # Test with entity_name and entity_id directly
    result = delete_entity(
        service_client=mock_service_client,
        logger=mock_logger,
        entity_name=entity_name,
        entity_id=entity_id,
    )

    # Assertions
    assert result is True
    mock_delete.assert_called_once_with(
        f"https://example.com/api/data/v9.2/accounts({entity_id})",
        headers={
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Prefer": "return=representation;odata.metadata=none",
            "Authorization": "Bearer mock_token",
        },
    )
    mock_logger.info.assert_called_once_with(
        f"Entity {entity_name} with id {entity_id} deleted"
    )


@patch("requests.delete")
def test_delete_entity_entity_object(mock_delete, mock_service_client, mock_logger):
    # Create an Entity object
    entity = Mock(spec=Entity)
    entity.entity_id = uuid.uuid4()
    entity.entity_logical_name = "contact"

    # Mock the requests.delete response
    mock_response = Mock()
    mock_response.ok = True
    mock_delete.return_value = mock_response

    # Test with an entity object
    result = delete_entity(
        service_client=mock_service_client, logger=mock_logger, entity=entity
    )

    # Assertions
    assert result is True
    mock_delete.assert_called_once()
    mock_logger.info.assert_called_once()


@patch("requests.delete")
def test_delete_entity_fail(mock_delete, mock_service_client, mock_logger):
    # Create an EntityReference object
    entity_reference = Mock(spec=EntityReference)
    entity_reference.entity_id = "12345678-1234-1234-1234-123456789abc"
    entity_reference.entity_logical_name = "account"

    # Mock a failed delete response
    mock_response = Mock()
    mock_response.ok = False
    mock_delete.return_value = mock_response

    # Test with an entity reference object
    result = delete_entity(
        service_client=mock_service_client,
        logger=mock_logger,
        entity_reference=entity_reference,
    )

    # Assertions
    assert result is False
    mock_delete.assert_called_once()
    mock_logger.error.assert_called_once()


@patch("requests.delete")
def test_delete_entity_http_error(mock_delete, mock_service_client):
    # Create an Entity object
    entity = Mock(spec=Entity)
    entity.entity_id = uuid.uuid4()
    entity.entity_logical_name = "contact"

    # Mock a request that raises an HTTPError
    mock_delete.side_effect = HTTPError("Failed to delete")

    # Test with an entity object
    with pytest.raises(HTTPError):
        delete_entity(service_client=mock_service_client, entity=entity)

    mock_delete.assert_called_once()


def test_delete_entity_service_client_not_ready(mock_logger):
    # Service client not ready
    mock_service_client = Mock(spec=ServiceClient)
    mock_service_client.IsReady = False

    with pytest.raises(ValueError, match="ServiceClient is not ready"):
        delete_entity(service_client=mock_service_client, logger=mock_logger)

    mock_logger.error.assert_called_once_with("ServiceClient is not ready")


def test_delete_entity_missing_arguments(mock_service_client, mock_logger):
    with pytest.raises(ValueError, match="At least one argument is required"):
        delete_entity(service_client=mock_service_client, logger=mock_logger)

    mock_logger.error.assert_called_once_with("At least one argument is required")


def test_delete_entity_entity_id_required(mock_service_client, mock_logger):
    with pytest.raises(ValueError, match="entity_id is required"):
        delete_entity(
            service_client=mock_service_client, logger=mock_logger, entity=Entity()
        )

    mock_logger.error.assert_called_once_with("entity_id is required")


def test_delete_entity_entity_name_required(mock_service_client, mock_logger):
    with pytest.raises(ValueError, match="entity_name is required"):
        delete_entity(
            service_client=mock_service_client,
            logger=mock_logger,
            entity=Entity(entity_id=uuid.uuid4()),
        )

    mock_logger.error.assert_called_once_with("entity_name is required")


def test_delete_entity_entity_reference_required(mock_service_client, mock_logger):
    with pytest.raises(
        ValueError, match="entity_reference must be of type EntityReference"
    ):
        delete_entity(
            service_client=mock_service_client,
            logger=mock_logger,
            entity_reference="notAnEntityReference",
        )

    mock_logger.error.assert_called_once_with(
        "entity_reference must be of type EntityReference"
    )


def test_delete_entity_entity_id_type(mock_service_client, mock_logger):
    with pytest.raises(ValueError, match="entity_id must be of type UUID or str"):
        delete_entity(
            service_client=mock_service_client,
            logger=mock_logger,
            entity_name="account",
            entity_id=123,
        )


def test_delete_entity_entity_name_type(mock_service_client, mock_logger):
    with pytest.raises(ValueError, match="entity_name must be of type str"):
        delete_entity(
            service_client=mock_service_client,
            logger=mock_logger,
            entity_name=123,
            entity_id=uuid.uuid4(),
        )


def test_delete_entity_entity_not_entity(mock_service_client, mock_logger):
    with pytest.raises(ValueError, match="entity must be of type Entity"):
        delete_entity(
            service_client=mock_service_client, logger=mock_logger, entity="account"
        )


def test_delete_entity_entity_reference_not_entity_reference(
    mock_service_client, mock_logger
):
    with pytest.raises(
        ValueError, match="entity_reference must be of type EntityReference"
    ):
        delete_entity(
            service_client=mock_service_client,
            logger=mock_logger,
            entity_reference="account",
        )


def test_delete_entity_entity_id_required(mock_service_client, mock_logger):
    with pytest.raises(ValueError, match="entity_id is required"):
        delete_entity(
            service_client=mock_service_client,
            logger=mock_logger,
            entity_name="account",
        )


def test_delete_entity_entity_name_required(mock_service_client, mock_logger):
    with pytest.raises(ValueError, match="entity_name is required"):
        delete_entity(
            service_client=mock_service_client,
            logger=mock_logger,
            entity_id=uuid.uuid4(),
        )


def test_delete_entity_entity_name_not_str(mock_service_client, mock_logger):
    with pytest.raises(ValueError, match="entity_name must be of type str"):
        delete_entity(
            service_client=mock_service_client,
            logger=mock_logger,
            entity_name=123,
            entity_id="12345678-1234-1234-1234-123456789abc",
        )


def test_delete_entity_entity_metadata_not_found(mock_service_client, mock_logger):
    mock_service_client.metadata = OrgMetadata(
        entities=[
            EntityMetadata(logical_name="contact", logical_collection_name="contacts"),
        ]
    )

    with pytest.raises(ValueError, match=f"Entity account not found in metadata"):
        delete_entity(
            service_client=mock_service_client,
            logger=mock_logger,
            entity_name="account",
            entity_id="12345678-1234-1234-1234-123456789abc",
        )


def test_delete_entity_entity_plural_name_not_found(mock_service_client, mock_logger):
    mock_service_client.metadata = OrgMetadata(
        entities=[
            EntityMetadata(logical_name="account"),
        ]
    )

    with pytest.raises(ValueError, match=f"Entity account does not have a plural name"):
        delete_entity(
            service_client=mock_service_client,
            logger=mock_logger,
            entity_name="account",
            entity_id="12345678-1234-1234-1234-123456789abc",
        )
