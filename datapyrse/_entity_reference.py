"""
A module for creating entity references in Dataverse
"""

from dataclasses import dataclass
from typing import Optional
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
    entity_id: Optional[UUID] = None
    name: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.entity_logical_name:
            raise ValueError("EntityReference entity_logical_name is required.")

    def to_dict(self) -> dict[str, str]:
        """Convert EntityReference instance to a dictionary."""
        return {
            "id": str(self.entity_id),
            "logical_name": self.entity_logical_name,
            "name": self.name or "",
        }
