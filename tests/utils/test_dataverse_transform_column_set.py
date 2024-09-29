import contextlib
from unittest import mock
from uuid import uuid4

# Assuming the ServiceClient class and transform_column_set method are in a module called my_module
from datapyrse.utils.dataverse import transform_column_set


# Mock response data for the metadata endpoint
mock_metadata = {
    "value": [
        {"LogicalName": "ownerid", "AttributeType": "Lookup"},
        {"LogicalName": "statuscode", "AttributeType": "Status"},
        {"LogicalName": "name", "AttributeType": "String"},
        {"LogicalName": "createdon", "AttributeType": "DateTime"},
    ]
}


# Helper function to mock the ServiceClient and the response from the metadata request
@contextlib.contextmanager
def mock_service_client(mocked_response):
    service_client = mock.Mock()
    service_client.resource_url = "https://example.crm.dynamics.com"
    service_client.get_access_token.return_value = "mock_access_token"

    with mock.patch("requests.get") as mocked_get:
        mocked_get.return_value = mock.Mock()
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = mocked_response
        yield service_client


# Test when all columns are primitive types (no transformation required)
def test_transform_column_set_with_primitive_columns():
    column_set = ["name"]
    with mock_service_client(mock_metadata) as service_client:
        transformed = transform_column_set(service_client, "account", column_set)

    # Expect columns to remain the same
    assert transformed == ["name"]


# Test when there is a lookup field in the column set
def test_transform_column_set_with_lookup_column():
    column_set = ["ownerid"]
    with mock_service_client(mock_metadata) as service_client:
        transformed = transform_column_set(service_client, "account", column_set)

    expected_transformed = [
        "_ownerid_value",
    ]
    assert transformed == expected_transformed


# Test when there is a state or status field in the column set
def test_transform_column_set_with_status_column():
    column_set = ["statuscode"]
    with mock_service_client(mock_metadata) as service_client:
        transformed = transform_column_set(service_client, "account", column_set)

    expected_transformed = [
        "statuscode",
    ]
    assert transformed == expected_transformed


# Test with a mix of lookup and primitive columns
def test_transform_column_set_with_mixed_columns():
    column_set = ["ownerid", "name", "createdon", "statuscode"]
    with mock_service_client(mock_metadata) as service_client:
        transformed = transform_column_set(service_client, "account", column_set)

    expected_transformed = [
        "_ownerid_value",
        "name",
        "createdon",
        "statuscode",
    ]
    assert transformed == expected_transformed


# Test when no metadata is found for the column
def test_transform_column_set_with_unknown_column_raises_error():
    column_set = ["unknown_column"]
    with mock_service_client(mock_metadata) as service_client:
        try:
            transform_column_set(service_client, "account", column_set)
            assert False, "Expected an exception to be raised"
        except Exception as e:
            print(e)
            assert "Attribute metadata not found for column: unknown_column" in str(e)

    column_set = ["name", "unknown_column"]
    with mock_service_client(mock_metadata) as service_client:
        try:
            transform_column_set(service_client, "account", column_set)
            assert False, "Expected an exception to be raised"
        except Exception as e:
            assert "Attribute metadata not found for column: unknown_column" in str(e)
