""" A module for creating order expressions for queries """

from dataclasses import dataclass
from enum import StrEnum


class OrderType(StrEnum):
    """
    Represents an order type in Dataverse or similar systems.

    This class encapsulates the core structure and behavior of an order type
    object in Dataverse, including the available order types.

    Attributes:
        ASC (str): The ascending order type.
        DESC (str): The descending order type.
    """

    ASC = "ASC"
    DESC = "DESC"


@dataclass
class OrderExpression:
    """
    Represents an order expression in Dataverse or similar systems.

    This class encapsulates the core structure and behavior of an order expression
    object in Dataverse, including the attribute name and order type.

    Attributes:
        attribute_name (str): The name of the attribute to order by.
        order_type (OrderType): The order type to use when ordering.

    Raises:
        ValueError: If attribute_name or order_type are not provided.
    """

    attribute_name: str
    order_type: OrderType = OrderType.ASC

    def __post_init__(self) -> None:
        if not self.attribute_name:
            raise ValueError("Attribute name is required")
