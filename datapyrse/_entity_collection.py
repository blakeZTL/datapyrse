"""
A module for creating entity collections in Dataverse
"""

from dataclasses import dataclass, field
from typing import Optional, Union

from datapyrse._entity import Entity


@dataclass
class EntityCollection:
    """
    Represents a collection of entities in Dataverse or similar systems.
    """

    entity_logical_name: Optional[str] = field(default=None)
    entities: Optional[list[Entity]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.entities:
            self.entities = []

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the collection."""
        if not entity.entity_id or not entity.entity_logical_name:
            raise ValueError("Entity must have an ID and a logical name")
        if not self.entities:
            self.entities = []
        if entity not in self.entities:
            self.entities.append(entity)

    def remove_entity(self, entity: Entity) -> None:
        """Remove an entity from the collection."""
        if not entity.entity_id or not entity.entity_logical_name:
            raise ValueError("Entity must have an ID and a logical name")
        if self.entities:
            self.entities = [
                e
                for e in self.entities
                if not (
                    e.entity_id == entity.entity_id
                    and e.entity_logical_name == entity.entity_logical_name
                )
            ]

    def to_dict(self) -> dict[str, Union[str, list[dict[str, str]]]]:
        """Convert EntityCollection instance to a dictionary."""
        if not self.entities:
            self.entities = []
        return {
            "logical_name": self.entity_logical_name or "",
            "entities": [entity.to_dict() for entity in self.entities],
        }
