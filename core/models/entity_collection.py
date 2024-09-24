from dataclasses import dataclass, field
from typing import List, Optional

from core.models.entity import Entity


@dataclass
class EntityCollection:
    """
    Represents a collection of entities in Dataverse or similar systems.
    """

    entity_logical_name: Optional[str] = field(default=None)
    entities: Optional[List[Entity]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.entities:
            self.entities = []
        else:
            if not all(isinstance(entity, Entity) for entity in self.entities):
                raise ValueError("All entities must be instances of Entity class")

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the collection."""
        if not isinstance(entity, Entity):
            raise ValueError("Entity must be an instance of Entity class")
        self.entities.append(entity)

    def remove_entity(self, entity: Entity) -> None:
        """Remove an entity from the collection."""
        if not isinstance(entity, Entity):
            raise ValueError("Entity must be an instance of Entity class")
        if entity.entity_id is None or entity.entity_logical_name is None:
            raise ValueError("Entity must have an ID and a logical name")
        self.entities = [
            e
            for e in self.entities
            if not (
                e.entity_id == entity.entity_id
                and e.entity_logical_name == entity.entity_logical_name
            )
        ]

    def to_dict(self) -> dict:
        """Convert EntityCollection instance to a dictionary."""
        return {
            "logical_name": self.entity_logical_name,
            "entities": [entity.to_dict() for entity in self.entities],
        }
