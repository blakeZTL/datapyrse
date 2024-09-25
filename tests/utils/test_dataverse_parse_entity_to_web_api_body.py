import logging
import uuid
import pytest
from unittest import mock
from datapyrse.core.models.entity import Entity, EntityReference, OptionSet
from datapyrse.core.models.entity_metadata import EntityMetadata
from datapyrse.core.utils.dataverse import (
    parse_entity_to_web_api_body,
    get_entity_metadata,
)


@pytest.fixture
def service_client():
    service_client = mock.Mock()
    service_client.IsReady = True
    return service_client


@pytest.fixture
def logger():
    return mock.Mock()


@pytest.fixture
def entity():
    entity = Entity(
        entity_logical_name="account",
        entity_id=uuid.uuid4(),
    )
    entity.attributes = {
        "name": "Sample Account",
        "primarycontactid": EntityReference(
            entity_logical_name="contact", entity_id="12345"
        ),
        "choice": OptionSet(value=1),
    }
    return entity


@mock.patch("datapyrse.core.utils.dataverse.get_entity_metadata")
@mock.patch("datapyrse.core.utils.dataverse.get_entity_collection_name_by_logical_name")
def test_parse_entity_to_web_api_body_success(
    mock_get_entity_collection_name_by_logical_name,
    mock_get_entity_metadata,
    service_client,
    entity,
    logger,
):
    # Mock the entity metadata
    mock_get_entity_metadata.return_value = [
        EntityMetadata(
            logical_name="primarycontactid",
            attribute_type="Lookup",
            schema_name="PrimaryContactId",
        ),
        EntityMetadata(
            logical_name="name",
            attribute_type="String",
            schema_name="Name",
        ),
        EntityMetadata(
            logical_name="choice",
            attribute_type="Picklist",
            schema_name="Choice",
        ),
    ]

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Mock the collection name lookup
    mock_get_entity_collection_name_by_logical_name.return_value = "contacts"

    # Mock entity reference
    entity.attributes["primarycontactid"].entity_logical_name = "contact"
    entity.attributes["primarycontactid"].entity_id = "12345"

    api_body = parse_entity_to_web_api_body(entity, service_client, logger)

    # Assertions for the API body
    print(api_body)
    assert api_body["name"] == "Sample Account"
    assert api_body["PrimaryContactId@odata.bind"] == "/contacts(12345)"
    assert api_body["choice"] == 1

    # Ensure that get_entity_metadata and get_entity_collection_name_by_logical_name were called
    mock_get_entity_metadata.assert_called_once_with("account", service_client)
    mock_get_entity_collection_name_by_logical_name.assert_called_once_with(
        service_client, "contact"
    )


def test_parse_entity_to_web_api_body_service_not_ready(service_client, entity, logger):
    # Simulate the service client not being ready
    service_client.IsReady = False

    with pytest.raises(Exception, match="Service client is not ready"):
        parse_entity_to_web_api_body(entity, service_client, logger)


def test_parse_entity_to_web_api_body_invalid_entity(service_client, logger):
    # Pass an invalid entity (None)
    with pytest.raises(
        Exception, match="Entity of type datapyrse.core.Entity is required"
    ):
        parse_entity_to_web_api_body(None, service_client, logger)


@mock.patch("datapyrse.core.utils.dataverse.get_entity_metadata")
def test_parse_entity_to_web_api_body_metadata_not_found(
    mock_get_entity_metadata, service_client, entity, logger
):
    # Simulate no metadata being found
    mock_get_entity_metadata.return_value = None

    with pytest.raises(Exception, match="Entity metadata not found"):
        parse_entity_to_web_api_body(entity, service_client, logger)


@mock.patch("datapyrse.core.utils.dataverse.get_entity_metadata")
def test_parse_entity_to_web_api_body_attribute_metadata_not_found(
    mock_get_entity_metadata, service_client, entity, logger
):
    # Simulate entity metadata missing for a particular attribute
    mock_get_entity_metadata.return_value = [
        EntityMetadata(logical_name="name", attribute_type="String", schema_name="Name")
    ]

    entity.attributes["primarycontactid"].logical_name = "primarycontactid"

    with pytest.raises(
        Exception, match="Attribute metadata not found for column: primarycontactid"
    ):
        parse_entity_to_web_api_body(entity, service_client, logger)
