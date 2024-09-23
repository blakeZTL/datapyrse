from dataclasses import dataclass
from typing import Any, List


@dataclass
class ConditionExpression:
    attribute_name: str
    operator: str  # Example: "Equal", "NotEqual", "Like", etc.
    values: List[Any]  # List of values to compare against
