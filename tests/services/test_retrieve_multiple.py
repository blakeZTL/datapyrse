from unittest import mock
import uuid
import pytest
from core.models.column_set import ColumnSet
from core.models.condition_expression import ConditionOperator
from core.models.entity import Entity
from core.models.entity_collection import EntityCollection
from core.models.query_expression import QueryExpression
from core.services.retrieve_multiple import retrieve_multiple


@pytest.fixture
def service_client():
    service_client = mock.Mock()
    service_client.IsReady = True
    service_client.get_access_token.return_value = "mock_access_token"
    service_client.resource_url = "https://example.crm.dynamics.com"
    return service_client


@pytest.fixture
def query_expression():
    return QueryExpression(entity_name="account", column_set=ColumnSet(True))


def test_retrieve_multiple_service_client_not_ready(service_client, query_expression):
    service_client.IsReady = False

    with pytest.raises(Exception, match="Service client is not ready"):
        retrieve_multiple(service_client, query_expression)


def test_retrieve_multiple_query_expression_missing(service_client, query_expression):
    with pytest.raises(Exception, match="Query is required"):
        retrieve_multiple(service_client, None)


def test_retrieve_multiple_query_expression_invalid(service_client):
    with pytest.raises(Exception, match="Query must be a QueryExpression"):
        retrieve_multiple(service_client, "query_expression")


@mock.patch(
    "core.services.retrieve_multiple.get_entity_collection_name_by_logical_name"
)
def test_retrieve_multiple_entity_collection_name_not_found(
    mock_get_entity_collection_name_by_logical_name, service_client, query_expression
):
    mock_get_entity_collection_name_by_logical_name.return_value = None

    with pytest.raises(Exception, match="Entity collection name not found"):
        retrieve_multiple(service_client, query_expression)


@mock.patch(
    "core.services.retrieve_multiple.get_entity_collection_name_by_logical_name"
)
@mock.patch.object(QueryExpression, "to_fetchxml")
def test_retrieve_multiple_fetchxml_not_found(
    mock_to_fetchxml,
    mock_get_entity_collection_name_by_logical_name,
    service_client,
    query_expression,
):
    mock_to_fetchxml.return_value = None
    mock_get_entity_collection_name_by_logical_name.return_value = "accounts"

    with pytest.raises(Exception, match="Failed to parse query expression"):
        retrieve_multiple(service_client, query_expression)


@mock.patch(
    "core.services.retrieve_multiple.get_entity_collection_name_by_logical_name"
)
def test_retrieve_multiple_no_entities_found(
    mock_get_entity_collection_name_by_logical_name, service_client, query_expression
):
    mock_get_entity_collection_name_by_logical_name.return_value = "accounts"

    with mock.patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"value": []}

        result = retrieve_multiple(service_client, query_expression)

        assert result.entities == []


@mock.patch(
    "core.services.retrieve_multiple.get_entity_collection_name_by_logical_name"
)
def test_retieve_multiple_entities_found(
    mock_get_entity_collection_name_by_logical_name, service_client, query_expression
):
    mock_get_entity_collection_name_by_logical_name.return_value = "accounts"

    account1 = Entity(
        entity_id=uuid.uuid4(),
        entity_logical_name="account",
        attributes={"name": "Account 1"},
    )
    account2 = Entity(
        entity_id=uuid.uuid4(),
        entity_logical_name="account",
        attributes={"name": "Account 2"},
    )
    with mock.patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "value": [
                {"accountid": str(account1.entity_id), "name": "Account 1"},
                {"accountid": str(account2.entity_id), "name": "Account 2"},
            ]
        }

        result = retrieve_multiple(service_client, query_expression)

        assert len(result.entities) == 2
        assert result.entities[0].attributes == {
            "accountid": str(account1.entity_id),
            "name": "Account 1",
        }
        assert result.entities[1].attributes == {
            "accountid": str(account2.entity_id),
            "name": "Account 2",
        }
