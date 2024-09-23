from unittest import mock
import uuid
import pytest
from models.entity import Entity
from models.entity_collection import EntityCollection
from services.retrieve_multiple import retrieve_multiple


@pytest.fixture
def service_client():
    service_client = mock.Mock()
    service_client.IsReady = True
    service_client.get_access_token.return_value = "mock_access_token"
    service_client.resource_url = "https://example.crm.dynamics.com"
    return service_client


def test_retrieve_multiple_service_client_not_ready():
    service_client = mock.Mock()
    service_client.IsReady = False

    with pytest.raises(Exception, match="Service client is not ready"):
        retrieve_multiple(service_client, "account", ["name"])


def test_retrieve_multiple_entity_name_missing(service_client):
    with pytest.raises(Exception, match="Entity logical name is required"):
        retrieve_multiple(service_client, "", ["name"])


def test_retrieve_multiple_column_set_missing(service_client):
    with pytest.raises(Exception, match="Column set is required"):
        retrieve_multiple(service_client, "account", [])


@mock.patch("services.retrieve_multiple.get_entity_collection_name_by_logical_name")
def test_retrieve_multiple_entity_plural_name_null(
    mock_get_entity_collection_name_by_logical_name,
    service_client,
):
    mock_get_entity_collection_name_by_logical_name.return_value = None

    with pytest.raises(Exception, match="Entity collection name not found"):
        retrieve_multiple(service_client, "account", ["name"])


@mock.patch("services.retrieve_multiple.get_entity_collection_name_by_logical_name")
@mock.patch("services.retrieve_multiple.transform_column_set")
def test_retrieve_multiple_transform_column_set_failure(
    mock_get_entity_collection_name_by_logical_name,
    mock_transform_column_set,
    service_client,
):
    mock_get_entity_collection_name_by_logical_name.return_value = "accounts"
    mock_transform_column_set.side_effect = Exception("Failed to transform column set")

    with pytest.raises(Exception, match="Failed to transform column set"):
        retrieve_multiple(service_client, "account", ["name"])


@mock.patch("services.retrieve_multiple.get_entity_collection_name_by_logical_name")
@mock.patch("services.retrieve_multiple.transform_column_set")
def test_retrieve_multiple_no_results(
    mock_get_entity_collection_name_by_logical_name,
    mock_transform_column_set,
    service_client,
):
    mock_get_entity_collection_name_by_logical_name.return_value = "accounts"
    mock_transform_column_set.return_value = ["name"]

    service_client.get_access_token.return_value = "mock_access_token"
    service_client.resource_url = "https://example.crm.dynamics.com"
    response = mock.Mock()
    response.json.return_value = {"value": []}

    with mock.patch("services.retrieve_multiple.requests.get") as mock_get:
        mock_get.return_value = response
        result = retrieve_multiple(service_client, "account", ["name"])
        assert result.to_dict() == {"entities": [], "logical_name": "account"}
        assert result == EntityCollection(entity_logical_name="account", entities=[])


@mock.patch("services.retrieve_multiple.get_entity_collection_name_by_logical_name")
@mock.patch("services.retrieve_multiple.transform_column_set")
def test_retrieve_multiple_success(
    mock_get_entity_collection_name_by_logical_name,
    mock_transform_column_set,
    service_client,
):
    mock_get_entity_collection_name_by_logical_name.return_value = "accounts"
    mock_transform_column_set.return_value = ["name"]

    account_id_1 = uuid.uuid4()
    account_id_2 = uuid.uuid4()

    service_client.get_access_token.return_value = "mock_access_token"
    service_client.resource_url = "https://example.crm.dynamics.com"
    response = mock.Mock()
    response.json.return_value = {
        "value": [
            {"accountid": str(account_id_1), "name": "Test Account 1"},
            {"accountid": str(account_id_2), "name": "Test Account 2"},
        ]
    }

    with mock.patch("services.retrieve_multiple.requests.get") as mock_get:
        mock_get.return_value = response
        result = retrieve_multiple(service_client, "account", ["name"])
        assert result.to_dict() == {
            "entities": [
                {
                    "id": str(account_id_1),
                    "logical_name": "account",
                    "accountid": str(account_id_1),
                    "name": "Test Account 1",
                },
                {
                    "id": str(account_id_2),
                    "logical_name": "account",
                    "accountid": str(account_id_2),
                    "name": "Test Account 2",
                },
            ],
            "logical_name": "account",
        }
        assert result == EntityCollection(
            entity_logical_name="account",
            entities=[
                Entity(
                    entity_logical_name="account",
                    entity_id=account_id_1,
                    attributes={
                        "accountid": str(account_id_1),
                        "name": "Test Account 1",
                    },
                ),
                Entity(
                    entity_logical_name="account",
                    entity_id=account_id_2,
                    attributes={
                        "accountid": str(account_id_2),
                        "name": "Test Account 2",
                    },
                ),
            ],
        )
