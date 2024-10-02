# pylint: disable=missing-module-docstring, missing-function-docstring

from typing import Any
from uuid import uuid4
import pytest
from datapyrse import EntityCollection
from datapyrse import Entity


def test_entity_collection_initialization_no_entities():
    entity_collection = EntityCollection(entity_logical_name="lead")
    assert entity_collection is not None
    assert entity_collection.entity_logical_name == "lead"
    assert entity_collection.entities == []


def test_entity_collection_initialization_no_logical_name():
    with pytest.raises(ValueError, match="Entity logical name must be a string"):
        EntityCollection(entity_logical_name=None)  # type: ignore


def test_entity_collection_initialization_with_entities():
    entity1 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity2 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity_collection.entities = [
        entity1,
        entity2,
    ]

    assert entity_collection is not None
    assert entity_collection.entity_logical_name == "lead"
    assert entity_collection.entities == [entity1, entity2]


def test_entity_collection_initialization_with_non_entity():
    entity1 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity2 = "not an entity"
    with pytest.raises(
        ValueError, match="All items must be a valid instance of the Entity class"
    ):
        ent_col = EntityCollection(entity_logical_name="lead")
        ent_col.entities = [entity1, entity2]  # type: ignore


def test_entity_collection_append_entity():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.entities.append(entity1)
    assert entity_collection.entities == [entity1]

    entity2 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.entities.append(entity2)
    assert entity_collection.entities == [entity1, entity2]


def test_entity_collection_append_entity_with_invalid_item():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.entities.append(entity1)
    entity2 = "not an entity"
    with pytest.raises(ValueError, match="Value must be an instance of Entity class"):
        entity_collection.entities.append(entity2)  # type: ignore
    assert entity_collection.entities == [entity1]


def test_entity_collection_add_entity():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    assert entity_collection.entities == [entity1]

    entity2 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.add_entity(entity2)
    assert entity_collection.entities == [entity1, entity2]


def test_entity_collection_add_entity_not_an_entity():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    entity2 = "not an entity"
    with pytest.raises(ValueError, match="Entity must be an instance of Entity class"):
        entity_collection.add_entity(entity2)  # type: ignore
    assert entity_collection.entities == [entity1]


def test_entity_collection_remove_entity():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    entity2 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.add_entity(entity2)
    entity_collection.remove_entity(entity1)
    assert entity_collection.entities == [entity2]

    entity_collection.remove_entity(entity2)
    assert entity_collection.entities == []


def test_entity_collection_remove_entity_not_in_collection():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    entity2 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.add_entity(entity2)
    entity3 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.remove_entity(entity3)
    assert entity_collection.entities == [entity1, entity2]

    entity4 = Entity(entity_id=entity1.entity_id, entity_logical_name="soemthingelse")
    entity_collection.remove_entity(entity4)
    assert entity_collection.entities == [entity1, entity2]

    entity5 = Entity(entity_id=uuid4(), entity_logical_name=entity1.entity_logical_name)
    entity_collection.remove_entity(entity5)
    assert entity_collection.entities == [entity1, entity2]


def test_entity_collection_remove_entity_no_id_or_no_logical_name():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    entity2 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.add_entity(entity2)
    entity3 = Entity(entity_id=None, entity_logical_name="lead")
    with pytest.raises(ValueError, match="Entity must have an ID and a logical name"):
        entity_collection.remove_entity(entity3)
    assert entity_collection.entities == [entity1, entity2]

    entity4 = Entity(entity_id=uuid4(), entity_logical_name=None)  # type: ignore
    with pytest.raises(ValueError, match="Entity must have an ID and a logical name"):
        entity_collection.remove_entity(entity4)
    assert entity_collection.entities == [entity1, entity2]


def test_entity_collection_remove_entity_not_an_entity():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    entity2 = Entity(entity_id=uuid4(), entity_logical_name="lead")
    entity_collection.add_entity(entity2)
    entity3 = "not an entity"
    with pytest.raises(ValueError, match="Entity must be an instance of Entity class"):
        entity_collection.remove_entity(entity3)  # type: ignore
    assert entity_collection.entities == [entity1, entity2]


def test_entity_collection_to_dict():
    entity1_id = uuid4()
    entity2_id = uuid4()
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id=entity1_id, entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    entity2 = Entity(entity_id=entity2_id, entity_logical_name="lead")
    entity_collection.add_entity(entity2)

    result_dict = entity_collection.to_dict()

    expected_dict: dict[str, Any] = {
        "logical_name": "lead",
        "entities": [
            {
                "id": str(entity1_id),
                "logical_name": "lead",
            },
            {"id": str(entity2_id), "logical_name": "lead"},
        ],
    }

    assert result_dict == expected_dict


def test_entity_collection_to_dict_with_not_entities():
    entity_collection = EntityCollection(entity_logical_name="lead")
    result_dict = entity_collection.to_dict()

    expected_dict: dict[str, Any] = {
        "logical_name": "lead",
        "entities": [],
    }

    assert result_dict == expected_dict
