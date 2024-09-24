from dataclasses import dataclass
import uuid


@dataclass
class EntityReference:
    """
    Represents a reference to another entity in Dataverse or similar systems.
    """

    entity_logical_name: str
    entity_id: uuid.UUID = None
    name: str = None

    def __post_init__(self) -> None: ...

    def to_dict(self) -> dict:
        """Convert EntityReference instance to a dictionary."""
        return {
            "id": str(self.entity_id),
            "logical_name": self.entity_logical_name,
            "name": self.name,
        }
