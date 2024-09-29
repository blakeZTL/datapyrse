import logging
from typing import List
from unittest import mock
import pytest
import requests
from datapyrse.models.entity_metadata import *
from datapyrse.utils.dataverse import get_metadata


@pytest.fixture
def service_client():
    service_client = mock.Mock()
    service_client.resource_url = "https://example.crm.dynamics.com"
    service_client.get_access_token.return_value = "mock_access_token"
    service_client.IsReady = True
    return service_client


@pytest.fixture
def logger():
    return mock.Mock(logging.Logger)


def test_get_metadata_success(service_client, logger):
    mock_metadata = mock.Mock(OrgMetadata)
    mock_metadata.entities.count = 5
    with (
        mock.patch("requests.get") as mock_get,
        mock.patch(
            "datapyrse.models.entity_metadata.OrgMetadata.from_json",
            return_value=mock_metadata,
        ),
    ):
        mock_response = mock.Mock()
        mock_response.json.return_value = {"value": [{"LogicalName": "account"}]}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        metadata = get_metadata(service_client, logger)

        assert metadata == mock_metadata
        mock_get.assert_called_once_with(
            f"{service_client.resource_url}/api/data/v9.2/EntityDefinitions?$expand=Attributes($select=LogicalName,AttributeType,SchemaName)",
            headers={
                "Authorization": "Bearer mock_access_token",
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0",
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
            },
        )
        logger.debug.assert_called_once_with("Metadata fetched: 5")


def test_get_metadata_no_metadata(service_client, logger):
    with mock.patch("requests.get") as mock_get:
        mock_response = mock.Mock()
        mock_response.json.return_value = {"value": []}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="No metadata found"):
            get_metadata(service_client, logger)

        logger.error.assert_called_once_with("No metadata found")


def test_get_metadata_failed_request(service_client, logger):
    with mock.patch("requests.get") as mock_get:
        mock_response = mock.Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Client Error"
        )
        mock_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError, match="404 Client Error"):
            get_metadata(service_client, logger)

        mock_get.assert_called_once()


def test_get_metadata_no_logger(service_client):
    with (
        mock.patch("requests.get") as mock_get,
        mock.patch(
            "datapyrse.models.entity_metadata.OrgMetadata.from_json",
        ) as mock_metadata,
    ):
        mock_response = mock.Mock()
        mock_response.json.return_value = {"value": [{"LogicalName": "account"}]}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        metadata = get_metadata(service_client)

        assert metadata is not None
        mock_get.assert_called_once()
