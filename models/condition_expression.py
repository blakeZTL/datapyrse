from dataclasses import dataclass
from typing import Any, List, Union
import uuid
from enum import Enum


class ConditionOperator(Enum):
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

    @staticmethod
    def get_all():
        return [
            ConditionOperator.EQUAL,
            ConditionOperator.NOT_EQUAL,
            ConditionOperator.GREATER,
            ConditionOperator.GREATER_EQUAL,
            ConditionOperator.LESS,
            ConditionOperator.LESS_EQUAL,
            ConditionOperator.BEGINS_WITH,
            ConditionOperator.DOES_NOT_BEGIN_WITH,
            ConditionOperator.ENDS_WITH,
            ConditionOperator.DOES_NOT_END_WITH,
            ConditionOperator.IN,
            ConditionOperator.NOT_IN,
            ConditionOperator.NULL,
            ConditionOperator.NOT_NULL,
            ConditionOperator.LIKE,
            ConditionOperator.NOT_LIKE,
        ]


@dataclass
class ConditionExpression:
    attribute_name: str
    operator: ConditionOperator
    values: Union[List[Any], bool, int, float, str, uuid.UUID, None]

    def __post_init__(self) -> None:

        if not self.operator:
            raise Exception("Operator is required")

        if not self.attribute_name:
            raise Exception("Attribute name is required")

        if not isinstance(self.attribute_name, str):
            raise Exception("Attribute name must be a string")

        if not isinstance(self.operator, ConditionOperator):
            raise Exception("Operator must be a ConditionOperator")

        if self.values:
            if not isinstance(self.values, (list, bool, int, float, str, uuid.UUID)):
                raise Exception(
                    "Values must be a list, boolean, integer, float, string, or UUID"
                )

        if not self.values:
            self.values = None
        else:
            if not isinstance(self.values, list):
                self.values = [self.values]
            else:
                self.values = self.values

        if (
            self.operator == ConditionOperator.NULL
            or self.operator == ConditionOperator.NOT_NULL
        ):
            self.values = None

        if (
            self.operator == ConditionOperator.IN
            or self.operator == ConditionOperator.NOT_IN
        ):
            if not self.values:
                raise Exception("Values are required for IN/NOT IN operators")
            if not isinstance(self.values, list):
                raise Exception("Values must be a list for IN/NOT IN operators")
            if len(self.values) == 0:
                raise Exception(
                    "Values must contain at least one value for IN/NOT IN operators"
                )
            if len(self.values) > 500:
                raise Exception(
                    "Values must contain less than 500 values for IN/NOT IN operators"
                )
