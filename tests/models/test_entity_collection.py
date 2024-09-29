from datapyrse.models.entity_collection import EntityCollection
from datapyrse.models.entity import Entity


def test_entity_collection_empty_initialization():
    entity_collection = EntityCollection()
    assert entity_collection is not None
    assert entity_collection.entity_logical_name == None
    assert entity_collection.entities == []


def test_entity_collection_initialization_no_entities():
    entity_collection = EntityCollection(entity_logical_name="lead")
    assert entity_collection is not None
    assert entity_collection.entity_logical_name == "lead"
    assert entity_collection.entities == []


def test_entity_collection_initialization_with_entities():
    entity1 = Entity(entity_id="123", entity_logical_name="lead")
    entity2 = Entity(entity_id="456", entity_logical_name="lead")
    entity_collection = EntityCollection(
        entity_logical_name="lead", entities=[entity1, entity2]
    )
    assert entity_collection is not None
    assert entity_collection.entity_logical_name == "lead"
    assert entity_collection.entities == [entity1, entity2]


def test_entity_collection_initialization_with_non_entity():
    entity1 = Entity(entity_id="123", entity_logical_name="lead")
    entity2 = "not an entity"
    try:
        EntityCollection(entity_logical_name="lead", entities=[entity1, entity2])
        assert False
    except ValueError as e:
        assert str(e) == "All entities must be instances of Entity class"


def test_entity_collection_add_entity():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id="123", entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    assert entity_collection.entities == [entity1]

    entity2 = Entity(entity_id="456", entity_logical_name="lead")
    entity_collection.add_entity(entity2)
    assert entity_collection.entities == [entity1, entity2]


def test_entity_collection_add_entity_not_an_entity():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id="123", entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    entity2 = "not an entity"
    try:
        entity_collection.add_entity(entity2)
        assert False
    except ValueError as e:
        assert str(e) == "Entity must be an instance of Entity class"
    assert entity_collection.entities == [entity1]


def test_entity_collection_remove_entity():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id="123", entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    entity2 = Entity(entity_id="456", entity_logical_name="lead")
    entity_collection.add_entity(entity2)
    entity_collection.remove_entity(entity1)
    assert entity_collection.entities == [entity2]

    entity_collection.remove_entity(entity2)
    assert entity_collection.entities == []


def test_entity_collection_remove_entity_not_in_collection():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id="123", entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    entity2 = Entity(entity_id="456", entity_logical_name="lead")
    entity_collection.add_entity(entity2)
    entity3 = Entity(entity_id="789", entity_logical_name="lead")
    entity_collection.remove_entity(entity3)
    assert entity_collection.entities == [entity1, entity2]

    entity4 = Entity(entity_id=entity1.entity_id, entity_logical_name="soemthingelse")
    entity_collection.remove_entity(entity4)
    assert entity_collection.entities == [entity1, entity2]

    entity5 = Entity(entity_id="789", entity_logical_name=entity1.entity_logical_name)
    entity_collection.remove_entity(entity5)
    assert entity_collection.entities == [entity1, entity2]


def test_entity_collection_remove_entity_no_id_or_no_logical_name():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id="123", entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    entity2 = Entity(entity_id="456", entity_logical_name="lead")
    entity_collection.add_entity(entity2)
    entity3 = Entity(entity_id=None, entity_logical_name="lead")
    try:
        entity_collection.remove_entity(entity3)
        assert False
    except ValueError as e:
        assert str(e) == "Entity must have an ID and a logical name"
    assert entity_collection.entities == [entity1, entity2]

    entity4 = Entity(entity_id="789", entity_logical_name=None)
    try:
        entity_collection.remove_entity(entity4)
        assert False
    except ValueError as e:
        assert str(e) == "Entity must have an ID and a logical name"
    assert entity_collection.entities == [entity1, entity2]


def test_entity_collection_remove_entity_not_an_entity():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id="123", entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    entity2 = Entity(entity_id="456", entity_logical_name="lead")
    entity_collection.add_entity(entity2)
    entity3 = "not an entity"
    try:
        entity_collection.remove_entity(entity3)
        assert False
    except ValueError as e:
        assert str(e) == "Entity must be an instance of Entity class"
    assert entity_collection.entities == [entity1, entity2]


def test_entity_collection_to_dict():
    entity_collection = EntityCollection(entity_logical_name="lead")
    entity1 = Entity(entity_id="123", entity_logical_name="lead")
    entity_collection.add_entity(entity1)
    entity2 = Entity(entity_id="456", entity_logical_name="lead")
    entity_collection.add_entity(entity2)

    result_dict = entity_collection.to_dict()

    expected_dict = {
        "logical_name": "lead",
        "entities": [
            {
                "id": "123",
                "logical_name": "lead",
            },
            {"id": "456", "logical_name": "lead"},
        ],
    }

    assert result_dict == expected_dict
