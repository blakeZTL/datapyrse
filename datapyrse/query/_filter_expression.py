"""
A module for creating filter expressions for queries
"""

from dataclasses import dataclass, field
from typing import List
from enum import StrEnum


from datapyrse.query._condition_expression import ConditionExpression


class FilterOperator(StrEnum):
    """
    Represents a filter operator in Dataverse or similar systems.

    This class encapsulates the core structure and behavior of a filter operator
    object in Dataverse, including the available filter operators.

    Attributes:
        AND (str): The AND operator.
        OR (str): The OR operator.
    """

    AND = "AND"
    OR = "OR"


@dataclass
class FilterExpression:
    """
    Represents a filter expression in Dataverse or similar systems.

    This class encapsulates the core structure and behavior of a filter expression
    object in Dataverse, including the filter operator, conditions, and filters.

    Attributes:
        filter_operator (FilterOperator): The operator to use when combining conditions.
        conditions (List[ConditionExpression]): A list of conditions to apply to the filter.
        filters (List[FilterExpression]): A list of filters to apply to the filter.

    Raises:
        ValueError: If conditions or filters are not provided.
    """

    filter_operator: FilterOperator = field(default=FilterOperator.AND)
    conditions: List[ConditionExpression] = field(default_factory=list)
    filters: List["FilterExpression"] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.conditions:
            self.conditions = []

        if not self.filters:
            self.filters = []
