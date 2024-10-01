"""A module for Entity Reference Collection"""

from dataclasses import dataclass
from datapyrse._entity_reference import EntityReference


@dataclass
class EntityReferenceCollection:
    """
    Collection of Entity References

    Attributes:
        entity_logical_name (str): Logical Name of the entity
        entity_references (list[EntityReference]): List of Entity References

    Raises:
        ValueError: If Entity Logical Name is not provided
        ValueError: If Entity References are not provided
        ValueError: If Entity Logical Name is not the same for all Entity References
        ValueError: If Entity ID is not provided for all Entity References

    Methods:
        __len__: Get the number of Entity References in the collection
        add: Add an Entity Reference to the collection
        remove: Remove an Entity Reference from the collection
    """

    entity_logical_name: str
    entity_references: list[EntityReference]

    def __post_init__(self):
        if not self.entity_logical_name:
            msg = "Logical Name required for the entity reference collection"
            raise ValueError(msg)
        if not self.entity_references:
            msg = "Entity References required for the entity reference collection"
            raise ValueError(msg)
        if not all(
            i.entity_logical_name == self.entity_logical_name
            for i in self.entity_references
        ):
            msg = "Entity Logical Name must be the same for all Entity References"
            raise ValueError(msg)
        if not all(i.entity_id is not None for i in self.entity_references):
            msg = "All Entity References must have an Entity ID"
            raise ValueError(msg)

    def __len__(self) -> int:
        return len(self.entity_references)

    def add(self, entity_reference: EntityReference) -> None:
        """
        Add an Entity Reference to the collection

        Args:
            entity_reference (EntityReference): Entity Reference to add
        """
        if entity_reference.entity_logical_name != self.entity_logical_name:
            msg = "Entity Logical Name must be the same for all Entity References"
            raise ValueError(msg)
        if entity_reference.entity_id is None:
            msg = "Entity ID required for the Entity Reference"
            raise ValueError(msg)
        self.entity_references.append(entity_reference)

    def remove(self, entity_reference: EntityReference) -> None:
        """
        Remove an Entity Reference from the collection

        Args:
            entity_reference (EntityReference): Entity Reference to remove
        """
        if entity_reference in self.entity_references:
            self.entity_references.remove(entity_reference)
