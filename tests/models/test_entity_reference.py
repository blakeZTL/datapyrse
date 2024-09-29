from uuid import uuid4
from datapyrse.models.entity_reference import EntityReference


def test_entity_reference_initialization():
    entity_name = "account"
    entity_id = uuid4()
    entity_ref = EntityReference(entity_logical_name=entity_name, entity_id=entity_id)

    assert entity_ref.entity_logical_name == entity_name
    assert entity_ref.entity_id == entity_id


def test_entity_reference_with_name():
    entity_name = "account"
    entity_id = uuid4()
    entity_name_value = "Acme Corp"
    entity_ref = EntityReference(
        entity_logical_name=entity_name, entity_id=entity_id, name=entity_name_value
    )

    assert entity_ref.entity_logical_name == entity_name
    assert entity_ref.entity_id == entity_id
    assert entity_ref.name == entity_name_value


def test_entity_reference_to_dict():
    entity_name = "account"
    entity_id = uuid4()
    entity_name_value = "Acme Corp"
    entity_ref = EntityReference(
        entity_logical_name=entity_name, entity_id=entity_id, name=entity_name_value
    )

    result_dict = entity_ref.to_dict()

    expected_dict = {
        "id": str(entity_id),
        "logical_name": entity_name,
        "name": entity_name_value,
    }

    assert result_dict == expected_dict
