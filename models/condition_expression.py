from dataclasses import dataclass
from typing import Any, List, Union
import uuid
from models.condition_operator import ConditionOperator


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
