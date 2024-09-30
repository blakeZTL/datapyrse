from dataclasses import dataclass
from enum import StrEnum

class OrderType(StrEnum):
    ASC = 'ASC'
    DESC = 'DESC'

@dataclass
class OrderExpression:
    attribute_name: str
    order_type: OrderType = ...
    def __post_init__(self) -> None: ...
    def __init__(self, attribute_name, order_type=...) -> None: ...
