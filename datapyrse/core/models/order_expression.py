from dataclasses import dataclass
from enum import Enum


class OrderType(Enum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass
class OrderExpression:
    attribute_name: str
    order_type: OrderType

    def __post_init__(self) -> None:
        if not self.attribute_name:
            raise Exception("Attribute name is required")

        if not self.order_type:
            raise Exception("Order type is required")

        if not isinstance(self.attribute_name, str):
            raise Exception("Attribute name must be a string")

        if not isinstance(self.order_type, OrderType):
            raise Exception("Order type must be an OrderType")
