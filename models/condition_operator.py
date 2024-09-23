# an static class to define the condition operators
from enum import Enum


class ConditionOperator(Enum):
    # define the condition operators
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    DOES_NOT_CONTAIN = "dpes not contain"
    BEGINS_WITH = "begins with"
    DOES_NOT_BEGIN_WITH = "does not begin with"
    ENDS_WITH = "ends with"
    DOES_NOT_END_WITH = "does not end with"
    IN = "in"
    NOT_IN = "not in"
    NULL = "is null"
    NOT_NULL = "is not null"
    LIKE = "like"
    NOT_LIKE = "not like"

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
            ConditionOperator.CONTAINS,
            ConditionOperator.DOES_NOT_CONTAIN,
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
