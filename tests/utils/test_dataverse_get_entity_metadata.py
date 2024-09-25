from typing import List
from unittest import mock
import pytest
import requests
from datapyrse.core.models.entity_metadata import (
    EntityMetadata,
    EntityMetadataResponse,
)
from datapyrse.core.utils.dataverse import get_entity_metadata


@pytest.fixture
def service_client():
    service_client = mock.Mock()
    service_client.resource_url = "https://example.crm.dynamics.com"
    service_client.get_access_token.return_value = "mock_access_token"
    service_client.IsReady = True
    return service_client


@mock.patch("datapyrse.core.utils.dataverse.get_entity_metadata")
@mock.patch("requests.get")
def test_get_entity_metadata_success(
    mock_requests_get, mock_get_entity_metadata, service_client
):

    mock_get_entity_metadata.return_value = {
        "value": [
            {
                "LogicalName": "account",
                "AttributeType": "string",
                "SchemaName": "Account",
            },
            {
                "LogicalName": "contact",
                "AttributeType": "integer",
                "SchemaName": "Contact",
            },
        ]
    }

    mock_requests_get.return_value.ok = True
    mock_requests_get.return_value.json.return_value = (
        mock_get_entity_metadata.return_value
    )

    entity_name = "account"
    result = get_entity_metadata(entity_name, service_client)

    # Assertions
    assert len(result) == 2
    assert result[0].logical_name == "account"
    assert result[0].attribute_type == "string"
    assert result[0].schema_name == "Account"
    assert result[1].logical_name == "contact"
    assert result[1].attribute_type == "integer"
    assert result[1].schema_name == "Contact"

    # Verify if the correct endpoint and headers were used
    expected_url = f"https://example.crm.dynamics.com/api/data/v9.2/EntityDefinitions(LogicalName='account')/Attributes?$select=LogicalName,AttributeType,SchemaName"
    requests.get.assert_called_once_with(
        expected_url,
        headers={
            "Authorization": "Bearer mock_access_token",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    for res in result:
        assert isinstance(res, EntityMetadata)


@mock.patch("datapyrse.core.utils.dataverse.get_entity_metadata")
@mock.patch("requests.get")
def test_get_entity_metadata_http_error(
    mock_requests_get, mock_get_entity_metadata, service_client
):
    mock_response = mock.Mock()
    mock_response.ok = False
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Mocked HTTP Error"
    )

    mock_requests_get.return_value = mock_response

    entity_name = "account"

    # Expecting the function to raise an HTTPError
    with pytest.raises(requests.exceptions.HTTPError, match="Mocked HTTP Error"):
        get_entity_metadata(entity_name, service_client)
