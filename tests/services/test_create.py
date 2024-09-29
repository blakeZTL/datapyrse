from typing import List
import uuid
import pytest
from unittest import mock
from datapyrse.models.entity import Entity
from datapyrse.models.entity_metadata import (
    AttributeMetadata,
    EntityMetadata,
    OrgMetadata,
)
from datapyrse.services.service_client import ServiceClient
from datapyrse.utils.dataverse import (
    get_entity_collection_name_by_logical_name,
    parse_entity_to_web_api_body,
)
from datapyrse.services.create import CreateRequest


@pytest.fixture
def service_client():
    service_client = mock.Mock(spec=ServiceClient)
    service_client.IsReady = True
    service_client.get_access_token.return_value = "mock_access_token"
    service_client.resource_url = "https://example.crm.dynamics.com"
    service_client.metadata = OrgMetadata(
        entities=[
            EntityMetadata(
                logical_name="account",
                logical_collection_name="accounts",
                attributes=[
                    AttributeMetadata(
                        logical_name="name",
                        attribute_type="string",
                        schema_name="Name",
                    ),
                ],
            ),
            EntityMetadata(
                logical_name="contact",
                logical_collection_name="contacts",
                attributes=[
                    AttributeMetadata(
                        logical_name="firstname",
                        attribute_type="string",
                        schema_name="FirstName",
                    ),
                ],
            ),
        ],
    )
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
def test_create_request_success(
    mock_requests_post,
    service_client,
    entity,
    logger,
):

    guid = uuid.uuid4()
    entity.entity_id = None

    mock_response = mock.Mock()
    mock_response.ok = True
    mock_response.headers = {
        "OData-EntityId": f"https://example.crm.dynamics.com/api/data/v9.2/accounts({guid})"
    }
    mock_response.json.return_value = {
        "accountid": str(guid),
    }
    mock_requests_post.return_value = mock_response

    created_entity = CreateRequest.create(service_client, entity, logger)

    assert created_entity.entity_id == guid

    mock_requests_post.assert_called_once()

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


@mock.patch("requests.post")
@mock.patch("datapyrse.services.create.parse_entity_to_web_api_body")
def test_create_request_http_failure(
    mock_parse_entity_to_web_api_body,
    mock_requests_post,
    service_client,
    entity,
    logger,
):

    # Mocking the parsed entity data
    mock_parse_entity_to_web_api_body.return_value = {"name": "Sample Account"}

    # Mocking a failed POST request
    mock_response = mock.Mock()
    mock_response.ok = False
    mock_response.text = "Bad Request"
    mock_requests_post.return_value = mock_response

    with pytest.raises(Exception, match="Failed to create entity: Bad Request"):
        CreateRequest.create(service_client, entity, logger)
