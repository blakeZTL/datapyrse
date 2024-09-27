import logging
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List

from datapyrse.core.models.entity_reference import EntityReference
from datapyrse.core.models.option_set import OptionSet


@dataclass
class Entity:
    """
    Represents a generic entity in Dataverse.

    This class encapsulates the core structure and behavior of an entity object
    in Dataverse, managing attributes, parsing lookup and option set fields, and
    converting entities to dictionaries for easy serialization. Each entity is
    identified by a logical name and a unique identifier (entity_id).

    Attributes:
        entity_logical_name (str): The logical name of the entity in Dataverse.
        entity_id (uuid.UUID): The unique identifier for the entity instance.
        attributes (Dict[str, Any]): A dictionary of attribute values associated
            with the entity.
        logger (logging.Logger): A logger instance for debugging and information
            logging.
    """

    entity_logical_name: str
    entity_id: uuid.UUID = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    logger: logging.Logger = None

    def __post_init__(self) -> None:
        """
        Initializes the entity after the dataclass fields have been populated.

        This method sets up a logger for the entity if none is provided and ensures
        the attributes are parsed and ready for use.
        """
        if not self.logger:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.WARNING)

        if not self.attributes:
            self.attributes = {}
        else:
            parsed_attributes = self._parse_attributes(list(self.attributes.keys()))
            self.attributes = parsed_attributes

    def __getitem__(self, key: str) -> Any:
        """
        Retrieves the value of an attribute using dictionary-like access.

        Args:
            key (str): The key corresponding to the attribute to retrieve.

        Returns:
            Any: The value of the attribute if it exists, otherwise None.
        """
        return self.attributes.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Sets the value of an attribute using dictionary-like access.

        Args:
            key (str): The key corresponding to the attribute to set.
            value (Any): The value to associate with the specified key.
        """
        self.attributes[key] = value

    def to_dict(self) -> dict:
        """
        Converts the entity instance into a dictionary.

        The resulting dictionary includes the entity's ID, logical name, and
        its attributes.

        Returns:
            dict: A dictionary representation of the entity.
        """
        base_dict = {
            "id": str(self.entity_id),
            "logical_name": self.entity_logical_name,
        }
        return {**base_dict, **self.attributes}

    def _parse_attributes(self, attributes: List[str]) -> Dict[str, Any]:
        """
        Parses the attributes of the entity, converting special fields (like lookups
        and option sets) into appropriate data structures such as EntityReference
        and OptionSet.

        Args:
            attributes (List[str]): A list of attribute keys to parse.

        Returns:
            Dict[str, Any]: A dictionary of parsed attributes ready for internal use.
        """
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
                self.logger.debug(f"{self._parse_attributes.__name__} - Attribute: {attribute_name}")
                self.logger.debug(f"ID: {self.attributes.get(attribute)}")
                self.logger.debug(
                    f"Logical name: {self.attributes.get(f"{attribute}@Microsoft.Dynamics.CRM.lookuplogicalname")}")
                self.logger.debug(
                    f"Name: {self.attributes.get(f"{attribute}@OData.Community.Display.V1.FormattedValue")}")
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
