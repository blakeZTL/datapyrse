# an static class to define the condition operators
from enum import Enum


class ConditionOperator(Enum):
    # define the condition operators
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

    # get the list of all condition operators
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
