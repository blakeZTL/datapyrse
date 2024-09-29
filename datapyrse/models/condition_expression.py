"""
A module for creating condition expressions for filtering data in a query
"""

from dataclasses import dataclass
from typing import Any, List, Union
import uuid
from enum import StrEnum


class ConditionOperator(StrEnum):
    """
    Represents the operators that can be used in a condition expression.

    Operators:
        - EQUAL: Equal to
        - NOT_EQUAL: Not equal to
        - GREATER: Greater than
        - GREATER_EQUAL: Greater than or equal to
        - LESS: Less than
        - LESS_EQUAL: Less than or equal to
        - BEGINS_WITH: Begins with
        - DOES_NOT_BEGIN_WITH: Does not begin with
        - ENDS_WITH: Ends with
        - DOES_NOT_END_WITH: Does not end with
        - IN: In list
        - NOT_IN: Not in list
        - NULL: Is null
        - NOT_NULL: Is not null
        - LIKE: Like
        - NOT_LIKE: Not like

    """

    EQUAL = "eq"
    NOT_EQUAL = "ne"
    GREATER = "gt"
    GREATER_EQUAL = "ge"
    LESS = "lt"
    LESS_EQUAL = "le"
    BEGINS_WITH = "begins-with"
    DOES_NOT_BEGIN_WITH = "not-begin-with"
    ENDS_WITH = "ends-with"
    DOES_NOT_END_WITH = "not-ends-with"
    IN = "in"
    NOT_IN = "not-in"
    NULL = "null"
    NOT_NULL = "not-null"
    LIKE = "like"
    NOT_LIKE = "not-like"


@dataclass
class ConditionExpression:
    """
    Represents a condition expression for filtering data in a query.

    This class encapsulates the structure and behavior of a condition expression
    in a query, including the attribute name, operator, and value(s) to filter by.

    Attributes:
        attribute_name (str): The name of the attribute to filter by.
        operator (ConditionOperator): The operator to use for the condition.
        value (Union[List[Any], bool, int, float, str, uuid.UUID, None]): The value(s)
            to filter by.

    Raises:
        ValueError: If the operator or attribute name is not provided, or if the value
            is not of a valid type
    """

    attribute_name: str
    operator: ConditionOperator
    value: Union[List[Any], bool, int, float, str, uuid.UUID, None]

    def __post_init__(self) -> None:

        if not self.operator:
            raise ValueError("Operator is required")

        if not self.attribute_name:
            raise ValueError("Attribute name is required")

        if self.value:
            if not isinstance(self.value, (list, bool, int, float, str, uuid.UUID)):
                raise ValueError(
                    "Value must be a list, boolean, integer, float, string, or UUID"
                )

        if not self.value:
            self.value = None
        else:
            if not isinstance(self.value, list):
                self.value = [self.value]
            else:
                self.value = self.value

        if self.operator in [ConditionOperator.NULL, ConditionOperator.NOT_NULL]:
            self.value = None

        elif self.operator in [ConditionOperator.IN, ConditionOperator.NOT_IN]:
            if not self.value:
                raise ValueError("Value are required for IN/NOT IN operators")
            if len(self.value) == 0:
                raise ValueError(
                    "Value must contain at least one value for IN/NOT IN operators"
                )
            if len(self.value) > 500:
                raise ValueError(
                    "Value must contain less than 500 value for IN/NOT IN operators"
                )
