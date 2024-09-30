"""A module for creating option sets in Dataverse."""

from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class OptionSet:
    """
    Represents an option set in Dataverse or similar systems.

    This class encapsulates the core structure and behavior of an option set
    object in Dataverse, including the available options.

    Attributes:
        label (str): The label of the option.
        value (int): The value of the option.
    """

    label: Optional[str] = field(default=None)
    value: Optional[int] = field(default=None)

    def to_dict(self) -> dict[str, Optional[Union[str, int]]]:
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
