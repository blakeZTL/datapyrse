import logging
import uuid
import pytest
from unittest import mock
from datapyrse.models.entity import Entity, EntityReference, OptionSet
from datapyrse.models.entity_metadata import (
    AttributeMetadata,
    EntityMetadata,
    OrgMetadata,
)
from datapyrse.services.service_client import ServiceClient
from datapyrse.utils.dataverse import (
    parse_entity_to_web_api_body,
    get_entity_metadata,
)


@pytest.fixture
def service_client():
    service_client = mock.Mock(spec=ServiceClient)
    service_client.IsReady = True
    service_client.metadata = OrgMetadata(
        entities=[
            EntityMetadata(
                logical_name="account",
                logical_collection_name="accounts",
                attributes=[
                    AttributeMetadata(
                        logical_name="primarycontactid",
                        attribute_type="Lookup",
                        schema_name="PrimaryContactId",
                    ),
                    AttributeMetadata(
                        logical_name="name",
                        attribute_type="String",
                        schema_name="Name",
                    ),
                    AttributeMetadata(
                        logical_name="choice",
                        attribute_type="Picklist",
                        schema_name="Choice",
                    ),
                ],
            ),
            EntityMetadata(
                logical_name="contact",
                logical_collection_name="contacts",
                attributes=[
                    AttributeMetadata(
                        logical_name="firstname",
                        attribute_type="String",
                        schema_name="FirstName",
                    ),
                ],
            ),
        ]
    )

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


def test_parse_entity_to_web_api_body_success(
    service_client,
    entity,
    logger,
):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Mock entity reference
    entity.attributes["primarycontactid"].entity_logical_name = "contact"
    entity.attributes["primarycontactid"].entity_id = "12345"

    api_body = parse_entity_to_web_api_body(entity, service_client, logger)

    # Assertions for the API body
    print(api_body)
    assert api_body["name"] == "Sample Account"
    assert api_body["PrimaryContactId@odata.bind"] == "/contacts(12345)"
    assert api_body["choice"] == 1


def test_parse_entity_to_web_api_body_service_not_ready(service_client, entity, logger):
    # Simulate the service client not being ready
    service_client.IsReady = False

    with pytest.raises(Exception, match="Service client is not ready"):
        parse_entity_to_web_api_body(entity, service_client, logger)


def test_parse_entity_to_web_api_body_invalid_entity(service_client, logger):
    # Pass an invalid entity (None)
    with pytest.raises(Exception, match="Entity of type datapyrse.Entity is required"):
        parse_entity_to_web_api_body(None, service_client, logger)


@mock.patch("datapyrse.utils.dataverse.get_entity_metadata")
def test_parse_entity_to_web_api_body_metadata_not_found(
    mock_get_entity_metadata, service_client, entity, logger
):
    # Simulate no metadata being found
    mock_get_entity_metadata.return_value = None

    with pytest.raises(Exception, match="Entity metadata not found"):
        parse_entity_to_web_api_body(entity, service_client, logger)


def test_parse_entity_to_web_api_body_attribute_metadata_not_found(
    service_client, entity, logger
):
    service_client.metadata.entities = [
        EntityMetadata(
            logical_name="account",
            logical_collection_name="accounts",
            attributes=[
                AttributeMetadata(
                    logical_name=None,
                    attribute_type="Lookup",
                    schema_name="PrimaryContactId",
                ),
                AttributeMetadata(
                    logical_name="name",
                    attribute_type="String",
                    schema_name="Name",
                ),
                AttributeMetadata(
                    logical_name="choice",
                    attribute_type="Picklist",
                    schema_name="Choice",
                ),
            ],
        ),
    ]

    entity.attributes["primarycontactid"].logical_name = "primarycontactid"

    with pytest.raises(
        Exception, match="Attribute metadata not found for column: primarycontactid"
    ):
        parse_entity_to_web_api_body(entity, service_client, logger)
