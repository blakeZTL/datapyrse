from dataclasses import dataclass, field
import logging
from typing import Dict, Any, List
import uuid
from core.models.entity_reference import EntityReference
from core.models.option_set import OptionSet


@dataclass
class Entity:
    """
    Represents a generic entity in Dataverse.
    """

    entity_logical_name: str
    entity_id: uuid.UUID = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    logger: logging.Logger = None

    def __post_init__(self) -> None:
        if not self.logger:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.WARNING)

        if not self.attributes:
            self.attributes = {}
        else:
            parsed_attributes = self._parse_attributes(list(self.attributes.keys()))
            self.attributes = parsed_attributes        

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

    def _parse_attributes(self, attributes: List[str]) -> Dict[str, Any]:
        """Parse attribute values for internal use."""
        parsed_attributes = {}
        for attribute in attributes:
            """Parse an attribute value."""
            if attribute.startswith("@"):
                continue
            elif attribute.startswith("_") and attribute.endswith("_value"):
                if not self.attributes.get(attribute):
                    self.logger.debug(f"Skipping attribute {attribute}; value is None")
                    continue

                attribute_name: str = attribute[1:-6]
                self.logger.debug(f"Attribute: {attribute_name}")                
                self.logger.debug(f"ID: {self.attributes.get(attribute)}")
                self.logger.debug(f"Logical name: {self.attributes.get(f"{attribute}@Microsoft.Dynamics.CRM.lookuplogicalname")}")
                self.logger.debug(f"Name: {self.attributes.get(f"{attribute}@OData.Community.Display.V1.FormattedValue")}")
                attribute_ref: EntityReference = EntityReference(
                    entity_logical_name=self.attributes.get(
                        f"{attribute}@Microsoft.Dynamics.CRM.lookuplogicalname"
                    ),
                    entity_id=uuid.UUID(self.attributes.get(attribute)),
                    name=self.attributes.get(
                        f"{attribute}@OData.Community.Display.V1.FormattedValue"
                    ),
                )
                parsed_attributes[attribute_name] = attribute_ref
            elif (
                isinstance(self.attributes.get(attribute), int)
                and f"{attribute}@OData.Community.Display.V1.FormattedValue"
                in self.attributes
            ):
                value = self.attributes.get(attribute)
                label = self.attributes.get(
                    f"{attribute}@OData.Community.Display.V1.FormattedValue"
                )
                parsed_attributes[attribute] = OptionSet(label=label, value=value)
            elif f"{self.entity_logical_name}id" == attribute:
                logging.debug(f"Setting entity ID to {self.attributes.get(attribute)}")
                self.entity_id = uuid.UUID(self.attributes.get(attribute))
                parsed_attributes[attribute] = self.attributes.get(attribute)
            else:
                parsed_attributes[attribute] = self.attributes.get(attribute)

        return parsed_attributes
