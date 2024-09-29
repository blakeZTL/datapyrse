import pytest
from unittest import mock
import uuid
from requests.exceptions import HTTPError
from datapyrse.models.entity_metadata import *
from datapyrse.models.entity_reference import EntityReference
from datapyrse.services.retrieve import retrieve
from datapyrse.models.entity import Entity


@pytest.fixture
def service_client():
    service_client = mock.Mock()
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
                    AttributeMetadata(
                        logical_name="ownerid",
                        attribute_type="lookup",
                        schema_name="Owner",
                    ),
                ],
            ),
            EntityMetadata(
                logical_name="systemuser",
                logical_collection_name="systemusers",
                attributes=[
                    AttributeMetadata(
                        logical_name="fullname",
                        attribute_type="string",
                        schema_name="FullName",
                    ),
                ],
            ),
        ],
    )
    return service_client


# Test when service_client is not ready
def test_retrieve_service_client_not_ready():
    service_client = mock.Mock()
    service_client.IsReady = False

    with pytest.raises(Exception, match="Service client is not ready"):
        retrieve(service_client, "account", uuid.uuid4(), ["name"])


# Test when entity_name is missing
def test_retrieve_entity_name_missing(service_client):
    with pytest.raises(Exception, match="Entity plural name is required"):
        retrieve(service_client, "", uuid.uuid4(), ["name"])


# Test when entity_id is missing
def test_retrieve_entity_id_missing(service_client):
    with pytest.raises(Exception, match="Entity ID is required"):
        retrieve(service_client, "account", None, ["name"])


# Test when column_set is missing
def test_retrieve_column_set_missing(service_client):

    with pytest.raises(Exception, match="Column set is required"):
        retrieve(service_client, "account", uuid.uuid4(), [])


def test_retrieve_entity_collection_not_found(service_client):
    service_client.metadata = OrgMetadata(
        entities=[
            EntityMetadata(
                logical_name="account",
                logical_collection_name=None,
                attributes=[
                    AttributeMetadata(
                        logical_name="name",
                        attribute_type="string",
                        schema_name="Name",
                    ),
                    AttributeMetadata(
                        logical_name="ownerid",
                        attribute_type="lookup",
                        schema_name="Owner",
                    ),
                ],
            ),
        ],
    )
    with pytest.raises(Exception, match="Entity collection name not found"):
        retrieve(service_client, "account", uuid.uuid4(), ["name"])


@mock.patch("datapyrse.services.retrieve.transform_column_set")
def test_retrieve_transform_column_set_failure(
    mock_transform_column_set,
    service_client,
):
    mock_transform_column_set.return_value = None

    with pytest.raises(Exception, match="Failed to transform column set"):
        retrieve(service_client, "account", uuid.uuid4(), ["name"])


@mock.patch("datapyrse.services.retrieve.transform_column_set")
@mock.patch("requests.get")
def test_retrieve_success(
    mock_requests_get,
    mock_transform_column_set,
    service_client,
):
    mock_transform_column_set.return_value = ["name", "_ownerid_value"]

    owner_guid = uuid.uuid4()

    # Mock the response from the GET request
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "Test Account",
        "_ownerid_value": str(owner_guid),
        "_ownerid_value@Microsoft.Dynamics.CRM.lookuplogicalname": "systemuser",
        "_ownerid_value@OData.Community.Display.V1.FormattedValue": "Blake Bradford",
    }
    mock_requests_get.return_value = mock_response

    # Call the retrieve method
    entity_id = uuid.uuid4()
    entity = retrieve(service_client, "account", entity_id, ["name", "ownerid"])

    # Assertions
    assert isinstance(entity, Entity)
    assert entity.entity_id == entity_id
    assert entity.entity_logical_name == "account"
    assert entity["name"] == "Test Account"
    assert entity["ownerid"] == EntityReference(
        entity_logical_name="systemuser",
        entity_id=owner_guid,
        name="Blake Bradford",
    )

    # Check if the request was made correctly
    expected_url = f"https://example.crm.dynamics.com/api/data/v9.2/accounts({entity_id})?$select=name,_ownerid_value"
    mock_requests_get.assert_called_once_with(
        expected_url,
        headers={
            "Authorization": "Bearer mock_access_token",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Prefer": "odata.include-annotations=*",
        },
    )


@mock.patch("datapyrse.services.retrieve.transform_column_set")
@mock.patch("requests.get")
def test_retrieve_http_error(
    mock_requests_get,
    mock_transform_column_set,
    service_client,
):
    mock_transform_column_set.return_value = ["name", "_ownerid_value"]

    # Mock the GET request to raise an HTTP error
    mock_requests_get.side_effect = HTTPError("HTTP Error occurred")

    # Call the retrieve method and expect an HTTP error
    with pytest.raises(HTTPError, match="HTTP Error occurred"):
        retrieve(service_client, "account", uuid.uuid4(), ["name", "_ownerid_value"])
