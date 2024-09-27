from dataclasses import dataclass
from uuid import UUID


@dataclass
class EntityReference:
    """
    Represents a reference to another entity in Dataverse or similar systems.
    """

    entity_logical_name: str
    entity_id: UUID | None = None
    name: str | None = None

    def __post_init__(self) -> None:
        if not self.entity_logical_name:
            raise ValueError("EntityReference entity_logical_name is required.")

    def to_dict(self) -> dict:
        """Convert EntityReference instance to a dictionary."""
        return {
            "id": str(self.entity_id),
            "logical_name": self.entity_logical_name,
            "name": self.name,
        }
