# pylint: disable=missing-function-docstring, missing-module-docstring

from uuid import UUID, uuid4

import pytest
from datapyrse import EntityReference


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


def test_entity_reference_no_entity_logical_name_or_not_a_string():
    with pytest.raises(
        ValueError,
        match="EntityReference entity_logical_name of type string is required.",
    ):
        EntityReference(entity_logical_name=None)  # type: ignore

    with pytest.raises(
        ValueError,
        match="EntityReference entity_logical_name of type string is required.",
    ):
        EntityReference(entity_logical_name=123)  # type: ignore


def test_entity_reference_with_valid_string_as_uuid():
    entity_name = "account"
    entity_id = "123e4567-e89b-12d3-a456-426614174000"
    entity_ref = EntityReference(entity_logical_name=entity_name, entity_id=entity_id)

    assert entity_ref.entity_logical_name == entity_name
    assert entity_ref.entity_id == UUID(entity_id)


def test_entity_reference_with_invalid_string_as_uuid():
    entity_name = "account"
    entity_id = "not a uuid"
    with pytest.raises(
        ValueError,
        match="EntityReference entity_id of type UUID or compatible string is required.",
    ):
        EntityReference(entity_logical_name=entity_name, entity_id=entity_id)


def test_entity_reference_no_name_or_not_a_string():
    entity_name = "account"
    entity_id = uuid4()
    with pytest.raises(
        ValueError, match="EntityReference name of type string is required."
    ):
        EntityReference(entity_logical_name=entity_name, entity_id=entity_id, name=123)  # type: ignore

    ent_ref = EntityReference(entity_logical_name=entity_name, entity_id=entity_id)
    assert ent_ref.name is None


def test_entity_reference_set_entity_id():
    entity_name = "account"
    entity_id = uuid4()
    entity_ref = EntityReference(entity_logical_name=entity_name)

    entity_ref.entity_id = entity_id

    assert entity_ref.entity_id == entity_id


def test_entity_reference_set_entity_id_with_valid_string():
    entity_name = "account"
    entity_id = "123e4567-e89b-12d3-a456-426614174000"
    entity_ref = EntityReference(entity_logical_name=entity_name)

    entity_ref.entity_id = entity_id

    assert entity_ref.entity_id == UUID(entity_id)


def test_entity_reference_set_entity_id_with_invalid_string():
    entity_name = "account"
    entity_id = "not a uuid"
    entity_ref = EntityReference(entity_logical_name=entity_name)

    with pytest.raises(
        ValueError,
        match="EntityReference entity_id of type UUID or compatible string is required.",
    ):
        entity_ref.entity_id = entity_id


def test_entity_reference_set_entity_id_with_not_uuid_or_string():
    entity_name = "account"
    entity_id = 123
    entity_ref = EntityReference(entity_logical_name=entity_name)

    with pytest.raises(
        ValueError,
        match="EntityReference entity_id of type UUID or compatible string is required.",
    ):
        entity_ref.entity_id = entity_id  # type: ignore


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

    entity_ref = EntityReference(entity_logical_name=entity_name, entity_id=entity_id)

    result_dict = entity_ref.to_dict()

    expected_dict = {
        "id": str(entity_id),
        "logical_name": entity_name,
        "name": "",
    }

    assert result_dict == expected_dict

    entity_ref = EntityReference(entity_logical_name=entity_name)

    result_dict = entity_ref.to_dict()

    expected_dict = {
        "id": "",
        "logical_name": entity_name,
        "name": "",
    }

    assert result_dict == expected_dict
