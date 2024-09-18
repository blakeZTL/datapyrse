from dataclasses import dataclass, field
from typing import Dict, Tuple, Any
import uuid
from utils.validation import validate_guid


@dataclass
class Entity:
    """
    Represents a generic entity in Dataverse or similar systems.
    """

    entity_logical_name: str
    entity_id: uuid.UUID = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.attributes:
            self.attributes = {}

        isValid, validId = validate_guid(self.entity_id)
        if not isValid:
            raise Exception("Entity ID is required and must be a valid GUID")
        else:
            self.entity_id = validId

    def __getitem__(self, key: str) -> Any:
        """Allows getting an attribute using dictionary-like access."""
        return self.attributes.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Allows setting an attribute using dictionary-like access."""
        self.attributes[key] = value

    def to_dict(self) -> dict:
        """Convert Entity instance to a dictionary."""
        base_dict = {
            "id": str(self.entity_id),
            "logical_name": self.entity_logical_name,
        }
        return {**base_dict, **self.attributes}

    def get_attribute_value(self, attribute_name: str) -> Any:
        """Get the value of an attribute by name."""
        return self.attributes.get(attribute_name)

    def try_get_attribute_value(self, attribute_name: str) -> Tuple[bool, Any]:
        """Try to get the value of an attribute by name."""
        if attribute_name in self.attributes:
            return True, self.attributes[attribute_name]
        else:
            return False, None


@dataclass
class EntityReference:
    """
    Represents a reference to another entity in Dataverse or similar systems.
    """

    entity_logical_name: str
    entity_id: uuid.UUID = None
    name: str = None

    def __post_init__(self) -> None:
        isValid, validId = validate_guid(self.entity_id)
        if not isValid:
            raise Exception("Entity ID is required and must be a valid GUID")
        else:
            self.entity_id = validId

    def to_dict(self) -> dict:
        """Convert EntityReference instance to a dictionary."""
        return {
            "id": str(self.entity_id),
            "logical_name": self.entity_logical_name,
        }


if __name__ == "__main__":
    entity = Entity(entity_id="123", entity_logical_name="account")
    entityref = EntityReference(entity_id="456", entity_logical_name="contact")
