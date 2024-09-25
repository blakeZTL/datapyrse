import uuid
import pytest
from unittest import mock
from datapyrse.core.models.entity import Entity
from datapyrse.core.services.service_client import ServiceClient
from datapyrse.core.utils.dataverse import (
    get_entity_collection_name_by_logical_name,
    parse_entity_to_web_api_body,
)
from datapyrse.core.services.create import CreateRequest


@pytest.fixture
def service_client():
    service_client = mock.Mock(spec=ServiceClient)
    service_client.IsReady = True
    service_client.get_access_token.return_value = "mock_access_token"
    service_client.resource_url = "https://example.crm.dynamics.com"
    return service_client


@pytest.fixture
def entity():
    entity = mock.Mock(spec=Entity)
    entity.logical_name = "account"
    entity.entity_id = "12345"
    entity.entity_logical_name = "account"
    entity.attributes = {"name": "Sample Account"}
    return entity


@pytest.fixture
def logger():
    return mock.Mock()


@mock.patch("requests.post")
@mock.patch("datapyrse.core.services.create.get_entity_collection_name_by_logical_name")
@mock.patch("datapyrse.core.services.create.parse_entity_to_web_api_body")
def test_create_request_success(
    mock_parse_entity_to_web_api_body,
    mock_get_entity_collection_name_by_logical_name,
    mock_requests_post,
    service_client,
    entity,
    logger,
):
    # Mocking successful entity collection name retrieval
    mock_get_entity_collection_name_by_logical_name.return_value = "accounts"

    # Mocking the parsed entity data
    mock_parse_entity_to_web_api_body.return_value = {"name": "Sample Account"}

    guid = uuid.uuid4()
    entity.entity_id = None

    # Mocking the successful POST request
    mock_response = mock.Mock()
    mock_response.ok = True
    mock_response.headers = {
        "OData-EntityId": f"https://example.crm.dynamics.com/api/data/v9.2/accounts({guid})"
    }
    mock_response.json.return_value = {
        "accountid": str(guid),
    }
    mock_requests_post.return_value = mock_response

    # Calling the create method
    created_entity = CreateRequest.create(service_client, entity, logger)

    # Assertions for success
    assert created_entity.entity_id == guid
    mock_get_entity_collection_name_by_logical_name.assert_called_once_with(
        service_client, "account"
    )
    mock_parse_entity_to_web_api_body.assert_called_once_with(
        entity, service_client, logger
    )
    mock_requests_post.assert_called_once()

    # Check if the correct API endpoint and headers were used
    expected_endpoint = "api/data/v9.2/accounts"
    mock_requests_post.assert_called_once_with(
        f"https://example.crm.dynamics.com/{expected_endpoint}",
        headers={
            "Authorization": "Bearer mock_access_token",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Prefer": "odata.include-annotations=*",
        },
        json={"name": "Sample Account"},
    )


def test_create_request_service_client_not_ready(service_client, entity):
    # Simulate service client not being ready
    service_client.IsReady = False

    with pytest.raises(Exception, match="Service client is not ready"):
        CreateRequest.create(service_client, entity)


def test_create_request_entity_not_provided(service_client, logger):
    # Pass None for entity
    with pytest.raises(Exception, match="Entity is required"):
        CreateRequest.create(service_client, None, logger)


def test_create_request_invalid_entity(service_client, logger):
    # Pass an invalid object that is not of type Entity
    with pytest.raises(Exception, match="Entity is not of type Entity"):
        CreateRequest.create(service_client, "invalid_entity", logger)


def test_create_request_missing_logical_name(service_client, entity, logger):
    # Simulate missing logical name
    entity.entity_logical_name = None

    with pytest.raises(Exception, match="Entity logical name is required"):
        CreateRequest.create(service_client, entity, logger)


@mock.patch("datapyrse.core.services.create.get_entity_collection_name_by_logical_name")
def test_create_request_entity_plural_name_not_found(
    mock_get_entity_collection_name_by_logical_name, service_client, entity, logger
):
    # Simulate failure to find entity plural name
    mock_get_entity_collection_name_by_logical_name.return_value = None

    with pytest.raises(Exception, match="Entity collection name not found"):
        CreateRequest.create(service_client, entity, logger)


@mock.patch("requests.post")
@mock.patch("datapyrse.core.services.create.get_entity_collection_name_by_logical_name")
@mock.patch("datapyrse.core.services.create.parse_entity_to_web_api_body")
def test_create_request_http_failure(
    mock_parse_entity_to_web_api_body,
    mock_get_entity_collection_name_by_logical_name,
    mock_requests_post,
    service_client,
    entity,
    logger,
):
    # Mocking successful entity collection name retrieval
    mock_get_entity_collection_name_by_logical_name.return_value = "accounts"

    # Mocking the parsed entity data
    mock_parse_entity_to_web_api_body.return_value = {"name": "Sample Account"}

    # Mocking a failed POST request
    mock_response = mock.Mock()
    mock_response.ok = False
    mock_response.text = "Bad Request"
    mock_requests_post.return_value = mock_response

    with pytest.raises(Exception, match="Failed to create entity: Bad Request"):
        CreateRequest.create(service_client, entity, logger)
