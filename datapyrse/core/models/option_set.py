from dataclasses import dataclass, field
from typing import Optional


@dataclass
class OptionSet:
    """
    Represents an option set in Dataverse
    """

    label: Optional[str] = field(default=None)
    value: Optional[int] = field(default=None)

    def to_dict(self) -> dict:
        """Convert OptionSet instance to a dictionary."""
        return {
            "value": self.value,
            "label": self.label,
        }

    def get_option_value(self) -> int | None:
        """Get the value of an option by name."""
        return self.value

    def get_option_label(self) -> str | None:
        """Get the label of an option by value."""
        return self.label
