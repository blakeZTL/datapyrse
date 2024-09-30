import uuid
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

class ConditionOperator(StrEnum):
    EQUAL = 'eq'
    NOT_EQUAL = 'ne'
    GREATER = 'gt'
    GREATER_EQUAL = 'ge'
    LESS = 'lt'
    LESS_EQUAL = 'le'
    BEGINS_WITH = 'begins-with'
    DOES_NOT_BEGIN_WITH = 'not-begin-with'
    ENDS_WITH = 'ends-with'
    DOES_NOT_END_WITH = 'not-ends-with'
    IN = 'in'
    NOT_IN = 'not-in'
    NULL = 'null'
    NOT_NULL = 'not-null'
    LIKE = 'like'
    NOT_LIKE = 'not-like'

@dataclass
class ConditionExpression:
    attribute_name: str
    operator: ConditionOperator
    value: list[Any] | bool | int | float | str | uuid.UUID | None
    def __post_init__(self) -> None: ...
    def __init__(self, attribute_name, operator, value) -> None: ...
