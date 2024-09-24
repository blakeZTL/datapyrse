from dataclasses import dataclass, field
from typing import List
from datapyrse.core.models.condition_expression import ConditionExpression
from enum import Enum


class FilterOperator(Enum):
    AND = "AND"
    OR = "OR"


@dataclass
class FilterExpression:
    filter_operator: FilterOperator = field(default=FilterOperator.AND)
    conditions: List[ConditionExpression] = field(default_factory=list)
    filters: List["FilterExpression"] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.conditions:
            self.conditions = []

        if not self.filters:
            self.filters = []

        if not isinstance(self.filter_operator, FilterOperator):
            raise Exception("Filter operator must be a FilterOperator")

        if self.conditions:
            if not isinstance(self.conditions, list):
                raise Exception("Conditions must be a list of ConditionExpressions")

        if self.filters:
            if not isinstance(self.filters, list):
                raise Exception("Filters must be a list of FilterExpressions")
