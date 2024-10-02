"""
A module for creating entity references in Dataverse
"""

from dataclasses import dataclass
from typing import Any, Optional, Union
from uuid import UUID


@dataclass
class EntityReference:
    """
    Represents a reference to an entity in Dataverse or similar systems.

    This class encapsulates the core structure and behavior of an entity reference
    object in Dataverse, including the logical name, unique identifier, and name
    of the entity.

    Attributes:
        entity_logical_name (str): The logical name of the entity in Dataverse.
        entity_id (uuid.UUID): The unique identifier for the entity instance.
        name (str): The name of the entity instance.

    Raises:
        ValueError: If entity_logical_name is not provided.
    """

    entity_logical_name: str
    entity_id: Optional[Union[UUID, str]] = None
    name: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.entity_logical_name or not isinstance(self.entity_logical_name, str):  # type: ignore
            raise ValueError(
                "EntityReference entity_logical_name of type string is required."
            )
        if self.entity_id and not isinstance(self.entity_id, UUID):
            try:
                self.entity_id = UUID(self.entity_id)
            except ValueError as exc:
                raise ValueError(
                    "EntityReference entity_id of type UUID or compatible string is required."
                ) from exc

        if self.name and not isinstance(self.name, str):  # type: ignore
            raise ValueError("EntityReference name of type string is required.")

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "entity_id" and value:
            if not isinstance(value, (UUID, str)):
                raise ValueError(
                    "EntityReference entity_id of type UUID or compatible string is required."
                )
            if isinstance(value, str):
                try:
                    value = UUID(value)
                except ValueError as exc:
                    raise ValueError(
                        "EntityReference entity_id of type UUID or compatible string is required."
                    ) from exc
        super().__setattr__(name, value)

    def to_dict(self) -> dict[str, str]:
        """Convert EntityReference instance to a dictionary."""
        return {
            "id": str(self.entity_id) if self.entity_id else "",
            "logical_name": self.entity_logical_name,
            "name": self.name or "",
        }
