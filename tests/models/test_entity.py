import unittest
import uuid
from models.entity import Entity, EntityReference
from unittest.mock import patch


class TestEntity(unittest.TestCase):

    @patch("models.entity.validate_guid")
    def test_entity_initialization(self, mock_validate_guid):
        mock_validate_guid.return_value = (True, uuid.uuid4())
        entity = Entity(entity_logical_name="account", entity_id=uuid.uuid4())
        self.assertEqual(entity.entity_logical_name, "account")
        self.assertTrue(mock_validate_guid.called)

    @patch("models.entity.validate_guid")
    def test_entity_invalid_guid(self, mock_validate_guid):
        mock_validate_guid.return_value = (False, None)
        with self.assertRaises(Exception) as context:
            Entity(entity_logical_name="account", entity_id=uuid.uuid4())
        self.assertTrue(
            "Entity ID is required and must be a valid GUID" in str(context.exception)
        )

    @patch("models.entity.validate_guid")
    def test_entity_get_set_item(self, mock_validate_guid):
        mock_validate_guid.return_value = (True, uuid.uuid4())
        entity = Entity(entity_logical_name="account", entity_id=uuid.uuid4())
        entity["name"] = "Test Account"
        self.assertEqual(entity["name"], "Test Account")

    @patch("models.entity.validate_guid")
    def test_entity_to_dict(self, mock_validate_guid):
        guid = uuid.uuid4()
        mock_validate_guid.return_value = (True, guid)
        entity_id = guid
        entity = Entity(entity_logical_name="account", entity_id=entity_id)
        entity["name"] = "Test Account"
        entity_dict = entity.to_dict()
        self.assertEqual(entity_dict["id"], str(entity_id))
        self.assertEqual(entity_dict["logical_name"], "account")
        self.assertEqual(entity_dict["name"], "Test Account")

    @patch("models.entity.validate_guid")
    def test_entity_get_attribute_value(self, mock_validate_guid):
        mock_validate_guid.return_value = (True, uuid.uuid4())
        entity = Entity(entity_logical_name="account", entity_id=uuid.uuid4())
        entity["name"] = "Test Account"
        self.assertEqual(entity.get_attribute_value("name"), "Test Account")

    @patch("models.entity.validate_guid")
    def test_entity_try_get_attribute_value(self, mock_validate_guid):
        mock_validate_guid.return_value = (True, uuid.uuid4())
        entity = Entity(entity_logical_name="account", entity_id=uuid.uuid4())
        entity["name"] = "Test Account"
        found, value = entity.try_get_attribute_value("name")
        self.assertTrue(found)
        self.assertEqual(value, "Test Account")
        found, value = entity.try_get_attribute_value("nonexistent")
        self.assertFalse(found)
        self.assertIsNone(value)


class TestEntityReference(unittest.TestCase):

    @patch("models.entity.validate_guid")
    def test_entity_reference_initialization(self, mock_validate_guid):
        guid = uuid.uuid4()
        mock_validate_guid.return_value = (True, guid)
        entity_ref = EntityReference(entity_id=guid, entity_logical_name="contact")
        self.assertEqual(entity_ref.entity_logical_name, "contact")
        self.assertTrue(mock_validate_guid.called)

    @patch("models.entity.validate_guid")
    def test_entity_reference_to_dict(self, mock_validate_guid):
        guid = uuid.uuid4()
        mock_validate_guid.return_value = (True, guid)
        entity_ref = EntityReference(entity_id=guid, entity_logical_name="contact")
        entity_ref_dict = entity_ref.to_dict()
        self.assertEqual(entity_ref_dict["id"], str(guid))
        self.assertEqual(entity_ref_dict["logical_name"], "contact")

    @patch("models.entity.validate_guid")
    def test_entity_reference_name(self, mock_validate_guid):
        guid = uuid.uuid4()
        mock_validate_guid.return_value = (True, guid)
        entity_ref = EntityReference(
            entity_id=guid, entity_logical_name="contact", name="John Doe"
        )
        self.assertEqual(entity_ref.name, "John Doe")
        self.assertEqual(entity_ref.entity_logical_name, "contact")
        self.assertEqual(entity_ref.entity_id, guid)


if __name__ == "__main__":
    unittest.main()
