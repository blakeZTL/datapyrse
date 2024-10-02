"""
A module for creating entity collections in Dataverse
"""

from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

from datapyrse._entity import Entity


class _ValidatedEntityList(list[Entity]):
    """
    A list of entities that validates the entities it contains.
    """

    def __init__(
        self,
        parent: "EntityCollection",
        entities: Optional[list[Entity]] = None,
    ) -> None:
        super().__init__(entities or [])
        self.parent = parent
        self._validate_entities(self)

    def _validate_entity(self, item: Entity) -> None:
        if not isinstance(item, Entity):  # type: ignore
            raise ValueError("Value must be an instance of Entity class")
        if not item.entity_id or not item.entity_logical_name:
            raise ValueError("Entity must have an ID and name")
        if item.entity_logical_name != self.parent.entity_logical_name:
            raise ValueError(
                "Entity logical name must match the collection's logical name"
            )

    def _validate_entities(self, items: list[Entity]) -> None:
        if not isinstance(items, list):  # type: ignore
            raise ValueError("Value must be a list")
        for item in items:
            try:
                self._validate_entity(item)
            except ValueError as e:
                raise ValueError(
                    "All items must be a valid instance of the Entity class"
                ) from e

    def append(self, item: Entity) -> None:
        self._validate_entity(item)
        super().append(item)

    def extend(self, items: Iterable[Entity]) -> None:
        self._validate_entities(list(items))
        super().extend(items)


@dataclass
class EntityCollection:
    """
    A collection of entities in Dataverse.

    Args:
        entity_logical_name (str): The logical name of the entity.

    Attributes:
        entity_logical_name (str): The logical name of the entity.
        entities (list[Entity]): The entities in the collection

    Raises:
        ValueError: If the entity logical name is not a string.
        ValueError: If all entities dont have the same logical name as the collection.
        ValueError: If all entities are not an instance of the Entity class.
        ValueError: If an entity does not have an ID or logical name.

    Examples:
        >>> entity1 = Entity(entity_id=uuid4(), entity_logical_name="lead")
        >>> entity2 = Entity(entity_id=uuid4(), entity_logical_name="lead")
        >>> entity_collection = EntityCollection(entity_logical_name="lead")
        >>> entity_collection.entities = [
        ...     entity1,
        ...     entity2,
        ... ]
        >>> entity_collection.entities
        [Entity(entity_id=uuid4(), entity_logical_name="lead"), Entity(entity_id=uuid4(), entity_logical_name="lead")]

    """

    entity_logical_name: str
    _entities: list[Entity] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if not self.entity_logical_name or not isinstance(self.entity_logical_name, str):  # type: ignore
            raise ValueError("Entity logical name must be a string")
        self._entities = _ValidatedEntityList(self)

    @property
    def entities(self) -> list[Entity]:
        """Get the entities in the collection."""
        return self._entities

    @entities.setter
    def entities(self, value: list[Entity]) -> None:  # Delegate validation
        self._entities = _ValidatedEntityList(self, value)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "entity_logical_name" and value and not isinstance(value, str):
            raise ValueError("Entity logical name must be a string")
        super().__setattr__(name, value)

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the collection."""
        if not isinstance(entity, Entity):  # type: ignore
            raise ValueError("Entity must be an instance of Entity class")
        if not entity.entity_id or not entity.entity_logical_name:
            raise ValueError("Entity must have an ID and a logical name")
        if entity not in self._entities:
            self._entities.append(entity)

    def remove_entity(self, entity: Entity) -> None:
        """Remove an entity from the collection."""
        if not isinstance(entity, Entity):  # type: ignore
            raise ValueError("Entity must be an instance of Entity class")
        if not entity.entity_id or not entity.entity_logical_name:
            raise ValueError("Entity must have an ID and a logical name")
        self._entities = [
            e
            for e in self._entities
            if not (
                e.entity_id == entity.entity_id
                and e.entity_logical_name == entity.entity_logical_name
            )
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert EntityCollection instance to a dictionary."""
        return {
            "logical_name": self.entity_logical_name or "",
            "entities": [entity.to_dict() for entity in self._entities],
        }
