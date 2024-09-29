import uuid
from dataclasses import is_dataclass
from uuid import uuid4
from datapyrse.models.entity import Entity
from datapyrse.models.entity_reference import EntityReference
from datapyrse.models.option_set import OptionSet


# Test initialization and default attributes
def test_entity_initialization():
    entity_name = "account"
    entity_id = uuid4()
    entity = Entity(entity_logical_name=entity_name, entity_id=entity_id)

    assert entity.entity_logical_name == entity_name
    assert entity.entity_id == entity_id
    assert isinstance(entity.attributes, dict)
    assert entity.attributes == {}


# Test initialization with attributes
def test_entity_initialization_with_attributes():
    entity_name = "contact"
    entity_id = uuid4()
    attributes = {"name": "John Doe", "email": "john@example.com"}

    entity = Entity(
        entity_logical_name=entity_name, entity_id=entity_id, attributes=attributes
    )

    assert entity.entity_logical_name == entity_name
    assert entity.entity_id == entity_id
    assert entity.attributes == attributes
    assert entity["name"] == "John Doe"
    assert entity["email"] == "john@example.com"


# Test setting and getting attributes using dictionary-like access
def test_entity_set_get_attributes():
    entity = Entity(entity_logical_name="lead")
    entity["first_name"] = "Jane"
    entity["last_name"] = "Doe"

    assert entity["first_name"] == "Jane"
    assert entity["last_name"] == "Doe"
    assert entity.attributes == {"first_name": "Jane", "last_name": "Doe"}


# Test the __post_init__ method for default attributes initialization
def test_entity_post_init():
    entity = Entity(entity_logical_name="opportunity")
    assert entity.attributes == {}


# Test the to_dict method
def test_entity_to_dict():
    entity_name = "account"
    entity_id = uuid4()
    attributes = {"name": "Acme Corp", "industry": "Manufacturing"}
    entity = Entity(
        entity_logical_name=entity_name, entity_id=entity_id, attributes=attributes
    )

    result_dict = entity.to_dict()

    expected_dict = {
        "id": str(entity_id),
        "logical_name": entity_name,
        "name": "Acme Corp",
        "industry": "Manufacturing",
    }

    assert result_dict == expected_dict


# Test when no attributes are passed, to_dict method should return logical_name and id only
def test_entity_to_dict_no_attributes():
    entity_name = "account"
    entity_id = uuid4()
    entity = Entity(entity_logical_name=entity_name, entity_id=entity_id)

    result_dict = entity.to_dict()

    expected_dict = {
        "id": str(entity_id),
        "logical_name": entity_name,
    }

    assert result_dict == expected_dict


# Test if entity_id is None
def test_entity_id_none():
    entity = Entity(entity_logical_name="case")
    result_dict = entity.to_dict()

    assert result_dict["id"] == "None"


# Test dataclass behavior
def test_entity_is_dataclass():
    assert is_dataclass(Entity)


# Test cases for the parse_attribute method
def test_parse_skip_attribute():
    entity = Entity(
        entity_logical_name="account", attributes={"@odata.context": "context"}
    )
    assert entity.attributes == {}, "Attribute starting with '@' should be skipped."


def test_parse_entity_reference():
    entity_id = str(uuid.uuid4())
    expected_ref = EntityReference(
        entity_logical_name="systemuser",
        entity_id=uuid.UUID(entity_id),
        name="Owner Name",
    )
    attributes = {
        "_ownerid_value": entity_id,
        "_ownerid_value@OData.Community.Display.V1.FormattedValue": "Owner Name",
        "_ownerid_value@Microsoft.Dynamics.CRM.lookuplogicalname": "systemuser",
    }
    entity = Entity(entity_logical_name="account", attributes=attributes)

    assert entity["ownerid"] == expected_ref


def test_parse_optionset():
    expected_option_set = OptionSet(label="Active", value=1)
    attributes = {
        "statecode": 1,
        "statecode@OData.Community.Display.V1.FormattedValue": "Active",
    }
    entity = Entity(entity_logical_name="account", attributes=attributes)

    assert entity.attributes["statecode"] == expected_option_set


def test_parse_entity_id():
    entity_id = str(uuid.uuid4())
    attributes = {"accountid": entity_id}
    entity = Entity(entity_logical_name="account", attributes=attributes)

    assert entity.entity_id == uuid.UUID(entity_id)


def test_parse_no_match():
    attributes = {"name": "Test Account"}
    entity = Entity(entity_logical_name="account", attributes=attributes)

    # No modifications expected for unmatched attribute
    assert entity["name"] == "Test Account"
