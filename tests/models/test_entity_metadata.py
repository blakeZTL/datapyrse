from datapyrse.core.models.entity_metadata import (
    EntityMetadata,
    EntityMetadataResponse,
)


# Test cases for EntityMetadata
def test_entity_metadata_from_json():
    json_data = {
        "LogicalName": "account",
        "AttributeType": "string",
        "SchemaName": "Account",
    }

    entity_metadata = EntityMetadata.from_json(json_data)

    assert entity_metadata.logical_name == "account"
    assert entity_metadata.attribute_type == "string"
    assert entity_metadata.schema_name == "Account"


def test_entity_metadata_default_values():
    entity_metadata = EntityMetadata()

    assert entity_metadata.logical_name is None
    assert entity_metadata.attribute_type is None
    assert entity_metadata.schema_name is None


# Test cases for EntityMetadataResponse
def test_entity_metadata_response_from_json():
    json_data = {
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

    response = EntityMetadataResponse.from_json(json_data)

    assert len(response.value) == 2
    assert response.value[0].logical_name == "account"
    assert response.value[0].attribute_type == "string"
    assert response.value[0].schema_name == "Account"
    assert response.value[1].logical_name == "contact"
    assert response.value[1].attribute_type == "integer"
    assert response.value[1].schema_name == "Contact"


def test_entity_metadata_response_default_values():
    response = EntityMetadataResponse()

    assert response.value is None
