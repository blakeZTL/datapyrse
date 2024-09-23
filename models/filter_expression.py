from dataclasses import dataclass, field
from typing import List
from models.condition_expression import ConditionExpression
from models.filter_expression import FilterExpression


@dataclass
class FilterExpression:
    filter_operator: str  # "AND" or "OR"
    conditions: List[ConditionExpression] = field(default_factory=list)
    filters: List[FilterExpression] = field(default_factory=list)  # Nested filters
