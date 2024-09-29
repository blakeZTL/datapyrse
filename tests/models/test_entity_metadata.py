from datapyrse.models.entity_metadata import *


def test_attribute_metadata_from_json():
    json_data = {
        "LogicalName": "accountname",
        "AttributeType": "String",
        "SchemaName": "AccountName",
    }

    attribute_metadata = AttributeMetadata.from_json(json_data)

    assert attribute_metadata.logical_name == "accountname"
    assert attribute_metadata.attribute_type == "String"
    assert attribute_metadata.schema_name == "AccountName"


def test_localized_label_from_json():
    json_data = {
        "HasChanged": True,
        "IsManaged": False,
        "Label": "Account",
        "LanguageCode": 1033,
        "MetadataId": "12345678-1234-1234-1234-123456789012",
    }

    localized_label = LocalizedLabel.from_json(json_data)

    assert localized_label.has_changed is True
    assert localized_label.is_managed is False
    assert localized_label.label == "Account"
    assert localized_label.language_code == 1033
    assert localized_label.metadata_id == "12345678-1234-1234-1234-123456789012"


def test_entity_metadata_from_json():
    json_data = {
        "Attributes": [
            {
                "LogicalName": "accountname",
                "AttributeType": "String",
                "SchemaName": "AccountName",
            },
            {
                "LogicalName": "accountid",
                "AttributeType": "Guid",
                "SchemaName": "AccountId",
            },
        ],
        "LogicalCollectionName": "accounts",
        "LogicalName": "account",
        "SchemaName": "Account",
        "PrimaryIdAttribute": "accountid",
        "PrimaryNameAttribute": "accountname",
    }

    entity_metadata = EntityMetadata.from_json(json_data)

    assert entity_metadata.logical_collection_name == "accounts"
    assert entity_metadata.logical_name == "account"
    assert entity_metadata.schema_name == "Account"
    assert entity_metadata.primary_id_attribute == "accountid"
    assert entity_metadata.primary_name_attribute == "accountname"
    assert len(entity_metadata.attributes) == 2
    assert entity_metadata.attributes[0].logical_name == "accountname"
    assert entity_metadata.attributes[1].attribute_type == "Guid"


def test_org_metadata_from_json():
    json_data = {
        "value": [
            {
                "Attributes": [
                    {
                        "LogicalName": "accountname",
                        "AttributeType": "String",
                        "SchemaName": "AccountName",
                    }
                ],
                "LogicalCollectionName": "accounts",
                "LogicalName": "account",
                "SchemaName": "Account",
                "PrimaryIdAttribute": "accountid",
                "PrimaryNameAttribute": "accountname",
            },
            {
                "Attributes": [
                    {
                        "LogicalName": "contactname",
                        "AttributeType": "String",
                        "SchemaName": "ContactName",
                    }
                ],
                "LogicalCollectionName": "contacts",
                "LogicalName": "contact",
                "SchemaName": "Contact",
                "PrimaryIdAttribute": "contactid",
                "PrimaryNameAttribute": "contactname",
            },
        ]
    }

    org_metadata = OrgMetadata.from_json(json_data)

    assert len(org_metadata.entities) == 2
    assert org_metadata.entities[0].logical_name == "account"
    assert org_metadata.entities[1].logical_name == "contact"
    assert org_metadata.entities[0].attributes[0].logical_name == "accountname"
    assert org_metadata.entities[1].attributes[0].schema_name == "ContactName"
